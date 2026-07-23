# Installation und Inbetriebnahme

Diese Anleitung beschreibt, wie du die Kundenverwaltungs-Anwendung lokal startest.

## Voraussetzungen

- Python 3.10 oder neuer
- `pip` für die Paketinstallation
- PowerShell, CMD oder Bash

> Wenn mehrere Python-Versionen installiert sind, verwende den vollständigen Pfad zum gewünschten Python-Executable.

## 1. Projektordner

Wechsle in das `App`-Verzeichnis:

```powershell
cd C:\GitHub\Kundenverwaltung\App
```

## 2. Virtuelle Umgebung anlegen

Erstelle eine lokale virtuelle Umgebung:

```powershell
python -m venv .venv
```

Aktiviere die Umgebung:

- PowerShell:
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- CMD:
  ```cmd
  .\.venv\Scripts\activate.bat
  ```
- Bash (WSL / Git Bash):
  ```bash
  source .venv/bin/activate
  ```

## 3. Abhängigkeiten installieren

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 4. `.env` konfigurieren

Kopiere das Beispiel und passe die Werte an:

```powershell
copy .env.example .env
```

### Beispielwerte für `.env`

```env
FLASK_DEBUG=1
APP_ENV=entwicklung
SECRET_KEY=ein-sicheres-geheimnis
DATABASE_URL=sqlite:///kundenverwaltung.db
ADMIN_STANDARD_PASSWORT=aendere-mich-admin123
MITARBEITER_STANDARD_PASSWORT=aendere-mich-mit123

MAIL_SERVER=127.0.0.1
MAIL_PORT=1025
MAIL_USE_TLS=False
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=kundenverwaltung@sportless-gmbh.de
MAIL_SUPPRESS_SEND=True
```

### Hinweise

- `SECRET_KEY` sollte für den produktiven Einsatz geändert werden.
- Ohne `DATABASE_URL` verwendet die App standardmäßig `sqlite:///kundenverwaltung.db`.
- Mail-Einstellungen können jetzt über `.env` gesetzt werden.
- `MAIL_SUPPRESS_SEND=True` verhindert das tatsächliche Versenden.

## 5. Datenbank initialisieren

Erstelle die Tabellen und lege die Standardkonten an:

```powershell
python init_db.py
```

Standardkonten:

- Admin: `admin` / `aendere-mich-admin123`
- Mitarbeiter: `mitarbeiter` / `aendere-mich-mit123`

Wenn du eigene Passwörter verwenden möchtest, setze die Variablen `ADMIN_STANDARD_PASSWORT` und `MITARBEITER_STANDARD_PASSWORT` in `.env`.

## 6. Anwendung starten

```powershell
python app.py
```

Die Anwendung ist erreichbar unter:

- `http://127.0.0.1:5000`

## 7. Lokaler SMTP-Test (optional)

Installiere optional `aiosmtpd`, wenn du den lokalen Testserver nutzen möchtest:

```powershell
python -m pip install aiosmtpd
python smtp_server.py
```

Für den Testserver sollte deine `.env` enthalten:

```env
MAIL_SERVER=127.0.0.1
MAIL_PORT=1025
MAIL_USE_TLS=False
MAIL_SUPPRESS_SEND=False
```

## 8. Tipps bei mehreren Python-Versionen

Wenn `python` nicht die gewünschte Version verwendet, starte Befehle mit dem vollständigen Pfad:

```powershell
C:\Users\Student\AppData\Local\Python\Python310\python.exe -m venv .venv
C:\Users\Student\AppData\Local\Python\Python310\python.exe -m pip install -r requirements.txt
C:\Users\Student\AppData\Local\Python\Python310\python.exe init_db.py
C:\Users\Student\AppData\Local\Python\Python310\python.exe app.py
```

## 9. Produktionshinweise

- Setze `APP_ENV=produktion` und `FLASK_DEBUG=0`.
- Verwende ein sicheres `SECRET_KEY`.
- Nutze für den Produktiveinsatz einen WSGI-Server wie `gunicorn` oder `waitress`.
- Prüfe SPF/DKIM/DMARC beim Einsatz eines externen SMTP-Dienstes.
