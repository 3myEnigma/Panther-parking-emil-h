from ..db import get_db


def find_by_email(email):
    row = get_db().execute("SELECT * FROM user WHERE email = ?", (email,)).fetchone()
    return dict(row) if row else None


def find_by_id(user_id):
    row = get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
    return dict(row) if row else None


def create(email, password_hash, role="driver"):
    db = get_db()
    cur = db.execute(
        "INSERT INTO user (email, password_hash, role) VALUES (?, ?, ?)",
        (email, password_hash, role),
    )
    db.commit()
    return cur.lastrowid


def set_admin(user_id, is_admin=True):
    db = get_db()
    value = 1 if is_admin else 0
    db.execute(
        "UPDATE user SET is_admin = ?, role = ? WHERE id = ?",
        (value, "admin" if value else "driver", user_id),
    )
    db.commit()
