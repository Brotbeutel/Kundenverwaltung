# Installation und Inbetriebnahme

Diese Anleitung beschreibt, wie du die Kundenverwaltungs-Anwendung lokal startest.

## Voraussetzungen

- Python 3.10+ (empfohlen: 3.14)
- 'pip' für die Paketinstallation

> Hinweis: Wenn mehrere Python-Versionen installiert sind, verwende den vollständigen Pfad zum normalen Windows-Python, z. B. `C:\Users\Student\AppData\Local\Python\bin\python.exe` - anstatt python [befehl]

## 1. Projektordner

Öffne ein Terminal und wechsle in das App-Verzeichnis:

```powershell
cd C:\GitHub\Kundenverwaltung\App
```

## 2. Virtuelle Umgebung anlegen

Lege eine projektlokale virtuelle Umgebung an:

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

## 4. Umgebungsvariablen konfigurieren

Erstelle im Ordner `App` eine Datei `.env` mit den benötigten Einstellungen.

### Minimalbeispiel für lokale Entwicklung

```env
FLASK_DEBUG=1
APP_ENV=entwicklung
SECRET_KEY=ein-sicheres-geheimnis

# SQLite (Standard) - optional, falls du keine andere DB verwenden möchtest
# DATABASE_URL=sqlite:///kundenverwaltung.db

MAIL_SERVER=smtp.mailtrap.io
MAIL_PORT=2525
MAIL_USE_TLS=True
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=kundenverwaltung@sportless-gmbh.de
MAIL_SUPPRESS_SEND=True

ADMIN_STANDARD_PASSWORT=aendere-mich-admin123
MITARBEITER_STANDARD_PASSWORT=aendere-mich-mit123
```

### Wichtige Hinweise

- `MAIL_SUPPRESS_SEND=True` verhindert das tatsächliche Versenden von E-Mails. Für echte Mails auf `False` setzen.
- `DATABASE_URL` kann auf eine PostgreSQL- oder MySQL-URL zeigen. Ohne `DATABASE_URL` verwendet die App `sqlite:///kundenverwaltung.db`.
- Ändere `SECRET_KEY` unbedingt vor dem produktiven Einsatz.

## 5. Datenbank initialisieren

Führe das Setup-Skript aus, um die Tabellen zu erstellen und Beispielkonten anzulegen:

```powershell
python init_db.py
```

Das Skript legt standardmäßig diese Benutzer an:

- Admin: `admin` / `aendere-mich-admin123`
- Mitarbeiter: `mitarbeiter` / `aendere-mich-mit123`

Wenn du eigene Passwörter verwenden möchtest, setze die Umgebungsvariablen `ADMIN_STANDARD_PASSWORT` und `MITARBEITER_STANDARD_PASSWORT`.

## 6. Anwendung starten

```powershell
python app.py
```

Die Anwendung läuft standardmäßig unter:

- `http://127.0.0.1:5000`

## 7. Lokaler E-Mail-Test (optional)

Für lokale SMTP-Tests kannst du den mitgelieferten Testserver starten:

```powershell
python smtp_server.py
```

Anschließend in `.env` konfiguriere:

```env
MAIL_SERVER=127.0.0.1
MAIL_PORT=1025
MAIL_USE_TLS=False
MAIL_SUPPRESS_SEND=False
```

## 8. Hinweise für Windows mit mehreren Python-Installationen

Wenn `python` im Terminal auf die falsche Version zeigt, verwende stattdessen den vollständigen Installationspfad, z. B.:

```powershell
C:\Users\Student\AppData\Local\Python\bin\python.exe -m venv .venv
C:\Users\Student\AppData\Local\Python\bin\python.exe -m pip install -r requirements.txt
C:\Users\Student\AppData\Local\Python\bin\python.exe init_db.py
C:\Users\Student\AppData\Local\Python\bin\python.exe app.py
```

## 9. Produktionshinweise

- Stelle sicher, dass `SECRET_KEY` sicher gesetzt ist.
- Setze `APP_ENV=produktion` und `FLASK_DEBUG=0`.
- Leite E-Mails über einen produktiven SMTP-Provider weiter und überprüfe SPF/DKIM/DMARC.
- Verwende bei Bedarf einen WSGI-Server wie `gunicorn` oder `waitress` statt des integrierten Flask-Servers.
