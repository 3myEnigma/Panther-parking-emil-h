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


def _admin_redirect():
    if not permit_service.is_admin(g.user):
        flash("Admin access required.")
        return redirect(url_for("lots.index"))
    return None


@bp.route("/approve", methods=("GET", "POST"))
@bp.route("/manage", methods=("GET", "POST"))
@bp.route("/approve-permits", methods=("GET", "POST"))
@login_required
def approve():
    denied = _admin_redirect()
    if denied:
        return denied

    if request.method == "POST":
        permit_id = request.form.get("permit_id") or request.form.get("id")
        action = request.form.get("action")
        try:
            if action == "approve" or request.form.get("approve"):
                permit_service.approve_permit(g.user, permit_id)
                flash("Permit approved.")
            elif action == "reject" or request.form.get("reject"):
                permit_service.reject_permit(g.user, permit_id)
                flash("Permit rejected.")
        except (PermitError, ValueError, TypeError) as e:
            flash(str(e))
        return redirect(url_for("permits.approve"))

    return render_template(
        "approve_permits.html",
        permits=permit_service.list_pending_permits(g.user),
    )


@bp.route("/<int:permit_id>/approve", methods=("POST",))
@bp.route("/approve/<int:permit_id>", methods=("POST",))
@login_required
def approve_permit(permit_id):
    denied = _admin_redirect()
    if denied:
        return denied
    try:
        permit_service.approve_permit(g.user, permit_id)
        flash("Permit approved.")
    except PermitError as e:
        flash(str(e))
    return redirect(url_for("permits.approve"))


@bp.route("/<int:permit_id>/reject", methods=("POST",))
@bp.route("/reject/<int:permit_id>", methods=("POST",))
@login_required
def reject_permit(permit_id):
    denied = _admin_redirect()
    if denied:
        return denied
    try:
        permit_service.reject_permit(g.user, permit_id)
        flash("Permit rejected.")
    except PermitError as e:
        flash(str(e))
    return redirect(url_for("permits.approve"))
