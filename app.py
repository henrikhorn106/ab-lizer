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

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/database.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

db_manager = DBManager()

# Config
os.environ["USER_NAME"] = "Henrik Horn"
os.environ["USER_EMAIL"] = "henrik.horn106@gmail.com"

user_name = os.environ.get("USER_NAME")
user_email = os.environ.get("USER_EMAIL")


@app.route("/")
def index():
    total_tests = len(db_manager.get_ab_tests())
    total_variants = db_manager.get_all_variants()
    total_impressions = 0
    total_conversions = 0
    for variant in total_variants:
        total_impressions += variant.impressions
        total_conversions += variant.conversions

    recent_test = db_manager.get_recent_test()
    test_data = {}
    for test in recent_test:
        test_data[test] = db_manager.get_variants(test.id)

    return render_template("index.html",
                           user_name=user_name,
                           user_email=user_email,
                           total_tests=total_tests,
                           total_impressions=total_impressions,
                           total_conversions=total_conversions,
                           test_data=test_data
                           )


@app.route("/tests")
def tests():
    data = {}
    for test in db_manager.get_ab_tests():
        data[test] = db_manager.get_variants(test.id)

    return render_template("tests.html",
                           user_name=user_name,
                           user_email=user_email,
                           data=data
                           )


@app.route("/tests", methods=["POST"])
def create_test():
    name = request.form.get("name")
    description = request.form.get("description")
    metric= request.form.get("metric")

    # Erstelle den Test mit db_manager
    db_manager.create_ab_test(name, description, metric)

    return redirect(url_for("tests"))


@app.route("/test/<int:test_id>", methods=["POST"])
def delete_test(test_id):
    db_manager.delete_ab_test(test_id)

    return redirect(url_for("tests"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run()
