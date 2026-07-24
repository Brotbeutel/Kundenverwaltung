"""
init_db.py
----------
One-time database setup script.
"""

import os
import sys
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

from config import konfigurationen
from models import db, Mitarbeiter, Rolle


def erstelle_app() -> Flask:
    """Create an isolated Flask application context for the database setup."""
    app = Flask(__name__)

    is_debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    umgebung = "entwicklung" if is_debug else os.environ.get("APP_ENV", "produktion")

    app.config.from_object(konfigurationen.get(umgebung, konfigurationen["default"]))
    db.init_app(app)
    return app


def lege_testkonten_an() -> None:
    """Create the admin and employee accounts if they do not already exist."""
    admin_pw = os.environ.get("ADMIN_STANDARD_PASSWORT", "aendere-mich-admin123")
    mitarbeiter_pw = os.environ.get("MITARBEITER_STANDARD_PASSWORT", "aendere-mich-mit123")

    if Mitarbeiter.query.filter_by(benutzername="admin").first() is None:
        admin = Mitarbeiter(
            benutzername="admin",
            anzeigename="Administrator",
            rolle=Rolle.ADMIN,
        )
        admin.setze_passwort(admin_pw)
        db.session.add(admin)
        print("✔ Admin-Konto 'admin' angelegt.")
    else:
        print("… Admin-Konto 'admin' existiert bereits, wird übersprungen.")

    if Mitarbeiter.query.filter_by(benutzername="mitarbeiter").first() is None:
        mitarbeiter = Mitarbeiter(
            benutzername="mitarbeiter",
            anzeigename="Test-Mitarbeiter",
            rolle=Rolle.MITARBEITER,
        )
        mitarbeiter.setze_passwort(mitarbeiter_pw)
        db.session.add(mitarbeiter)
        print("✔ Mitarbeiter-Konto 'mitarbeiter' angelegt.")
    else:
        print("… Mitarbeiter-Konto 'mitarbeiter' existiert bereits, wird übersprungen.")

    db.session.commit()


def main() -> None:
    app = erstelle_app()
    with app.app_context():
        db.create_all()
        print("✔ Datenbanktabellen erstellt (oder bereits vorhanden).")
        lege_testkonten_an()

    admin_pw = os.environ.get("ADMIN_STANDARD_PASSWORT", "aendere-mich-admin123")
    mitarbeiter_pw = os.environ.get("MITARBEITER_STANDARD_PASSWORT", "aendere-mich-mit123")

    print("\nFertig! Die Datenbank ist einsatzbereit.")
    print("Login-Daten (Aktuelle Konfiguration):")
    print(f"  Admin:       Benutzername='admin'       Passwort='{admin_pw}'")
    print(f"  Mitarbeiter: Benutzername='mitarbeiter' Passwort='{mitarbeiter_pw}'")


if __name__ == "__main__":
    sys.exit(main())
