"""
routes.py
---------
Routen der Kundenverwaltungs-Anwendung, aufgeteilt in zwei Blueprints:

    - auth_bp:   Login / Logout
    - kunden_bp: Kunden-CRUD (Anlegen, Anzeigen, Bearbeiten, Löschen)

Rechte-Modell:
    - Alle Routen (außer /login) erfordern eine angemeldete Sitzung
      (@login_required).
    - Anlegen und Bearbeiten von Kunden ist jedem angemeldeten Mitarbeiter
      erlaubt.
    - Das endgültige Löschen eines Kundendatensatzes (DSGVO) ist
      ausschließlich der Rolle 'admin' vorbehalten (@admin_erforderlich).
      Ein Zugriffsversuch durch einen normalen Mitarbeiter wird mit
      HTTP 403 Forbidden abgelehnt.

Die HTML-Templates (login.html, kunden_liste.html, kunde_formular.html)
folgen in Schritt 4 - hier wird bereits mit den finalen Template- und
Variablennamen gearbeitet, damit Schritt 4 direkt andocken kann.
"""

from functools import wraps

from functools import wraps
from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    current_app
)
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message

from models import Kunde, Mitarbeiter, db

# Wir importieren das Mail-Objekt aus der App, aber lokal innerhalb von Funktionen, um Schleifen zu vermeiden.
auth_bp = Blueprint("auth", __name__)
kunden_bp = Blueprint("kunden", __name__)

# ---------------------------------------------------------------------------
# E-mails: Logik zum Versenden von Willkommens-E-Mails an neue Kunden
# ---------------------------------------------------------------------------
def sende_willkommens_mail(kunde):
    """Sendet automatisch eine E-Mail an einen neuen Kunden."""
    from app import mail # Lokale Importe verhindern zirkuläre Importe.

    if not kunde.email:
        return # Wenn keine E-Mail-Adresse angegeben ist, unternehmen wir nichts.

    msg = Message(
        subject="Willkommen bei der Sportless GmbH!",
        recipients=[kunde.email],
        body=f"Hallo {kunde.vorname} {kunde.nachname},\n\n"
            f"vielen Dank für Ihr Vertrauen! Wir haben Ihre Daten erfolgreich "
            f"in unserem neuen digitalen System erfasst.\n\n"
            f"Mit freundlichen Grüßen,\n"
            f"Das Team der Sportless GmbH"
    )
    try:
        mail.send(msg)
        flash(f"Willkommens-E-Mail an {kunde.email} wurde versendet.", "info")
    except Exception as e:
        # Если почта не отправилась (например, сервер отключен), приложение не должно падать
        flash(f"E-Mail-Versand fehlgeschlagen: {str(e)}", "warning")

# ---------------------------------------------------------------------------
# Decorator: Zugriff auf Admin-Rolle beschränken
# ---------------------------------------------------------------------------
def admin_erforderlich(view_funktion):
    @wraps(view_funktion)
    def eingewickelte_funktion(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login", next=request.path))
        if not current_user.ist_admin:
            abort(403)
        return view_funktion(*args, **kwargs)
    return eingewickelte_funktion


# ---------------------------------------------------------------------------
# Auth-Blueprint: Login / Logout
# ---------------------------------------------------------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("kunden.kunden_liste"))

    if request.method == "POST":
        benutzername = request.form.get("benutzername", "").strip()
        passwort = request.form.get("passwort", "")
        angemeldet_bleiben = bool(request.form.get("angemeldet_bleiben"))

        mitarbeiter = Mitarbeiter.query.filter_by(benutzername=benutzername).first()

        if mitarbeiter is None or not mitarbeiter.prüfe_passwort(passwort):
            flash("Benutzername oder Passwort ist falsch.", "error")
            return render_template("login.html"), 401

        if not mitarbeiter.aktiv:
            flash("Dieses Konto wurde deaktiviert. Bitte wenden Sie sich an einen Admin.", "error")
            return render_template("login.html"), 403

        login_user(mitarbeiter, remember=angemeldet_bleiben)
        flash(f"Willkommen zurück, {mitarbeiter.anzeigename}!", "success")

        ziel = request.args.get("next")
        if ziel and ziel.startswith("/"):
            return redirect(ziel)
        return redirect(url_for("kunden.kunden_liste"))

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sie wurden abgemeldet.", "info")
    return redirect(url_for("auth.login"))


# ---------------------------------------------------------------------------
# Kunden-Blueprint: CRUD
# ---------------------------------------------------------------------------
@kunden_bp.route("/kunden")
@login_required
def kunden_liste():
    suchbegriff = request.args.get("q", "").strip()
    abfrage = Kunde.query

    if suchbegriff:
        muster = f"%{suchbegriff}%"
        abfrage = abfrage.filter(
            db.or_(
                Kunde.vorname.ilike(muster),
                Kunde.nachname.ilike(muster),
                Kunde.firma.ilike(muster),
                Kunde.ort.ilike(muster),
            )
        )

    kunden = abfrage.order_by(Kunde.nachname.asc(), Kunde.vorname.asc()).all()
    return render_template("kunden_liste.html", kunden=kunden, suchbegriff=suchbegriff)


def _kundendaten_aus_formular(kunde: Kunde) -> list[str]:
    fehler = []
    vorname = request.form.get("vorname", "").strip()
    nachname = request.form.get("nachname", "").strip()

    if not vorname:
        fehler.append("Der Vorname darf nicht leer sein.")
    if not nachname:
        fehler.append("Der Nachname darf nicht leer sein.")

    kunde.vorname = vorname
    kunde.nachname = nachname
    kunde.firma = request.form.get("firma", "").strip() or None
    kunde.strasse = request.form.get("strasse", "").strip() or None
    kunde.plz = request.form.get("plz", "").strip() or None
    kunde.ort = request.form.get("ort", "").strip() or None
    kunde.email = request.form.get("email", "").strip() or None
    kunde.telefon = request.form.get("telefon", "").strip() or None
    kunde.notizen = request.form.get("notizen", "").strip() or None

    return fehler


@kunden_bp.route("/kunde/neu", methods=["GET", "POST"])
@login_required
def kunde_neu():
    kunde = Kunde()

    if request.method == "POST":
        fehler = _kundendaten_aus_formular(kunde)

        if fehler:
            for meldung in fehler:
                flash(meldung, "error")
            return render_template("kunde_formular.html", kunde=kunde, modus="neu"), 400

        kunde.angelegt_von_id = current_user.id
        db.session.add(kunde)
        db.session.commit()

        # ТРИГГЕР ОТПРАВКИ ПИСЬМА:
        sende_willkommens_mail(kunde)

        flash(f"Kunde '{kunde.vollstaendiger_name}' wurde angelegt.", "success")
        return redirect(url_for("kunden.kunden_liste"))

    return render_template("kunde_formular.html", kunde=kunde, modus="neu")


@kunden_bp.route("/kunde/<int:id>/bearbeiten", methods=["GET", "POST"])
@login_required
def kunde_bearbeiten(id: int):
    kunde = db.session.get(Kunde, id)
    if kunde is None:
        abort(404)

    if request.method == "POST":
        fehler = _kundendaten_aus_formular(kunde)

        if fehler:
            for meldung in fehler:
                flash(meldung, "error")
            return render_template("kunde_formular.html", kunde=kunde, modus="bearbeiten"), 400

        db.session.commit()
        flash(f"Kunde '{kunde.vollstaendiger_name}' wurde aktualisiert.", "success")
        return redirect(url_for("kunden.kunden_liste"))

    return render_template("kunde_formular.html", kunde=kunde, modus="bearbeiten")


@kunden_bp.route("/kunde/<int:id>/loeschen", methods=["POST"])
@login_required
@admin_erforderlich
def kunde_loeschen(id: int):
    kunde = db.session.get(Kunde, id)
    if kunde is None:
        abort(404)

    name = kunde.vollstaendiger_name
    db.session.delete(kunde)
    db.session.commit()

    flash(f"Kunde '{name}' wurde gemäß DSGVO endgültig gelöscht.", "success")
    return redirect(url_for("kunden.kunden_liste"))
