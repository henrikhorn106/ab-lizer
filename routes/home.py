"""
Home/Dashboard Blueprint
Routes for the main dashboard page
"""

from flask import Blueprint, render_template, request, redirect, url_for

from data.db_manager import DBManager
from services.test_service import TestService

home_bp = Blueprint('home', __name__)

db_manager = DBManager()
test_service = TestService()


@home_bp.route("/")
def home_page():
    """Dashboard homepage showing overview statistics and recent test"""
    user = db_manager.get_user(1)

    # Get dashboard statistics
    stats = test_service.get_dashboard_stats()

    # Get most recent test data
    recent_test_data = test_service.get_recent_test_data()

    return render_template(
        "index.html",
        user=user,
        total_tests=stats['total_tests'],
        total_impressions=stats['total_impressions'],
        total_conversions=stats['total_conversions'],
        test=recent_test_data['test'] if recent_test_data else None,
        variants=recent_test_data['variants'] if recent_test_data else [],
        report=recent_test_data['report'] if recent_test_data else None
    )


@home_bp.route("/home/<int:user_id>", methods=["POST"])
def home_page_create_test(user_id):
    """Create a new test from the home page"""
    name = request.form.get("name")
    description = request.form.get("description")
    metric = request.form.get("metric")

    test_service.create_test(user_id, name, description, metric)

    return redirect(url_for("home.home_page"))


@home_bp.route("/home/variants/<int:user_id>/<int:test_id>", methods=["POST"])
def home_page_create_variant(user_id, test_id):
    """Create variants for a test from the home page"""
    impressions_a = request.form.get("var1_impressions")
    conversions_a = request.form.get("var1_conversions")
    impressions_b = request.form.get("var2_impressions")
    conversions_b = request.form.get("var2_conversions")

    test_service.create_variants_with_data(
        test_id,
        impressions_a, conversions_a,
        impressions_b, conversions_b
    )

    return redirect(url_for("home.home_page"))
