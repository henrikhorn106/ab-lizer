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
from utils.significance_calculator import two_proportion_z_test

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/database.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

db_manager = DBManager()


# =================================================================
# INDEX
# =================================================================

@app.route("/")
def index():
    user = db_manager.get_user(1)

    total_tests = len(db_manager.get_ab_tests())
    total_variants = db_manager.get_all_variants()
    total_impressions = 0
    total_conversions = 0
    for variant in total_variants:
        total_impressions += variant.impressions
        total_conversions += variant.conversions

    # Test data
    recent_test = db_manager.get_recent_test()
    test_data = {}
    has_variant = True
    for test in recent_test:
        test_data[test] = db_manager.get_variants(test.id)

        if test_data[test] == []:
            has_variant = False
        else:
            has_variant = True

    # Report data
    report_data = db_manager.get_report(recent_test[0].id)

    return render_template("index.html",
                           user=user,
                           total_tests=total_tests,
                           total_impressions=total_impressions,
                           total_conversions=total_conversions,
                           test_data=test_data,
                           has_variant=has_variant,
                           report_data=report_data
                           )


# =================================================================
# TESTS & VARIANTS
# =================================================================

@app.route("/tests/<int:user_id>")
def tests(user_id):
    user = db_manager.get_user(user_id)

    data = {}
    for test in db_manager.get_ab_tests():
        data[test] = db_manager.get_variants(test.id)

    return render_template("tests.html",
                           user=user,
                           data=data
                           )


@app.route("/tests/<int:user_id>", methods=["POST"])
def create_test(user_id):
    company = db_manager.get_company(user_id)

    name = request.form.get("name")
    description = request.form.get("description")
    metric= request.form.get("metric")

    db_manager.create_ab_test(company.id, name, description, metric)

    return redirect(url_for("tests", user_id=user_id))


@app.route("/tests/<int:user_id>/<int:test_id>", methods=["POST"])
def delete_test(user_id, test_id):
    db_manager.delete_ab_test(test_id)

    return redirect(url_for("tests", user_id=user_id))


@app.route("/variants/<int:user_id>/<int:test_id>", methods=["POST"])
def create_variant(user_id, test_id):

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

    db_manager.create_report(test_id, summary, data["p_value"], round(data["significant"], 2), "-")

    return redirect(url_for("tests", user_id=user_id))


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
