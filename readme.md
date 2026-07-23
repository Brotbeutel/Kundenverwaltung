# Kundenverwaltungssystem – Sportless GmbH

Webbasierte Kundenverwaltungsanwendung für Sportless GmbH mit Mitarbeiter-Login, Rollenverwaltung und DSGVO-konformer Löschfunktion.

## Projektübersicht

Diese Anwendung digitalisiert papierbasierte Kundenlisten und bietet einen zentralen Punkt für:

- Kunden anlegen, anzeigen, bearbeiten und löschen
- Mitarbeiter-Authentifizierung mit Admin- und Mitarbeiterrolle
- Kundenregistrierung über die Startseite
- optionalen E-Mail-Versand über SMTP

## Technologie-Stack

- Python 3.10+
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF
- Flask-Mail
- SQLite standardmäßig, optional konfigurierbar über `DATABASE_URL`
- `python-dotenv` zur lokalen `.env`-Konfiguration

## Verfügbare Seiten und Routen

- `/` – Startseite. Leitet angemeldete Nutzer zur Kundenliste weiter.
- `/login` – Mitarbeiter-Login
- `/logout` – Abmelden
- `/registrierung` – Kunden-Selbstregistrierung (POST)
- `/kunden` – Kundenliste und Suche
- `/kunde/neu` – Neues Kundenformular
- `/kunde/<id>/bearbeiten` – Kundenbearbeitung
- `/kunde/<id>/loeschen` – Endgültiges Löschen eines Kunden (POST, nur Admin)

## Lokale Einrichtung

Die Hauptanwendung befindet sich in `App/`. Ein Einstieg ist in `App/installation_guide.md` dokumentiert.

### Kurzer Start

```powershell
cd C:\GitHub\Kundenverwaltung\App
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
copy .env.example .env
python init_db.py
python app.py
```

Öffne dann `http://127.0.0.1:5000` im Browser.

## Standardkonten

`init_db.py` legt diese Benutzer an, falls sie noch nicht existieren:

- Admin: `admin` / `aendere-mich-admin123`
- Mitarbeiter: `mitarbeiter` / `aendere-mich-mit123`

## Konfiguration

Die Anwendung lädt Umgebungsvariablen aus einer `.env`-Datei im `App/`-Verzeichnis. Beispielwerte findest du in `App/.env.example`.

Für Mail-Parameter wie `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER` und `MAIL_SUPPRESS_SEND` wird `App/config.py` verwendet. Standardmäßig ist ein lokaler SMTP-Testserver auf `127.0.0.1:1025` konfiguriert.

## Lokaler Mail-Test

1. Installiere den lokalen SMTP-Server:
   ```powershell
   python -m pip install aiosmtpd
   python smtp_server.py
   ```
2. Setze in `App/.env`:
   ```env
   MAIL_SERVER=127.0.0.1
   MAIL_PORT=1025
   MAIL_USE_TLS=False
   MAIL_SUPPRESS_SEND=False
   ```
3. Starte die Anwendung und registriere einen Kunden über `/registrierung`.
4. Gesendete E-Mails werden im Terminal des lokalen SMTP-Servers angezeigt.

## Hinweise

- Setze `SECRET_KEY` unbedingt sicher, bevor du die App produktiv einsetzt.
- `APP_ENV=produktion` und `FLASK_DEBUG=0` sind für den Live-Betrieb empfohlen.
- Für echte SMTP-Verwendung sollten SPF/DKIM/DMARC geprüft werden.

## Weiteres

Siehe `App/installation_guide.md` für eine ausführliche Installations- und Startanleitung.

