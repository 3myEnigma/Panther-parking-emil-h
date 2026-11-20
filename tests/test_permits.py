"""Story #3: As a driver, I want to apply for a parking permit."""
from app.repositories import permit_repository, vehicle_repository


def register_vehicle(client, app, plate="ABC123"):
    client.post(
        "/vehicles/",
        data={"plate": plate, "make": "Toyota", "model": "Camry", "color": "Blue"},
    )
    with app.app_context():
        return vehicle_repository.find_by_plate(plate)


def test_ac1_valid_application_is_pending(client, register_and_login, app):
    register_and_login()
    vehicle = register_vehicle(client, app)

    resp = client.post(
        "/permits/",
        data={"vehicle_id": vehicle["id"], "zone": "Student"},
        follow_redirects=True,
    )

    assert resp.status_code == 200
    assert b"Permit application submitted." in resp.data
    assert b"pending" in resp.data
    with app.app_context():
        permits = permit_repository.list_by_user_id(vehicle["user_id"])
        assert len(permits) == 1
        assert permits[0]["status"] == "pending"
        assert permits[0]["zone"] == "Student"


def test_ac2_unowned_or_missing_vehicle_rejected(client, register_and_login, app):
    register_and_login("owner@pvamu.edu")
    owned_vehicle = register_vehicle(client, app, "OWNER123")

    client.get("/auth/logout")
    register_and_login("other@pvamu.edu")
    resp = client.post(
        "/permits/",
        data={"vehicle_id": owned_vehicle["id"], "zone": "Student"},
        follow_redirects=True,
    )
    assert b"You do not own this vehicle." in resp.data

    resp = client.post(
        "/permits/",
        data={"vehicle_id": "", "zone": "Student"},
        follow_redirects=True,
    )
    assert b"A vehicle is required." in resp.data
    with app.app_context():
        assert permit_repository.list_by_user_id(owned_vehicle["user_id"]) == []


def test_ac3_missing_or_invalid_zone_rejected(client, register_and_login, app):
    register_and_login()
    vehicle = register_vehicle(client, app)

    resp = client.post(
        "/permits/",
        data={"vehicle_id": vehicle["id"], "zone": ""},
        follow_redirects=True,
    )
    assert b"Zone is required." in resp.data

    resp = client.post(
        "/permits/",
        data={"vehicle_id": vehicle["id"], "zone": "NotAZone"},
        follow_redirects=True,
    )
    assert b"Invalid parking zone." in resp.data

    with app.app_context():
        assert permit_repository.list_by_user_id(vehicle["user_id"]) == []


def test_ac4_logged_out_redirected(client):
    resp = client.get("/permits/")
    assert resp.status_code == 302
    assert "/auth/login" in resp.headers["Location"]
