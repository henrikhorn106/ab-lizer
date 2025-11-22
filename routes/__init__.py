"""
Routes package for AB Lizer
Contains Flask Blueprints for different sections of the application
"""

from flask import Flask


def register_blueprints(app: Flask):
    """
    Register all blueprints with the Flask app

    Args:
        app: Flask application instance
    """
    from routes.home import home_bp
    from routes.tests import tests_bp
    from routes.settings import settings_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(tests_bp)
    app.register_blueprint(settings_bp)
