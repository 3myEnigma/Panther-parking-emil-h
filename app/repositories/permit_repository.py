from ..db import get_db


def create(user_id, vehicle_id, zone):
    db = get_db()
    cur = db.execute(
        "INSERT INTO permit (user_id, vehicle_id, zone) VALUES (?, ?, ?)",
        (user_id, vehicle_id, zone),
    )
    db.commit()
    return cur.lastrowid


def list_by_user_id(user_id):
    rows = get_db().execute(
        """
        SELECT permit.*, vehicle.plate
        FROM permit
        JOIN vehicle ON vehicle.id = permit.vehicle_id
        WHERE permit.user_id = ?
        ORDER BY permit.id DESC
        """,
        (user_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def find_by_id(permit_id):
    row = get_db().execute(
        "SELECT * FROM permit WHERE id = ?",
        (permit_id,),
    ).fetchone()
    return dict(row) if row else None


def list_by_user(user_id):
    return list_by_user_id(user_id)
