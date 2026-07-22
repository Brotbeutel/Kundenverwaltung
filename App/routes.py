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
# Decorator: Zugriff auf Admin-Rolle beschränken
# ---------------------------------------------------------------------------
def admin_erforderlich(view_funktion):
    """Beschränkt eine Route auf Mitarbeiter mit der Rolle 'admin'.

    Setzt @login_required voraus bzw. prüft zusätzlich, ob überhaupt ein
    Benutzer angemeldet ist. Nicht-Admins erhalten HTTP 403 Forbidden -
    das ist die geforderte DSGVO-Absicherung für das harte Löschen von
    Kundendaten.
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
    """Hilfsfunktion, falls admin_erforderlich ohne vorheriges
    @login_required auf einer Route landet (defensive Absicherung)."""
    return redirect(url_for("auth.login", next=request.path))


# ---------------------------------------------------------------------------
# Auth-Blueprint: Startseite
# ---------------------------------------------------------------------------
@auth_bp.route("/")
def startseite():
    """Zeigt die Willkommensseite der Anwendung an."""
    from flask_login import current_user
    if current_user.is_authenticated:
        return redirect(url_for("kunden.kunden_liste"))
    return render_template("index.html")


# routes.py

@auth_bp.route("/registrierung", methods=["POST"])
def selbst_registrierung():
    """Ermöglicht Kunden, sich selbst von der Startseite aus zu registrieren."""
    # Создаем новый пустой объект клиента
    kunde = Kunde()

    # Собираем данные из формы
    fehler = _kundendaten_aus_formular(kunde)

    if fehler:
        for meldung in fehler:
            flash(meldung, "error")
        return redirect(url_for("auth.startseite"))

    # Так как клиент регистрируется сам, поле сотрудника остается пустым (None)
    kunde.angelegt_von_id = None

    db.session.add(kunde)
    db.session.commit()

    # Отправляем e-mail с благодарностью за регистрацию!
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
# Auth-Blueprint: Login / Logout
# ---------------------------------------------------------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Meldet einen Mitarbeiter anhand von Benutzername und Passwort an."""

    # Bereits angemeldete Mitarbeiter direkt weiterleiten
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

        # Offene Umleitung vermeiden: nur relative Pfade aus 'next' übernehmen
        ziel = request.args.get("next")
        if ziel and ziel.startswith("/"):
            return redirect(ziel)
        return redirect(url_for("kunden.kunden_liste"))

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    """Beendet die aktuelle Sitzung sicher."""
    logout_user()
    flash("Sie wurden abgemeldet.", "info")
    return redirect(url_for("auth.login"))


# ---------------------------------------------------------------------------
# Kunden-Blueprint: CRUD
# ---------------------------------------------------------------------------
@kunden_bp.route("/kunden")
@login_required
def kunden_liste():
    """Zeigt alle Kunden an, optional gefiltert über den Query-Parameter 'q'."""
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
    """Überträgt Formulardaten aus request.form in ein Kunde-Objekt.

    Gibt eine Liste von Validierungsfehlern zurück (leer = alles ok).
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

    return fehler


@kunden_bp.route("/kunde/neu", methods=["GET", "POST"])
@login_required
def kunde_neu():
    """Erstellt einen neuen Kundendatensatz.

    Die ID des anlegenden Mitarbeiters wird automatisch aus der laufenden
    Sitzung (current_user) übernommen - kann vom Formular nicht überschrieben
    werden.
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
    """Bearbeitet einen bestehenden Kunden. Für alle angemeldeten
    Mitarbeiter zugänglich (kein admin_erforderlich)."""
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
    """Löscht einen Kundendatensatz endgültig (hartes Löschen).

    DSGVO-Vorgabe: Ausschließlich Mitarbeiter mit der Rolle 'admin' dürfen
    diese Route aufrufen. Der admin_erforderlich-Decorator sorgt dafür,
    dass normale Mitarbeiter mit HTTP 403 Forbidden abgewiesen werden,
    bevor diese Funktion überhaupt ausgeführt wird.
    """
    kunde = db.session.get(Kunde, id)
    if kunde is None:
        abort(404)

    name = kunde.vollstaendiger_name
    db.session.delete(kunde)
    db.session.commit()

    flash(f"Kunde '{name}' wurde gemäß DSGVO endgültig gelöscht.", "success")
    return redirect(url_for("kunden.kunden_liste"))
