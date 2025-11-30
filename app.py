"""
Project AB Lizer

AB Lizer is a web application built with Python, Flask, and modern AI technologies
that helps marketers and data teams evaluate and interpret A/B test results more intelligently.

While traditional A/B testing tools show only raw numbers and significance values,
this project goes further by using Generative AI and machine learning to generate
human-readable insights, predict outcomes, and suggest data-driven improvements for future experiments.

The platform provides a clean API with full CRUD functionality,
a connected database for test storage, and an AI layer that turns data into actionable recommendations.
"""

import os

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

from data.db_manager import DBManager
from data.models import db
from routes.ai import generate_ai_recommendation, generate_ai_summary
from utils.utils import two_proportion_z_test, transform_test_data

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/database.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

db_manager = DBManager()


# =================================================================
# HELPER FUNCTIONS
# Having utils.py or helper.py script that gets imported here would be better
# =================================================================

@app.template_filter('initials')
def get_initials(name):
    """Extract initials from a full name"""
    if not name:
        return ''

    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    elif len(parts) == 1:
        return parts[0][:2].upper()
    return ''


# =================================================================
# INDEX
# =================================================================

@app.route("/")
def home_page():
    user = db_manager.get_user(1)

    total_tests = len(db_manager.get_ab_tests(user.company_id))
    total_variants = db_manager.get_all_variants(user.company_id)
    total_impressions = 0
    total_conversions = 0
    for variant in total_variants:
        total_impressions += variant.impressions
        total_conversions += variant.conversions

    # Data for the most recent test
    test = db_manager.get_recent_test(user.company_id)
    try:
        variants = db_manager.get_variants(test.id)
        report = db_manager.get_report(test.id)
    except AttributeError:
        variants = []
        report = None

    for variant in variants:
        variant.conversion_rate = round(float(variant.conversions) / float(variant.impressions) * 100, 2)

    return render_template("index.html",
                           user=user,
                           total_tests=total_tests,
                           total_impressions=total_impressions,
                           total_conversions=total_conversions,
                           test=test,
                           variants=variants,
                           report=report
                           )


@app.route("/home/<int:user_id>", methods=["POST"])
def home_page_create_test(user_id):
    company = db_manager.get_company(user_id)

    name = request.form.get("name")
    description = request.form.get("description")
    metric = request.form.get("metric")

    db_manager.create_ab_test(company.id, name, description, metric)

    return redirect(url_for("home_page", user_id=user_id))


@app.route("/home/variants/<int:user_id>/<int:test_id>", methods=["POST"])
def home_page_create_variant(user_id, test_id):

    # Create Variant A
    name = "Variant A"
    impressions_a = request.form.get("var1_impressions")
    conversions_a = request.form.get("var1_conversions")
    conversion_rate = round(float(conversions_a) / float(impressions_a) * 100, 2)
    db_manager.create_variant(test_id, name, impressions_a, conversions_a, conversion_rate)

    # Create Variant B
    name = "Variant B"
    impressions_b = request.form.get("var2_impressions")
    conversions_b = request.form.get("var2_conversions")
    conversion_rate = round(float(conversions_b) / float(impressions_b) * 100, 2)
    db_manager.create_variant(test_id, name, impressions_b, conversions_b, conversion_rate)

    # Calculate significance
    report_data = two_proportion_z_test(
        int(impressions_a),
        int(conversions_a),
        int(impressions_b),
        int(conversions_b)
    )


    # Transform data for AI

    # 1. Company data
    company = db_manager.get_company(user_id)
    company_data = {
        "name": company.name,
        "audience": company.audience,
        "year": company.year
    }
    # 2. Test data
    test_data = db_manager.get_test(test_id, company.id)
    transform_test_data(test_data, db_manager.get_variants(test_id), report_data)

    # 3. Report data
    ai_recommendation = generate_ai_recommendation(report_data, company_data)
    ai_summary = generate_ai_summary(ai_recommendation)


    # Create report
    db_manager.create_report(test_id,
                             summary=ai_summary,
                             p_value=round(report_data["p_value"], 2),
                             significance=report_data["significant"],
                             ai_recommendation=ai_recommendation)

    return redirect(url_for("home_page", user_id=user_id))


# =================================================================
# TESTS & VARIANTS
# =================================================================

@app.route("/tests/<int:user_id>")
def tests_page(user_id):
    user = db_manager.get_user(user_id)
    tests = db_manager.get_ab_tests(user.company_id)
    variants = db_manager.get_all_variants(user.company_id)
    reports = db_manager.get_all_reports()

    return render_template("tests.html",
                           user=user,
                           tests=tests,
                           variants=variants,
                           reports=reports
                           )


@app.route("/tests/<int:user_id>", methods=["POST"])
def tests_page_create_test(user_id):
    company = db_manager.get_company(user_id)

    name = request.form.get("name")
    description = request.form.get("description")
    metric = request.form.get("metric")

    db_manager.create_ab_test(company.id, name, description, metric)

    return redirect(url_for("tests_page", user_id=user_id))


@app.route("/tests/<int:user_id>/<int:test_id>", methods=["POST"])
def tests_page_delete_test(user_id, test_id):
    db_manager.delete_ab_test(test_id)

    return redirect(url_for("tests_page", user_id=user_id))


@app.route("/tests/variants/<int:user_id>/<int:test_id>", methods=["POST"])
def tests_page_create_variant(user_id, test_id):

    # Create Variant A
    name = "Variant A"
    impressions_a = request.form.get("var1_impressions")
    conversions_a = request.form.get("var1_conversions")
    conversion_rate = round(float(conversions_a) / float(impressions_a) * 100, 2)
    db_manager.create_variant(test_id, name, impressions_a, conversions_a, conversion_rate)

    # Create Variant B
    name = "Variant B"
    impressions_b = request.form.get("var2_impressions")
    conversions_b = request.form.get("var2_conversions")
    conversion_rate = round(float(conversions_b) / float(impressions_b) * 100, 2)
    db_manager.create_variant(test_id, name, impressions_b, conversions_b, conversion_rate)

    return redirect(url_for("tests_page", user_id=user_id))


# =================================================================
# EDIT TEST PAGE
# =================================================================

@app.route("/edit/<int:user_id>/<int:test_id>")
def edit_test_page(user_id, test_id):
    user = db_manager.get_user(user_id)
    test = db_manager.get_test(test_id, user.company_id)
    variants = db_manager.get_variants(test_id)
    report = db_manager.get_report(test_id)

    return render_template("edit.html", user=user, test=test, variants=variants, report=report)


@app.route("/edit/<int:user_id>/<int:test_id>", methods=["POST"])
def edit_test_page_update_variant(user_id, test_id):
    # Update test
    name = request.form.get("name")
    description = request.form.get("description")
    metric = request.form.get("metric")
    db_manager.update_ab_test(test_id, name, description, metric)

    # Update variants (multiple at once)
    variant_ids = request.form.getlist("variant_id[]")
    sessions_list = request.form.getlist("sessions[]")
    conversions_list = request.form.getlist("conversions[]")

    # Iterate through variant_ids and update their impressions and conversions
    for i in range(len(variant_ids)):
        variant_id = variant_ids[i]
        impressions = sessions_list[i]
        conversions = conversions_list[i]
        conversion_rate = round(float(conversions) / float(impressions) * 100, 2)
        db_manager.update_variant(variant_id, impressions, conversions, conversion_rate)

    # Get variant data
    variants = db_manager.get_variants(test_id)
    impressions_a = variants[0].impressions
    conversions_a = variants[0].conversions
    impressions_b = variants[1].impressions
    conversions_b = variants[1].conversions

    # Calculate significance
    report_data = two_proportion_z_test(
        int(impressions_a),
        int(conversions_a),
        int(impressions_b),
        int(conversions_b)
    )

    # Transform data for AI

    # 1. Company data
    company = db_manager.get_company(user_id)
    company_data = {
        "name": company.name,
        "audience": company.audience,
        "year": company.year
    }
    # 2. Test data
    test_data = db_manager.get_test(test_id, company.id)
    transform_test_data(test_data, db_manager.get_variants(test_id), report_data)

    # 3. Report data
    ai_recommendation = generate_ai_recommendation(test_data, report_data, company_data)
    ai_summary = generate_ai_summary(ai_recommendation)

    # Create report
    report = db_manager.get_report(test_id)
    db_manager.update_report(report.id,
                             summary=ai_summary,
                             p_value=round(report_data["p_value"], 2),
                             significance=report_data["significant"],
                             ai_recommendation=ai_recommendation)

    return redirect(url_for("edit_test_page", user_id=user_id, test_id=test_id))


# =================================================================
# API
# =================================================================

@app.route("/api/test-ratios/<int:company_id>")
def get_test_ratios(company_id):
    """
    Calculate and return the ratio of winning, losing, and other tests.

    Winning: significant AND conversion increased (Variant B > Variant A)
    Losing: significant AND conversion decreased (Variant B < Variant A)
    Other: not significant
    """
    tests = db_manager.get_ab_tests(company_id)

    winning = 0
    losing = 0
    other = 0

    for test in tests:
        try:
            report = db_manager.get_report(test.id)
            variants = db_manager.get_variants(test.id)

            # Skip if no report or not enough variants
            if not report or len(variants) < 2:
                other += 1
                continue

            # Check if significant
            if report.significance:
                # Compare conversion rates (Variant A is index 0, Variant B is index 1)
                variant_a_rate = variants[0].conversion_rate
                variant_b_rate = variants[1].conversion_rate

                if variant_b_rate > variant_a_rate:
                    winning += 1
                else:
                    losing += 1
            else:
                other += 1

        except (AttributeError, IndexError):
            other += 1

    total = winning + losing + other

    if total == 0:
        return jsonify({
            "winning": 0,
            "losing": 0,
            "other": 0,
            "winning_percent": 0,
            "losing_percent": 0,
            "other_percent": 0
        })

    return jsonify({
        "winning": winning,
        "losing": losing,
        "other": other,
        "winning_percent": round((winning / total) * 100, 1),
        "losing_percent": round((losing / total) * 100, 1),
        "other_percent": round((other / total) * 100, 1)
    })


# =================================================================
# SETTINGS
# =================================================================

@app.route("/settings/<int:user_id>")
def settings(user_id):
    user = db_manager.get_user(user_id)
    company = db_manager.get_company(user.company_id)

    return render_template("settings.html",
                           user=user,
                           company=company
                           )


@app.route("/settings/<int:user_id>", methods=["POST"])
def update_user(user_id):
    name = request.form.get("name")
    email = request.form.get("email")
    db_manager.update_user(user_id, name, email)

    return redirect(url_for("settings", user_id=user_id))


@app.route("/settings/<int:user_id>/<int:company_id>", methods=["POST"])
def update_company(user_id ,company_id):
    name = request.form.get("company_name")
    year = request.form.get("year")
    audience = request.form.get("audience")
    website = request.form.get("website")
    db_manager.update_company(company_id, name, year, audience, website)

    return redirect(url_for("settings", user_id=user_id))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run()
