"""Story #4: As an administrator, I want to approve or reject permit applications."""
from app.repositories import permit_repository, user_repository, vehicle_repository


def make_admin(app, email):
    with app.app_context():
        user = user_repository.find_by_email(email)
        user_repository.set_admin(user["id"], True)


def create_pending_permit(app, driver_email="driver@pvamu.edu", plate="DRIVER123"):
    with app.app_context():
        driver = user_repository.find_by_email(driver_email)
        if driver is None:
            return None
        vehicle = vehicle_repository.find_by_plate(plate)
        if vehicle is None:
            vehicle_id = vehicle_repository.create(driver["id"], plate, "Honda", "Civic", "Red")
        else:
            vehicle_id = vehicle["id"]
        permit_id = permit_repository.create(driver["id"], vehicle_id, "Student")
        return permit_id


def test_ac1_admin_views_pending_permits(client, app, register_and_login):
    register_and_login("driver@pvamu.edu")
    with app.app_context():
        driver = user_repository.find_by_email("driver@pvamu.edu")
        vehicle_id = vehicle_repository.create(
            driver["id"], "DRIVER123", "Honda", "Civic", "Red"
        )
        permit_repository.create(driver["id"], vehicle_id, "Student")
    client.get("/auth/logout")

    register_and_login("admin@pvamu.edu")
    make_admin(app, "admin@pvamu.edu")
    client.get("/auth/logout")
    register_and_login("admin@pvamu.edu")

    resp = client.get("/permits/approve")
    assert resp.status_code == 200
    assert b"driver@pvamu.edu" in resp.data
    assert b"DRIVER123" in resp.data
    assert b"Student" in resp.data


def test_ac2_approve_sets_status_and_removes_pending(client, app, register_and_login):
    register_and_login("driver@pvamu.edu")
    permit_id = create_pending_permit(app)
    client.get("/auth/logout")

    register_and_login("admin@pvamu.edu")
    make_admin(app, "admin@pvamu.edu")
    client.get("/auth/logout")
    register_and_login("admin@pvamu.edu")

    resp = client.post(f"/permits/{permit_id}/approve", follow_redirects=True)
    assert resp.status_code == 200
    with app.app_context():
        assert permit_repository.find_by_id(permit_id)["status"] == "approved"
        assert all(p["id"] != permit_id for p in permit_repository.list_pending_with_details())


def test_ac3_reject_sets_status_and_removes_pending(client, app, register_and_login):
    register_and_login("driver@pvamu.edu")
    permit_id = create_pending_permit(app)
    client.get("/auth/logout")

    register_and_login("admin@pvamu.edu")
    make_admin(app, "admin@pvamu.edu")
    client.get("/auth/logout")
    register_and_login("admin@pvamu.edu")

    resp = client.post(f"/permits/{permit_id}/reject", follow_redirects=True)
    assert resp.status_code == 200
    with app.app_context():
        assert permit_repository.find_by_id(permit_id)["status"] == "rejected"
        assert all(p["id"] != permit_id for p in permit_repository.list_pending_with_details())


def test_ac4_non_admin_cannot_view_or_change(client, app, register_and_login):
    register_and_login("driver@pvamu.edu")
    with app.app_context():
        vehicle_id = vehicle_repository.create(1, "PROTECTED123", "Ford", "Fusion", "Blue")
        permit_id = permit_repository.create(1, vehicle_id, "Student")

    resp = client.get("/permits/approve")
    assert resp.status_code == 302
    assert "/lots/" in resp.headers["Location"]

    resp = client.post(f"/permits/{permit_id}/approve")
    assert resp.status_code == 302
    resp = client.post(f"/permits/{permit_id}/reject")
    assert resp.status_code == 302
    with app.app_context():
        assert permit_repository.find_by_id(permit_id)["status"] == "pending"
