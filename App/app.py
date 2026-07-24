"""
app.py
------
Customer management application factory.

Initializes Flask together with the extensions (SQLAlchemy, Flask-Login,
Flask-Mail) and registers the blueprints from routes.py.

Local startup:
    python app.py
"""

import os

from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf import CSRFProtect
from dotenv import load_dotenv
from sqlalchemy import event
from sqlalchemy.engine import Engine

load_dotenv()

from config import konfigurationen
from models import db, Mitarbeiter

# --- Extensions (initialized first, then bound in create_app()) ---
login_manager = LoginManager()
mail = Mail()
# Protects all POST forms (login, create/edit/delete customer) against
# cross-site request forgery. Every <form> in the templates must include
# the hidden field {{ csrf_token() }} (see templates/*.html).
csrf = CSRFProtect()


@event.listens_for(Engine, "connect")
def _aktiviere_sqlite_fremdschluessel(dbapi_connection, connection_record):
    """Enable enforcement of foreign-key constraints in SQLite.

    SQLite ignores foreign-key constraints such as ondelete='SET NULL' in
    models.py unless 'PRAGMA foreign_keys=ON' is enabled for each connection.
    For other databases such as PostgreSQL in production, this hook is a
    no-op and harmless.
    """
    if dbapi_connection.__class__.__module__.startswith("sqlite3"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def erstelle_app() -> Flask:
    """Create and configure the Flask application using the application factory pattern."""

    app = Flask(__name__)

    # Determine the environment (see init_db.py for the same logic)
    ist_debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    umgebung = "entwicklung" if ist_debug else os.environ.get("APP_ENV", "produktion")
    app.config.from_object(konfigurationen.get(umgebung, konfigurationen["default"]))

    # --- Bind extensions to the app ---
    db.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  # type: ignore
    login_manager.login_message = "Bitte melden Sie sich an, um fortzufahren."
    login_manager.login_message_category = "info"

    # --- Register blueprints ---
    from routes import auth_bp, kunden_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(kunden_bp)

    return app


@login_manager.user_loader
def lade_benutzer(benutzer_id: str):
    """Load an employee object from the stored session ID for each Flask-Login request."""
    return db.session.get(Mitarbeiter, int(benutzer_id))


# Module-level app instance for local startup via "python app.py"
# or for WSGI servers such as gunicorn ("app:app")
app = erstelle_app()


if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", False))
