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

from config import config
from data.models import db
from routes import register_blueprints


def create_app(config_name=None):
    """
    Application Factory pattern for Flask

    Args:
        config_name: Name of the configuration to use (development, testing, production)

    Returns:
        Configured Flask application
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    register_blueprints(app)

    # Register custom template filters
    register_template_filters(app)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app


def register_template_filters(app):
    """Register custom Jinja2 template filters"""

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


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
