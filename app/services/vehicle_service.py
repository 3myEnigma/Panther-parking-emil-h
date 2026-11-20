"""Business rules for vehicles. No Flask request objects and no SQL here."""
import re

from ..repositories import vehicle_repository


class VehicleError(Exception):
    """Raised with a user-facing message when a rule is broken."""


def register_vehicle(user_id, plate, make, model, color):
    plate = (plate or "").strip().upper()
    make = (make or "").strip()
    model = (model or "").strip()
    color = (color or "").strip()

    if not re.fullmatch(r"[A-Z0-9]{2,8}", plate):
        raise VehicleError("Plate must be 2–8 letters or digits.")
    if vehicle_repository.find_by_plate(plate):
        raise VehicleError("This plate is already registered.")

    return vehicle_repository.create(user_id, plate, make, model, color)


def add_vehicle(user_id, plate, make, model, color):
    return register_vehicle(user_id, plate, make, model, color)


def list_vehicles(user_id):
    return vehicle_repository.list_by_user_id(user_id)
