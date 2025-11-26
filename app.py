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

from flask import Flask, render_template, request, redirect, url_for, flash

from data.db_manager import DBManager
from data.models import db
from routes.ai import generate_ai_recommendation
from routes.tests import tranform_data
from utils.significance_calculator import two_proportion_z_test

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/database.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

db_manager = DBManager()


# =================================================================
# HELPER FUNCTIONS
# =================================================================

def create_test(user_id):
    company = db_manager.get_company(user_id)

    name = request.form.get("name")
    description = request.form.get("description")
    metric = request.form.get("metric")

    db_manager.create_ab_test(company.id, name, description, metric)


def create_variant(test_id, company_id):

    # Variant A
    name = "Variant A"
    impressions_a = request.form.get("var1_impressions")
    conversions_a = request.form.get("var1_conversions")
    conversion_rate = round(float(conversions_a) / float(impressions_a) * 100, 2)
    db_manager.create_variant(test_id, name, impressions_a, conversions_a, conversion_rate)

    # Variant B
    name = "Variant B"
    impressions_b = request.form.get("var2_impressions")
    conversions_b = request.form.get("var2_conversions")
    conversion_rate = round(float(conversions_b) / float(impressions_b) * 100, 2)
    db_manager.create_variant(test_id, name, impressions_b, conversions_b, conversion_rate)

    create_report(test_id, company_id, impressions_a, conversions_a, impressions_b, conversions_b)


def create_report(test_id, company_id, impressions_a, conversions_a, impressions_b, conversions_b):
    # Calculate significance
    data = two_proportion_z_test(
        int(impressions_a),
        int(conversions_a),
        int(impressions_b),
        int(conversions_b)
    )

    if data["significant"]:
        summary = "Test was significant."
    else:
        summary = "Test was not significant."

    test = db_manager.get_test(test_id, company_id)
    tranform_data(test, db_manager.get_variants(test.id), data)
    ai_recommendation = generate_ai_recommendation(data)

    db_manager.create_report(test_id, summary, round(data["p_value"], 2), data["significant"], ai_recommendation)


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
    create_test(user_id)

    return redirect(url_for("home_page", user_id=user_id))


@app.route("/home/variants/<int:user_id>/<int:test_id>", methods=["POST"])
def home_page_create_variant(user_id, test_id):
    company_id = db_manager.get_company(user_id).id
    create_variant(test_id, company_id)

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
    create_test(user_id)

    return redirect(url_for("tests_page", user_id=user_id))


@app.route("/tests/<int:user_id>/<int:test_id>", methods=["POST"])
def tests_page_delete_test(user_id, test_id):
    db_manager.delete_ab_test(test_id)

    return redirect(url_for("tests_page", user_id=user_id))


@app.route("/tests/variants/<int:user_id>/<int:test_id>", methods=["POST"])
def tests_page_create_variant(user_id, test_id):
    create_variant(test_id)

    return redirect(url_for("tests_page", user_id=user_id))

# =================================================================
# DETAILED TEST PAGE
# =================================================================
@app.route("/detailed/<int:user_id>/<int:test_id>")
def detailed_test_page(user_id, test_id):
    user = db_manager.get_user(user_id)
    test = db_manager.get_test(test_id, user.company_id)
    variants = db_manager.get_variants(test_id)
    report = db_manager.get_report(test_id)

    return render_template("detail.html", user=user, test=test, variants=variants, report=report)


@app.route("/detailed/<int:user_id>/<int:test_id>", methods=["POST"])
def detailed_test_page_update_variant(user_id, test_id):
    # Update test
    name = request.form.get("name")
    description = request.form.get("description")
    metric = request.form.get("metric")
    db_manager.update_ab_test(test_id, name, description, metric)

    # Update variants (mehrere auf einmal)
    variant_ids = request.form.getlist("variant_id[]")
    sessions_list = request.form.getlist("sessions[]")
    conversions_list = request.form.getlist("conversions[]")

    # Durch alle Varianten iterieren
    for i in range(len(variant_ids)):
        variant_id = variant_ids[i]
        impressions = sessions_list[i]
        conversions = conversions_list[i]
        conversion_rate = round(float(conversions) / float(impressions) * 100, 2)
        db_manager.update_variant(variant_id, impressions, conversions, conversion_rate)

    return redirect(url_for("detailed_test_page", user_id=user_id, test_id=test_id))


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
    url = request.form.get("url")
    db_manager.update_company(company_id, name, year, audience, url)

    return redirect(url_for("settings", user_id=user_id))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run()
