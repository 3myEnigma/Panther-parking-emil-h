"""Business rules for parking lots."""
from ..repositories import lot_repository

FILLING_THRESHOLD = 0.75  # 75% occupied or more = "filling"


class LotError(Exception):
    """Raised with a user-facing message when a lot rule is broken."""


def is_admin(user):
    return bool(user and (user.get("is_admin") == 1 or user.get("role") == "admin"))


def require_admin(user):
    if not is_admin(user):
        raise LotError("Admin access required.")


def validate_lot(name, zone, capacity):
    name = (name or "").strip()
    zone = (zone or "").strip()
    try:
        capacity = int(capacity)
    except (TypeError, ValueError):
        raise LotError("Capacity must be at least 1.")

    if not name:
        raise LotError("Lot name is required.")
    if not zone:
        raise LotError("Lot zone is required.")
    if capacity < 1:
        raise LotError("Capacity must be at least 1.")
    return name, zone, capacity


def create_lot(user, name, zone, capacity):
    require_admin(user)
    name, zone, capacity = validate_lot(name, zone, capacity)
    if lot_repository.find_by_name(name):
        raise LotError("A lot with that name already exists.")
    return lot_repository.create(name, zone, capacity)


def update_lot(user, lot_id, name, zone, capacity):
    require_admin(user)
    name, zone, capacity = validate_lot(name, zone, capacity)
    existing = lot_repository.find_by_id(lot_id)
    if existing is None:
        raise LotError("Lot not found.")
    duplicate = lot_repository.find_by_name(name)
    if duplicate and duplicate["id"] != int(lot_id):
        raise LotError("A lot with that name already exists.")
    lot_repository.update(lot_id, name, zone, capacity)
    return existing


def status_for(capacity, occupied):
    """Return 'open', 'filling' or 'full' for a lot.

    Story #5 acceptance criteria live in tests/test_lots.py.
    """
    if occupied >= capacity:
        return "full"
    if occupied / capacity >= FILLING_THRESHOLD:
        return "filling"
    return "open"


def lots_with_status():
    lots = lot_repository.list_all()
    for lot in lots:
        lot["status"] = status_for(lot["capacity"], lot["occupied"])
        lot["available"] = max(lot["capacity"] - lot["occupied"], 0)
    return lots


def find_lot(lot_id):
    return lot_repository.find_by_id(lot_id)
