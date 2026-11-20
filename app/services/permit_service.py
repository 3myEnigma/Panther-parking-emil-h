"""Business rules for parking permits."""
from ..repositories import lot_repository, permit_repository, vehicle_repository


class PermitError(Exception):
    """Raised with a user-facing message when a permit rule is broken."""


def apply_for_permit(user_id, vehicle_id, zone):
    if vehicle_id is None or not str(vehicle_id).strip():
        raise PermitError("A vehicle is required.")

    zone = (zone or "").strip()
    if not zone:
        raise PermitError("Zone is required.")

    try:
        vehicle_id = int(vehicle_id)
    except (TypeError, ValueError):
        raise PermitError("You do not own this vehicle.")

    vehicle = vehicle_repository.find_by_id(vehicle_id)
    if vehicle is None or vehicle["user_id"] != user_id:
        raise PermitError("You do not own this vehicle.")

    valid_zones = {lot["zone"] for lot in lot_repository.list_all()}
    if zone not in valid_zones:
        raise PermitError("Invalid parking zone.")

    permit_id = permit_repository.create(user_id, vehicle_id, zone)
    return permit_repository.list_by_user_id(user_id)[0] if permit_id else None


def list_permits(user_id):
    return permit_repository.list_by_user_id(user_id)
