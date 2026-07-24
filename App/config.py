"""
config.py
---------
Zentrale Konfiguration der Kundenverwaltungs-Anwendung.
"""

import os
from datetime import timedelta

# Basisverzeichnis des Projekts
BASISVERZEICHNIS = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Basis-Konfiguration, gilt für alle Umgebungen."""

    # --- Sicherheit ---
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-nur-fuer-lokale-entwicklung-aendern")

    # --- Datenbank ---
    # Fix für Heroku/Render/PostgreSQL: Ersetzen von postgres:// durch postgresql://
    _db_url = os.environ.get("DATABASE_URL")
    if _db_url and _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = _db_url or "sqlite:///" + os.path.join(BASISVERZEICHNIS, "kundenverwaltung.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Login / Session ---
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    REMEMBER_COOKIE_DURATION = timedelta(days=7)

    # --- E-Mail (Flask-Mail) ---
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "127.0.0.1")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "1025"))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "False").lower() in ("1", "true", "yes", "on")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "kundenverwaltung@sportless-gmbh.de")
 
    MAIL_SUPPRESS_SEND = os.environ.get("MAIL_SUPPRESS_SEND", "False").lower() in ("1", "true", "yes", "on")
    MAIL_SERVER = "127.0.0.1"
    MAIL_PORT = 1025
    MAIL_USE_TLS = False
    MAIL_USERNAME = ""
    MAIL_PASSWORD = ""
    MAIL_DEFAULT_SENDER = "kundenverwaltung@sportless-gmbh.de"
 
    MAIL_SUPPRESS_SEND = False


class EntwicklungConfig(Config):
    """Konfiguration für die lokale Entwicklung."""
    DEBUG = True


class ProduktionConfig(Config):
    """Konfiguration für den Produktivbetrieb."""
    DEBUG = False


# Zuordnung
konfigurationen = {
    "entwicklung": EntwicklungConfig,
    "produktion": ProduktionConfig,
    "default": EntwicklungConfig,
}
