"""
Tests Blueprint
Routes for managing AB tests and variants
"""

from flask import Blueprint, render_template, request, redirect, url_for

from data.db_manager import DBManager
from services.test_service import TestService

tests_bp = Blueprint('tests', __name__, url_prefix='/tests')

db_manager = DBManager()
test_service = TestService()


@tests_bp.route("/<int:user_id>")
def tests_page(user_id):
    """Display all tests with their variants and reports"""
    user = db_manager.get_user(user_id)
    tests = db_manager.get_ab_tests()
    variants = db_manager.get_all_variants()
    reports = db_manager.get_all_reports()

    return render_template(
        "tests.html",
        user=user,
        tests=tests,
        variants=variants,
        reports=reports
    )


@tests_bp.route("/<int:user_id>", methods=["POST"])
def tests_page_create_test(user_id):
    """Create a new test"""
    name = request.form.get("name")
    description = request.form.get("description")
    metric = request.form.get("metric")

    test_service.create_test(user_id, name, description, metric)

    return redirect(url_for("tests.tests_page", user_id=user_id))


@tests_bp.route("/<int:user_id>/<int:test_id>", methods=["POST"])
def tests_page_delete_test(user_id, test_id):
    """Delete a test"""
    test_service.delete_test(test_id)

    return redirect(url_for("tests.tests_page", user_id=user_id))


@tests_bp.route("/variants/<int:user_id>/<int:test_id>", methods=["POST"])
def tests_page_create_variant(user_id, test_id):
    """Create variants for a test"""
    impressions_a = request.form.get("var1_impressions")
    conversions_a = request.form.get("var1_conversions")
    impressions_b = request.form.get("var2_impressions")
    conversions_b = request.form.get("var2_conversions")

    test_service.create_variants_with_data(
        test_id,
        impressions_a, conversions_a,
        impressions_b, conversions_b
    )

    return redirect(url_for("tests.tests_page", user_id=user_id))


@tests_bp.route("/detailed/<int:user_id>/<int:test_id>")
def detailed_test_page(user_id, test_id):
    """Display detailed view of a single test"""
    user = db_manager.get_user(user_id)
    test = db_manager.get_test(test_id)
    variants = db_manager.get_variants(test_id)
    report = db_manager.get_report(test_id)

    return render_template(
        "detail.html",
        user=user,
        test=test,
        variants=variants,
        report=report
    )


@tests_bp.route("/detailed/<int:user_id>/<int:test_id>", methods=["POST"])
def detailed_test_page_update(user_id, test_id):
    """Update test details and variants"""
    # Update test
    name = request.form.get("name")
    description = request.form.get("description")
    metric = request.form.get("metric")
    test_service.update_test(test_id, name, description, metric)

    # Update variants (multiple at once)
    variant_ids = request.form.getlist("variant_id[]")
    sessions_list = request.form.getlist("sessions[]")
    conversions_list = request.form.getlist("conversions[]")

    # Build variant data list
    variant_data = []
    for i in range(len(variant_ids)):
        variant_data.append((
            variant_ids[i],
            sessions_list[i],
            conversions_list[i]
        ))

    test_service.update_variants_bulk(variant_data)

    return redirect(url_for("tests.detailed_test_page", user_id=user_id, test_id=test_id))
