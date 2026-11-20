import sqlite3

import click
from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("make-admin")
@click.argument("email")
def make_admin_command(email):
    """Promote an existing account to administrator."""
    db = get_db()
    cur = db.execute(
        "UPDATE user SET is_admin = 1, role = 'admin' WHERE email = ?",
        ((email or "").strip().lower(),),
    )
    db.commit()
    if cur.rowcount == 0:
        raise click.ClickException(f"No account found for {email}.")
    click.echo(f"Promoted {email} to admin.")


@click.command("init-db")
def init_db_command():
    """Drop and recreate all tables, then load sample lots."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(make_admin_command)
