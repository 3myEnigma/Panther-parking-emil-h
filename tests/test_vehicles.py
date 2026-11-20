"""Story #2: As a driver, I want to register a vehicle."""
from app.repositories import vehicle_repository


def test_ac1_valid_vehicle_added(client, register_and_login, app):
    register_and_login()
    resp = client.post(
        "/vehicles/",
        data={"plate": "ABC123", "make": "Toyota", "model": "Camry", "color": "Blue"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"ABC123" in resp.data
    with app.app_context():
        assert vehicle_repository.find_by_plate("ABC123") is not None


def test_ac2_invalid_plate_rejected(client, register_and_login, app):
    register_and_login()
    resp = client.post(
        "/vehicles/",
        data={"plate": "A-1", "make": "Honda", "model": "Civic", "color": "Red"},
        follow_redirects=True,
    )
    assert b"2" in resp.data
    assert b"8" in resp.data
    with app.app_context():
        assert vehicle_repository.find_by_plate("A-1") is None


def test_ac3_duplicate_plate_rejected(client, register_and_login):
    register_and_login()
    data = {"plate": "DUP123", "make": "Ford", "model": "Fusion", "color": "Black"}
    client.post("/vehicles/", data=data)
    resp = client.post("/vehicles/", data=data, follow_redirects=True)
    assert b"This plate is already registered." in resp.data


def test_ac4_logged_out_redirected(client):
    resp = client.get("/vehicles/")
    assert resp.status_code == 302
    assert "/auth/login" in resp.headers["Location"]
