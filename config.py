"""
Configuration for AB Lizer application
Supports different environments (development, testing, production)
"""

import os


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        f"sqlite:///{os.path.join(Config.BASE_DIR, 'data/database.db')}"


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"sqlite:///{os.path.join(Config.BASE_DIR, 'data/database.db')}"


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
