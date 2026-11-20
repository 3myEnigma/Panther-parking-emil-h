"""Story #6: As an administrator, I want to create and edit parking lots."""
from app.repositories import lot_repository, user_repository


def make_admin(app, email="admin@pvamu.edu"):
    with app.app_context():
        user = user_repository.find_by_email(email)
        if user:
            user_repository.set_admin(user["id"], True)


def test_ac1_admin_creates_lot(client, app, register_and_login):
    register_and_login("admin@pvamu.edu")
    make_admin(app, "admin@pvamu.edu")
    client.get("/auth/logout")
    register_and_login("admin@pvamu.edu")

    resp = client.post(
        "/lots/manage",
        data={"name": "Test Lot", "zone": "Student", "capacity": "50"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Lot created" in resp.data
    with app.app_context():
        assert lot_repository.find_by_name("Test Lot") is not None


def test_ac2_admin_edits_lot(client, app, register_and_login):
    register_and_login("admin@pvamu.edu")
    make_admin(app, "admin@pvamu.edu")
    client.get("/auth/logout")
    register_and_login("admin@pvamu.edu")

    with app.app_context():
        lot_id = lot_repository.create("Edit Lot", "Student", 40)
    resp = client.post(
        f"/lots/{lot_id}/edit",
        data={"name": "Edited Lot", "zone": "Faculty", "capacity": "75"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Lot updated" in resp.data
    with app.app_context():
        lot = lot_repository.find_by_id(lot_id)
        assert lot["name"] == "Edited Lot"
        assert lot["zone"] == "Faculty"
        assert lot["capacity"] == 75


def test_ac3_invalid_lot_rejected(client, app, register_and_login):
    register_and_login("admin@pvamu.edu")
    make_admin(app, "admin@pvamu.edu")
    client.get("/auth/logout")
    register_and_login("admin@pvamu.edu")

    resp = client.post(
        "/lots/manage",
        data={"name": "", "zone": "", "capacity": "0"},
        follow_redirects=True,
    )
    assert b"Lot name is required" in resp.data

    resp = client.post(
        "/lots/manage",
        data={"name": "No Zone", "zone": "", "capacity": "10"},
        follow_redirects=True,
    )
    assert b"Lot zone is required" in resp.data

    resp = client.post(
        "/lots/manage",
        data={"name": "Bad Capacity", "zone": "Student", "capacity": "0"},
        follow_redirects=True,
    )
    assert b"Capacity must be at least 1" in resp.data
    with app.app_context():
        assert lot_repository.find_by_name("Bad Capacity") is None


def test_ac4_non_admin_and_logged_out_cannot_modify(client, app, register_and_login):
    register_and_login("driver@pvamu.edu")
    resp = client.get("/lots/manage")
    assert resp.status_code == 302
    assert "/lots/" in resp.headers["Location"]

    with app.app_context():
        lot_id = lot_repository.create("Protected Lot", "Student", 20)
    resp = client.post(
        f"/lots/{lot_id}/edit",
        data={"name": "Hacked", "zone": "Student", "capacity": "99"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    with app.app_context():
        assert lot_repository.find_by_id(lot_id)["name"] == "Protected Lot"

    client.get("/auth/logout")
    resp = client.get("/lots/manage")
    assert resp.status_code == 302
    assert "/auth/login" in resp.headers["Location"]
