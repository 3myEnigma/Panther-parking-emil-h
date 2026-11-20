from ..db import get_db


def find_by_plate(plate):
    row = get_db().execute(
        "SELECT * FROM vehicle WHERE UPPER(plate) = UPPER(?)",
        (plate,),
    ).fetchone()
    return dict(row) if row else None


def find_by_id(vehicle_id):
    row = get_db().execute(
        "SELECT * FROM vehicle WHERE id = ?",
        (vehicle_id,),
    ).fetchone()
    return dict(row) if row else None


def list_by_user_id(user_id):
    rows = get_db().execute(
        "SELECT * FROM vehicle WHERE user_id = ? ORDER BY id",
        (user_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def create(user_id, plate, make, model, color):
    db = get_db()
    cur = db.execute(
        "INSERT INTO vehicle (user_id, plate, make, model, color) VALUES (?, ?, ?, ?, ?)",
        (user_id, plate, make, model, color),
    )
    db.commit()
    return cur.lastrowid
