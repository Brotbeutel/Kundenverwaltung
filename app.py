"""
app.py
------
Application-Factory der Kundenverwaltungs-Anwendung.

Initialisiert Flask sowie die Extensions (SQLAlchemy, Flask-Login,
Flask-Mail) und registriert die Blueprints aus routes.py.

Start (lokal):
    python app.py
"""

import os

from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from dotenv import load_dotenv
from sqlalchemy import event
from sqlalchemy.engine import Engine

load_dotenv()

from config import konfigurationen
from models import db, Mitarbeiter

# --- Extensions (noch ohne App-Bindung, siehe erstelle_app()) ---
login_manager = LoginManager()
mail = Mail()


@event.listens_for(Engine, "connect")
def _aktiviere_sqlite_fremdschluessel(dbapi_connection, connection_record):
    """Aktiviert die Durchsetzung von Foreign-Key-Constraints in SQLite.

    SQLite ignoriert FOREIGN KEY-Constraints (z.B. ondelete='SET NULL' in
    models.py) standardmäßig, solange 'PRAGMA foreign_keys=ON' nicht pro
    Verbindung gesetzt wird. Für andere Datenbanken (z.B. PostgreSQL in
    Produktion) ist dieser Hook wirkungslos und unschädlich.
    """
    if dbapi_connection.__class__.__module__.startswith("sqlite3"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def erstelle_app() -> Flask:
    """Erstellt und konfiguriert die Flask-Anwendung (Application-Factory-Pattern)."""

    app = Flask(__name__)

    # Umgebung bestimmen (siehe init_db.py für dieselbe Logik)
    ist_debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    umgebung = "entwicklung" if ist_debug else os.environ.get("APP_ENV", "produktion")
    app.config.from_object(konfigurationen.get(umgebung, konfigurationen["default"]))

    # --- Extensions an die App binden ---
    db.init_app(app)
    mail.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Bitte melden Sie sich an, um fortzufahren."
    login_manager.login_message_category = "info"

    # --- Blueprints registrieren ---
    from routes import auth_bp, kunden_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(kunden_bp)

    return app


@login_manager.user_loader
def lade_benutzer(benutzer_id: str):
    """Wird von Flask-Login bei jeder Anfrage aufgerufen, um aus der
    gespeicherten Session-ID wieder ein Mitarbeiter-Objekt zu laden."""
    return db.session.get(Mitarbeiter, int(benutzer_id))


# Modul-Ebene: App-Instanz für den lokalen Start via "python app.py"
# bzw. für WSGI-Server wie gunicorn ("app:app")
app = erstelle_app()


if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", False))
