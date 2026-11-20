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


def is_admin(user):
    return bool(user and (user.get("is_admin") == 1 or user.get("role") == "admin"))


def require_admin(user):
    if not is_admin(user):
        raise PermitError("Admin access required.")


def list_pending_permits(user):
    require_admin(user)
    return permit_repository.list_pending_with_details()


def list_pending(user):
    return list_pending_permits(user)


def update_permit_status(user, permit_id, status):
    require_admin(user)
    if status not in ("approved", "rejected"):
        raise PermitError("Invalid permit status.")
    if permit_repository.find_by_id(permit_id) is None:
        raise PermitError("Permit not found.")
    permit_repository.update_status(permit_id, status)
    return True


def approve_permit(user, permit_id):
    return update_permit_status(user, permit_id, "approved")


def reject_permit(user, permit_id):
    return update_permit_status(user, permit_id, "rejected")
