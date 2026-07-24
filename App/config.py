"""
config.py
---------
Central configuration for the customer management application.
"""

import os
from datetime import timedelta

# Project base directory
BASISVERZEICHNIS = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration shared by all environments."""

    # --- Security ---
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-for-local-development-change-me")

    # --- Database ---
    # Compatibility fix for Heroku/Render/PostgreSQL: convert postgres:// to postgresql://
    _db_url = os.environ.get("DATABASE_URL")
    if _db_url and _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = _db_url or "sqlite:///" + os.path.join(BASISVERZEICHNIS, "kundenverwaltung.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Login / session ---
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    REMEMBER_COOKIE_DURATION = timedelta(days=7)

    # --- Email (Flask-Mail) ---
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "127.0.0.1")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "1025"))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "False").lower() in ("1", "true", "yes", "on")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "kundenverwaltung@sportless-gmbh.de")
    MAIL_SUPPRESS_SEND = os.environ.get("MAIL_SUPPRESS_SEND", "False").lower() in ("1", "true", "yes", "on")


class EntwicklungConfig(Config):
    """Configuration for local development."""
    DEBUG = True


class ProduktionConfig(Config):
    """Configuration for production."""
    DEBUG = False


# Mapping
konfigurationen = {
    "entwicklung": EntwicklungConfig,
    "produktion": ProduktionConfig,
    "default": EntwicklungConfig,
}
