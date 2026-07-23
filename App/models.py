"""
models.py
---------
Datenbankmodelle der Kundenverwaltungs-Anwendung.
"""

from datetime import datetime, timezone
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Rolle:
    """Erlaubte Rollen für Mitarbeiterkonten."""
    MITARBEITER = "mitarbeiter"
    ADMIN = "admin"
    ALLE = (MITARBEITER, ADMIN)


class Mitarbeiter(db.Model, UserMixin):
    """Ein Mitarbeiterkonto, mit dem sich Angestellte der Sportless GmbH
    im System einloggen können."""

    __tablename__ = "mitarbeiter"

    id = db.Column(db.Integer, primary_key=True)
    benutzername = db.Column(db.String(64), unique=True, nullable=False, index=True)
    anzeigename = db.Column(db.String(120), nullable=False)

    # 512 Zeichen, um lange scrypt-Hashes (Werkzeug 3.x) sicher zu speichern
    passwort_hash = db.Column(db.String(512), nullable=False)

    rolle = db.Column(db.String(20), nullable=False, default=Rolle.MITARBEITER)
    aktiv = db.Column(db.Boolean, nullable=False, default=True)

    erstellt_am = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Wenn ein Mitarbeiter gelöscht wird, bleiben seine Kunden erhalten
    # (angelegt_von_id wird auf NULL gesetzt, siehe Kunde.angelegt_von_id)
    kunden = db.relationship(
        "Kunde",
        backref=db.backref("angelegt_von", lazy="joined"),
        lazy=True
    )

    def setze_passwort(self, klartext_passwort: str) -> None:
        """Speichert nur den Hash des Passworts (Werkzeug 3.0.3 nutzt scrypt)."""
        self.passwort_hash = generate_password_hash(klartext_passwort)

    def prüfe_passwort(self, klartext_passwort: str) -> bool:
        return check_password_hash(self.passwort_hash, klartext_passwort)

    @property
    def ist_admin(self) -> bool:
        return self.rolle == Rolle.ADMIN

    @property
    def is_active(self) -> bool:  # noqa: N802
        return self.aktiv

    def __repr__(self) -> str:
        return f"<Mitarbeiter {self.benutzername} ({self.rolle})>"


class Kunde(db.Model):
    """Ein Kundendatensatz der Sportless GmbH."""

    __tablename__ = "kunden"

    id = db.Column(db.Integer, primary_key=True)

    vorname = db.Column(db.String(100), nullable=False)
    nachname = db.Column(db.String(100), nullable=False)
    geburtsdatum = db.Column(db.Date, nullable=True)
    firma = db.Column(db.String(150), nullable=True)

    strasse = db.Column(db.String(150), nullable=True)
    plz = db.Column(db.String(10), nullable=True)
    ort = db.Column(db.String(100), nullable=True)

    email = db.Column(db.String(150), nullable=True)
    telefon = db.Column(db.String(50), nullable=True)

    notizen = db.Column(db.Text, nullable=True)

    erstellt_am = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    aktualisiert_am = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # ondelete="SET NULL": Kunden bleiben erhalten, wenn der anlegende
    # Mitarbeiter gelöscht wird (nur mit aktivierten FK-Constraints wirksam,
    # siehe Hinweis zu SQLite in app.py)
    angelegt_von_id = db.Column(
        db.Integer,
        db.ForeignKey("mitarbeiter.id", ondelete="SET NULL"),
        nullable=True
    )

    @property
    def vollstaendiger_name(self) -> str:
        return f"{self.vorname} {self.nachname}"

    def __repr__(self) -> str:
        return f"<Kunde {self.vollstaendiger_name} ({self.firma or 'privat'})>"
