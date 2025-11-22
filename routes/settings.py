"""
Settings Blueprint
Routes for user and company settings management
"""

from flask import Blueprint, render_template, request, redirect, url_for

from data.db_manager import DBManager

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

db_manager = DBManager()


@settings_bp.route("/<int:user_id>")
def settings_page(user_id):
    """Display user and company settings"""
    user = db_manager.get_user(user_id)
    company = db_manager.get_company(user.company_id)

    return render_template(
        "settings.html",
        user=user,
        company=company
    )


@settings_bp.route("/<int:user_id>", methods=["POST"])
def update_user(user_id):
    """Update user profile information"""
    name = request.form.get("name")
    email = request.form.get("email")
    db_manager.update_user(user_id, name, email)

    return redirect(url_for("settings.settings_page", user_id=user_id))


@settings_bp.route("/<int:user_id>/<int:company_id>", methods=["POST"])
def update_company(user_id, company_id):
    """Update company information"""
    name = request.form.get("company_name")
    year = request.form.get("year")
    audience = request.form.get("audience")
    url = request.form.get("url")
    db_manager.update_company(company_id, name, year, audience, url)

    return redirect(url_for("settings.settings_page", user_id=user_id))
