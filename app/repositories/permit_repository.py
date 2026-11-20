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


def list_pending_with_details():
    rows = get_db().execute(
        """
        SELECT permit.id, permit.user_id, permit.vehicle_id, permit.zone,
               permit.status, user.email AS driver_email,
               vehicle.plate, vehicle.make, vehicle.model, vehicle.color
        FROM permit
        JOIN user ON user.id = permit.user_id
        JOIN vehicle ON vehicle.id = permit.vehicle_id
        WHERE permit.status = 'pending'
        ORDER BY permit.id
        """
    ).fetchall()
    return [dict(row) for row in rows]


def list_pending():
    return list_pending_with_details()


def update_status(permit_id, status):
    db = get_db()
    cur = db.execute(
        "UPDATE permit SET status = ? WHERE id = ?",
        (status, permit_id),
    )
    db.commit()
    return cur.rowcount


def set_status(permit_id, status):
    return update_status(permit_id, status)


def list_all_pending():
    return list_pending_with_details()
