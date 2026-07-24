"""
routes.py
---------
Routes for the customer management application, split into two blueprints:

    - auth_bp:   login / logout
    - kunden_bp: customer CRUD (create, list, edit, delete)

Access model:
    - All routes except /login require an authenticated session
      (@login_required).
    - Creating and editing customers is allowed for any authenticated
      employee.
    - Final deletion of a customer record (DSGVO) is restricted to the
      'admin' role (@admin_erforderlich).
      Attempts by regular employees are rejected with HTTP 403 Forbidden.

The HTML templates (login.html, kunden_liste.html, kunde_formular.html)
use the final template and variable names so the later steps can integrate
cleanly.
"""
from datetime import datetime
from datetime import date, timedelta
import random

from flask_mail import Mail, Message

from functools import wraps

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from models import Kunde, Mitarbeiter, db

auth_bp = Blueprint("auth", __name__)
kunden_bp = Blueprint("kunden", __name__)


# ---------------------------------------------------------------------------
# Decorator: restrict access to the admin role
# ---------------------------------------------------------------------------
def admin_erforderlich(view_funktion):
    """Restrict a route to employees with the 'admin' role.

    This decorator expects @login_required to be applied first, and it
    additionally checks whether a user is authenticated at all. Non-admins
    receive HTTP 403 Forbidden, which provides the required GDPR safeguard
    for hard deletion of customer data.
    """

    @wraps(view_funktion)
    def eingewickelte_funktion(*args, **kwargs):
        if not current_user.is_authenticated:
            return login_manager_redirect()
        if not current_user.ist_admin:
            abort(403)
        return view_funktion(*args, **kwargs)

    return eingewickelte_funktion


def login_manager_redirect():
    """Helper used when admin_erforderlich is applied without a preceding
    @login_required check (defensive safeguard)."""
    return redirect(url_for("auth.login", next=request.path))


# ---------------------------------------------------------------------------
# Auth blueprint: landing page
# ---------------------------------------------------------------------------
@auth_bp.route("/")
def startseite():
    """Render the application landing page."""
    from flask_login import current_user
    if current_user.is_authenticated:
        return redirect(url_for("kunden.kunden_liste"))
    return render_template("index.html")


# routes.py

@auth_bp.route("/registrierung", methods=["POST"])
def selbst_registrierung():
    """Allow customers to self-register from the landing page."""
    # Create a new empty customer object
    kunde = Kunde()

    # Collect form data
    fehler = _kundendaten_aus_formular(kunde)

    if fehler:
        for meldung in fehler:
            flash(meldung, "error")
        return redirect(url_for("auth.startseite"))

    # Since the customer registers themselves, the employee field remains empty (None)
    kunde.angelegt_von_id = None

    db.session.add(kunde)
    db.session.commit()

    # Send a thank-you email after successful registration
    if kunde.email:
        from app import mail
        msg = Message(
            subject="Vielen Dank für Ihre Registrierung bei Sportless!",
            recipients=[kunde.email],
            body=f"Hallo {kunde.vorname} {kunde.nachname},\n\n"
                 f"vielen Dank für Ihre Registrierung in der Sportless GmbH Fitnessstudio!\n"
                 f"Wir freuen uns darauf, Sie bei Ihrem Training zu unterstützen.\n\n"
                 f"Mit sportlichen Grüßen,\n"
                 f"Ihr Sportless Team"
        )
        try:
            mail.send(msg)
            flash("Registrierung erfolgreich! Eine Bestätigung wurde an Ihre E-Mail gesendet.", "success")
        except Exception as e:
            flash("Registrierung erfolgreich, aber die Bestätigung konnte nicht gesendet werden.", "warning")

    return redirect(url_for("auth.startseite"))

# ---------------------------------------------------------------------------
# Auth blueprint: login / logout
# ---------------------------------------------------------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate an employee using username and password."""

    # Redirect already authenticated employees directly
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
            flash(
                "Dieses Konto wurde deaktiviert. Bitte wenden Sie sich an einen Admin.",
                "error",
            )
            return render_template("login.html"), 403

        login_user(mitarbeiter, remember=angemeldet_bleiben)
        flash(f"Willkommen zurück, {mitarbeiter.anzeigename}!", "success")

        # Prevent open redirects: only accept relative paths from 'next'
        ziel = request.args.get("next")
        if ziel and ziel.startswith("/"):
            return redirect(ziel)
        return redirect(url_for("kunden.kunden_liste"))

    return render_template("login.html")


@auth_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    """End the current session safely."""
    logout_user()
    flash("Sie wurden abgemeldet.", "info")
    return redirect(url_for("auth.login"))


# ---------------------------------------------------------------------------
# Customer blueprint: CRUD
# ---------------------------------------------------------------------------
@kunden_bp.route("/kunden")
@login_required
def kunden_liste():
    """List all customers, optionally filtered via the 'q' query parameter."""
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
    """Copy form data from request.form into a Kunde object.

    Returns a list of validation errors (empty means everything is valid).
    """
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

    # Read the date from the POST payload
    geburtsdatum_str = request.form.get("geburtsdatum", "").strip()
    if geburtsdatum_str:
        try:
            # Convert the string "YYYY-MM-DD" into a SQLAlchemy date object
            kunde.geburtsdatum = datetime.strptime(geburtsdatum_str, "%Y-%m-%d").date()
        except ValueError:
            fehler.append("Das Geburtsdatum hat ein ungültiges Format.")
    else:
        kunde.geburtsdatum = None

    return fehler


@kunden_bp.route("/kunde/neu", methods=["GET", "POST"])
@login_required
def kunde_neu():
    """Create a new customer record.

    The ID of the creating employee is taken automatically from the current
    session (current_user) and cannot be overridden by the form.
    """
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

        flash(f"Kunde '{kunde.vollstaendiger_name}' wurde angelegt.", "success")
        return redirect(url_for("kunden.kunden_liste"))

    return render_template("kunde_formular.html", kunde=kunde, modus="neu")


@kunden_bp.route("/kunde/<int:id>/bearbeiten", methods=["GET", "POST"])
@login_required
def kunde_bearbeiten(id: int):
    """Edit an existing customer. Accessible to all authenticated employees
    without requiring admin privileges."""
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
    """Permanently delete a customer record (hard delete).

    GDPR requirement: only employees with the 'admin' role may access this
    route. The admin_erforderlich decorator ensures that regular employees
    receive HTTP 403 Forbidden before the function is executed.
    """
    kunde = db.session.get(Kunde, id)
    if kunde is None:
        abort(404)

    name = kunde.vollstaendiger_name
    db.session.delete(kunde)
    db.session.commit()

    flash(f"Kunde '{name}' wurde gemäß DSGVO endgültig gelöscht.", "success")
    return redirect(url_for("kunden.kunden_liste"))


# routes.py
from datetime import date, timedelta
import random

@kunden_bp.route("/kunden/geburtstag-test")
@login_required
def geburtstag_simulation():
    """Simulate automated birthday-mail checking and sending."""
    from app import mail
    from flask_mail import Message

    heute = date.today()
    # Temporary terminal print for verification during development
    print(f"=== SIMULATION START: TODAY IS {heute.day}.{heute.month} ===")

    alle_kunden = Kunde.query.all()
    geburtstagskinder = []

    for kunde in alle_kunden:
        # Also print each customer we are checking to the console
        print(f"Checking customer: {kunde.vollstaendiger_name}, birthday in system: {kunde.geburtsdatum}")
        if kunde.geburtsdatum and kunde.geburtsdatum.day == heute.day and kunde.geburtsdatum.month == heute.month:
            geburtstagskinder.append(kunde)

    print(f"Birthday customers found: {len(geburtstagskinder)}")

    if not geburtstagskinder:
        flash("No customer has a birthday today. Create a test customer with today's date in the system.", "info")
        return redirect(url_for("kunden.kunden_liste"))

    # 3. Loop over all birthday customers and send their emails
    gesendete_mails = 0
    for kind in geburtstagskinder:
        if not kind.email:
            continue

        # Prepare dynamic voucher data
        betrag = random.choice([10, 15, 20])  # Random amount
        code = random.randint(1000, 9999)     # Random voucher code suffix
        gueltig_bis = (heute + timedelta(days=30)).strftime("%d.%m.%Y") # 30 days valid

        # Birthday email text
        mail_text = (
            f"Liebe/r {kind.vorname},\n\n"
            f"zu Ihrem Geburtstag gratuliert Ihnen das gesamte Team von Sportless GmbH ganz herzlich "
            f"und wünscht Ihnen Gesundheit, Glück und viele sportliche Erfolge im neuen Lebensjahr!\n\n"
            f"Als kleines Geburtstagsgeschenk möchten wir uns für Ihr Vertrauen bedanken. Deshalb erhalten "
            f"Sie von uns einen Gutschein im Wert von {betrag} €, den Sie für unsere Angebote und Leistungen nutzen können.\n\n"
            f"Ihr Gutscheincode:\n"
            f"GEBURTSTAG-{code}\n\n"
            f"Der Gutschein ist bis zum {gueltig_bis} gültig.\n\n"
            f"Wir freuen uns darauf, Sie auch weiterhin auf Ihrem sportlichen Weg begleiten zu dürfen "
            f"und wünschen Ihnen einen wunderschönen Geburtstag!\n\n"
            f"Mit freundlichen Grüßen\n"
            f"Ihr Sportless-Team"
        )

        msg = Message(
            subject="Herzlichen Glückwunsch zum Geburtstag!",
            recipients=[kind.email],
            body=mail_text
        )

        try:
            mail.send(msg)
            gesendete_mails += 1
        except Exception as e:
            flash(f"Error sending to {kind.email}: {str(e)}", "error")

    if gesendete_mails > 0:
        flash(f"Success! {gesendete_mails} birthday email(s) were simulated and sent.", "success")
    return redirect(url_for("kunden.kunden_liste"))
