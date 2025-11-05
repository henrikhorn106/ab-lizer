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

from flask import Flask

from models import db

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/database.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
