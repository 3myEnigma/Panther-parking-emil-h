from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from ..routes.auth import login_required
from ..repositories import lot_repository
from ..services import permit_service, vehicle_service
from ..services.permit_service import PermitError

bp = Blueprint("permits", __name__, url_prefix="/permits")


@bp.route("/", methods=("GET", "POST"))
@bp.route("", methods=("GET", "POST"))
@login_required
def index():
    if request.method == "POST":
        try:
            permit_service.apply_for_permit(
                g.user["id"],
                request.form.get("vehicle_id"),
                request.form.get("zone"),
            )
            flash("Permit application submitted.")
            return redirect(url_for("permits.index"))
        except PermitError as e:
            flash(str(e))

    zones = sorted({lot["zone"] for lot in lot_repository.list_all()})
    return render_template(
        "permits.html",
        permits=permit_service.list_permits(g.user["id"]),
        vehicles=vehicle_service.list_vehicles(g.user["id"]),
        zones=zones,
    )
