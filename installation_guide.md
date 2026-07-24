# Installation und Inbetriebnahme

Diese Anleitung beschreibt, wie du die Kundenverwaltungs-Anwendung lokal startest.

## Voraussetzungen

- Python 3.10 oder neuer
- `pip` für die Paketinstallation
- PowerShell, CMD oder Bash

> Wenn mehrere Python-Versionen installiert sind, verwende den vollständigen Pfad zum gewünschten Python-Executable.

## Benutze eine normale Python-Installation

Wenn VS Code aktuell die falsche Python-Installation verwendet (QMK/MSYS), wähle explizit die normale Windows-Python-Installation:

- `C:\Users\Student\AppData\Local\Python\bin\python.exe`

In VS Code:

1. Öffne die Befehlspalette (`Strg+Shift+P`).
2. Suche nach `Python: Select Interpreter`.
3. Wähle `C:\Users\Student\AppData\Local\Python\bin\python.exe` aus.

Das Repository enthält zudem eine Arbeitsbereichs-Einstellung in `.vscode/settings.json`, die diese Interpreter-Auswahl standardmäßig setzt.

> Wichtig: Wir können den Python-Interpreter selbst nicht sinnvoll in Git einchecken. Stattdessen bietet dieses Projekt eine bootstrap-Skript (`App/setup_dev_env.ps1`) und projektspezifische VS Code-Einstellungen, die den richtigen Interpreter und die lokale virtuelle Umgebung sauber starten.

## 1. Projektordner

Wechsle in das Projekt-Root-Verzeichnis:

```powershell
cd C:\GitHub\Kundenverwaltung
```

## 2. Bootstrap-Skript verwenden (empfohlen)

Das Projekt enthält ein Bootstrap-Skript, das die normale Windows-Python-Installation verwendet, eine virtuelle Umgebung erstellt, Abhängigkeiten installiert und eine `.env`-Datei aus `.env.example` anlegt.

### PowerShell

```powershell
cd C:\GitHub\Kundenverwaltung
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\App\setup_dev_env.ps1
```

### Ein-Klick-Launcher für Windows

Im Projektroot liegt `start_app.bat` bereit. Doppelklick oder Start aus PowerShell:

```powershell
cd C:\GitHub\Kundenverwaltung
.\start_app.bat
```

### Bash (falls verfügbar)

```bash
cd /c/GitHub/Kundenverwaltung/App
./setup_dev_env.sh
```

Wenn du die Schritte lieber manuell durchführen möchtest, kannst du weiterhin eine virtuelle Umgebung anlegen und aktivieren:

```powershell
python -m venv .venv
```

> Die virtuelle Umgebung wird im Projektroot angelegt. Dadurch ist der gleiche Interpreter sowohl für `init_db.py` als auch für `app.py` und den Mail-Testserver verfügbar.

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
python -m pip install -r .\App\requirements.txt
```

## 4. `.env` konfigurieren

Kopiere das Beispiel und passe die Werte an:

```powershell
copy .\App\.env.example .\.env
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
python .\App\init_db.py
```

Standardkonten:

- Admin: `admin` / `aendere-mich-admin123`
- Mitarbeiter: `mitarbeiter` / `aendere-mich-mit123`

Wenn du eigene Passwörter verwenden möchtest, setze die Variablen `ADMIN_STANDARD_PASSWORT` und `MITARBEITER_STANDARD_PASSWORT` in `.env`.

## 6. Anwendung starten

```powershell
python .\App\app.py
```

Die Anwendung ist erreichbar unter:

- `http://127.0.0.1:5000`

## 7. Lokaler SMTP-Test (optional)

Installiere optional `aiosmtpd`, wenn du den lokalen Testserver nutzen möchtest:

```powershell
.\.venv\Scripts\python.exe -m pip install aiosmtpd
.\.venv\Scripts\python.exe .\App\smtp_server.py
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
C:\Users\Student\AppData\Local\Python\bin\python.exe -m venv .venv
C:\Users\Student\AppData\Local\Python\bin\python.exe -m pip install -r .\App\requirements.txt
C:\Users\Student\AppData\Local\Python\bin\python.exe .\App\init_db.py
C:\Users\Student\AppData\Local\Python\bin\python.exe .\App\app.py
```

## 9. Produktionshinweise

- Setze `APP_ENV=produktion` und `FLASK_DEBUG=0`.
- Verwende ein sicheres `SECRET_KEY`.
- Nutze für den Produktiveinsatz einen WSGI-Server wie `gunicorn` oder `waitress`.
- Prüfe SPF/DKIM/DMARC beim Einsatz eines externen SMTP-Dienstes.
