from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from ..routes.auth import login_required
from ..services import lot_service
from ..services.lot_service import LotError

bp = Blueprint("lots", __name__, url_prefix="/lots")


@bp.route("/")
def index():
    return render_template("lots.html", lots=lot_service.lots_with_status())


def _admin_required():
    if g.user is None:
        return redirect(url_for("auth.login"))
    if not lot_service.is_admin(g.user):
        flash("Admin access required.")
        return redirect(url_for("lots.index"))
    return None


@bp.route("/manage", methods=("GET", "POST"))
@login_required
def manage():
    denied = _admin_required()
    if denied:
        return denied

    if request.method == "POST":
        lot_id = request.form.get("lot_id") or request.form.get("id")
        try:
            if lot_id:
                lot_service.update_lot(
                    g.user, lot_id, request.form.get("name"),
                    request.form.get("zone"), request.form.get("capacity"),
                )
                flash("Lot updated.")
            else:
                lot_service.create_lot(
                    g.user, request.form.get("name"),
                    request.form.get("zone"), request.form.get("capacity"),
                )
                flash("Lot created.")
            return redirect(url_for("lots.manage"))
        except LotError as e:
            flash(str(e))

    return render_template("manage_lots.html", lots=lot_service.lots_with_status())


@bp.route("/<int:lot_id>/edit", methods=("GET", "POST"))
@bp.route("/manage/<int:lot_id>", methods=("GET", "POST"))
@bp.route("/edit/<int:lot_id>", methods=("GET", "POST"))
@login_required
def edit(lot_id):
    denied = _admin_required()
    if denied:
        return denied

    if request.method == "POST":
        try:
            lot_service.update_lot(
                g.user, lot_id, request.form.get("name"),
                request.form.get("zone"), request.form.get("capacity"),
            )
            flash("Lot updated.")
            return redirect(url_for("lots.manage"))
        except LotError as e:
            flash(str(e))

    lot = lot_service.find_lot(lot_id)
    if lot is None:
        flash("Lot not found.")
        return redirect(url_for("lots.manage"))
    lots = lot_service.lots_with_status()
    return render_template("manage_lots.html", lots=lots, editing_lot=lot)
