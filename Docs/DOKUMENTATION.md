# Dokumentation: Kundenverwaltung Sportless GmbH

## 1. Übersicht

Dieses Programm ist eine kleine Web-Anwendung, mit der die Sportless GmbH ihre Kundendaten digital verwaltet — statt wie bisher auf Zetteln und in Notizbüchern.

**Was das Programm löst:**
- Mitarbeiter können sich mit Benutzername und Passwort anmelden.
- Sie können Kunden anlegen, in einer Liste ansehen und Daten bearbeiten (Name, Firma, Adresse, Geburtsdatum, Kontaktdaten, Notizen).
- Nur Administratoren dürfen Kunden endgültig löschen — das ist Pflicht wegen der DSGVO (dem deutschen Datenschutzgesetz).
- Kunden können sich auch selbst über eine Startseite registrieren.
- Das System kann automatisch E-Mails an Kunden verschicken — zum Beispiel eine Bestätigung nach der Registrierung oder eine Glückwunsch-Mail mit Rabattcode zum Geburtstag.

Kurz gesagt: Alles, was vorher auf Papier passiert ist, passiert jetzt im Browser — sicherer, schneller und durchsuchbar.

## 2. Voraussetzungen

Um das Programm zu starten, wird Folgendes benötigt:

| Was | Wofür wird es gebraucht |
|---|---|
| Python 3.12 oder neuer | Die Programmiersprache, in der alles geschrieben ist |
| Flask | Das "Grundgerüst" der Web-Anwendung — sorgt dafür, dass der Browser überhaupt etwas anzeigen kann |
| Flask-SQLAlchemy | Verbindet das Programm mit der Datenbank (dort werden die Kundendaten gespeichert) |
| Flask-Login | Kümmert sich um das Anmelden/Abmelden der Mitarbeiter |
| Flask-Mail | Verschickt die automatischen E-Mails |
| Flask-WTF | Schützt die Formulare vor Missbrauch (mehr dazu in Abschnitt 4) |
| Werkzeug | Verschlüsselt die Passwörter sicher |
| python-dotenv | Liest geheime Einstellungen (z. B. Passwörter) aus einer separaten Datei, statt sie im Code zu verstecken |
| aiosmtpd *(nur zum Testen)* | Ein kleiner "Fake-Postbote" für den eigenen Rechner, der E-Mails nicht wirklich verschickt, sondern nur im Terminal anzeigt |

Alle Pakete außer `aiosmtpd` stehen in der Datei `requirements.txt` und lassen sich mit einem einzigen Befehl installieren:
```
pip install -r requirements.txt
```

## 3. Code-Struktur

Das Programm ist auf mehrere Dateien aufgeteilt. Jede Datei hat eine klare Aufgabe:

| Datei | Aufgabe |
|---|---|
| `app.py` | Startet die Anwendung und verbindet alle Bausteine (Datenbank, Login, E-Mail, Sicherheit) miteinander |
| `config.py` | Enthält alle Einstellungen an einem Ort (z. B. wo die Datenbank liegt, wie der E-Mail-Versand funktioniert) |
| `models.py` | Beschreibt, welche Daten gespeichert werden — also wie ein "Mitarbeiter" und ein "Kunde" in der Datenbank aussehen |
| `init_db.py` | Ein Einmal-Skript, das die Datenbank anlegt und zwei Testkonten erstellt |
| `routes.py` | Enthält die eigentliche Logik: Was passiert, wenn jemand eine bestimmte Seite aufruft? |
| `smtp_server.py` | Ein kleiner Test-Postbote für den eigenen Rechner (siehe Abschnitt 4) |
| `templates/` | Die HTML-Seiten, die der Nutzer im Browser sieht |

### Die wichtigsten Datenmodelle (`models.py`)

| Modell | Beschreibung |
|---|---|
| `Mitarbeiter` | Ein Benutzerkonto zum Anmelden. Hat einen Namen, ein verschlüsseltes Passwort und eine Rolle (`mitarbeiter` oder `admin`) |
| `Kunde` | Ein Kundendatensatz mit Vorname, Nachname, Geburtsdatum, Firma, Adresse, E-Mail, Telefon und Notizen |

### Die wichtigsten Seiten/Funktionen (`routes.py`)

Eine "Route" ist einfach eine Web-Adresse, hinter der eine bestimmte Aktion steckt — zum Beispiel "zeige die Kundenliste an" oder "lösche diesen Kunden".

| Adresse (Route) | Was passiert dort | Wer darf das? |
|---|---|---|
| `/` | Zeigt die öffentliche Startseite mit Registrierungsformular | Jeder (auch ohne Anmeldung) |
| `/registrierung` | Ein Kunde meldet sich selbst als neuer Kunde an | Jeder (auch ohne Anmeldung) |
| `/login` | Mitarbeiter meldet sich mit Benutzername und Passwort an | Jeder |
| `/logout` | Mitarbeiter meldet sich ab | Angemeldete Mitarbeiter |
| `/kunden` | Zeigt die Liste aller Kunden, mit Suchfunktion | Angemeldete Mitarbeiter |
| `/kunde/neu` | Formular zum Anlegen eines neuen Kunden | Angemeldete Mitarbeiter |
| `/kunde/<id>/bearbeiten` | Formular zum Bearbeiten eines bestehenden Kunden | Angemeldete Mitarbeiter |
| `/kunde/<id>/loeschen` | Löscht einen Kunden **endgültig** | **Nur Administratoren** |
| `/kunden/geburtstag-test` | Prüft, welche Kunden heute Geburtstag haben, und verschickt eine Glückwunsch-Mail mit Rabattcode | Angemeldete Mitarbeiter |

**Kleiner Hinweis:** Die Geburtstags-Mail-Funktion kann aktuell von jedem angemeldeten Mitarbeiter ausgelöst werden, nicht nur von Admins. Das ist unkritisch, weil dabei keine Kundendaten verändert oder gelöscht werden — falls gewünscht, lässt sich das aber genauso wie beim Löschen auf Admins einschränken.

## 4. Automatisierungen & Sicherheit

### Wie werden Passwörter geschützt?

Kein Passwort wird jemals im Klartext gespeichert. Stattdessen wird beim Anlegen eines Kontos nur ein sogenannter "Hash" gespeichert — eine Art Fingerabdruck des Passworts, aus dem sich das Original nicht mehr zurückrechnen lässt. Beim Login wird geprüft, ob der Fingerabdruck des eingegebenen Passworts zum gespeicherten Fingerabdruck passt.

### Wie funktionieren die Admin-Rechte (DSGVO)?

Jeder Mitarbeiter hat eine Rolle: entweder `mitarbeiter` oder `admin`. Vor dem endgültigen Löschen eines Kunden prüft das Programm automatisch, welche Rolle die angemeldete Person hat:

- Ist die Person **Admin** → Löschen wird ausgeführt.
- Ist die Person **normaler Mitarbeiter** → Das Programm verweigert die Aktion sofort und zeigt eine Fehlermeldung ("403 Forbidden") — der Löschvorgang wird gar nicht erst gestartet.

Das stellt sicher, dass Kundendaten nach DSGVO nur von befugten Personen endgültig entfernt werden können.

### Wie sind die Formulare vor Missbrauch geschützt?

Jedes Formular (Login, Kunde anlegen, Kunde löschen usw.) enthält ein unsichtbares Sicherheits-Feld, den sogenannten CSRF-Token. Das verhindert, dass eine fremde Webseite heimlich in eurem Namen Aktionen auslöst (z. B. dich dazu bringt, ohne dein Wissen einen Kunden zu löschen). Ohne gültigen Token lehnt das Programm die Anfrage automatisch ab.

### Wie funktioniert der automatische E-Mail-Versand?

Das Programm verschickt E-Mails in drei Situationen:

1. **Registrierungsbestätigung** — sobald sich ein Kunde über die Startseite selbst registriert, bekommt er automatisch eine Dankes-Mail.
2. **Geburtstags-Mail mit Rabattcode** — über die Test-Funktion `/kunden/geburtstag-test` prüft das Programm, welche Kunden heute Geburtstag haben, und verschickt automatisch eine Glückwunsch-Mail mit einem zufällig erzeugten Rabattcode (10, 15 oder 20 €), der 30 Tage gültig ist.
3. *(Weitere Vorlagen lassen sich nach demselben Muster ergänzen.)*

**Wichtig für Tests auf dem eigenen Rechner:** Damit beim Testen keine echten E-Mails an echte Adressen verschickt werden, gibt es die Datei `smtp_server.py`. Das ist ein kleiner "Fake-Postbote", der auf dem eigenen Rechner läuft, alle E-Mails entgegennimmt und sie einfach im Terminal-Fenster anzeigt — statt sie wirklich zu verschicken.

So testet man es:
1. Terminal öffnen und `python smtp_server.py` ausführen (läuft und wartet auf E-Mails).
2. In einem zweiten Terminal die eigentliche Anwendung mit `python app.py` starten.
3. In `config.py` ist bereits `MAIL_SERVER = "127.0.0.1"` und `MAIL_PORT = 1025` eingetragen — das ist genau die Adresse des Fake-Postboten aus Schritt 1.
4. Wird jetzt eine E-Mail ausgelöst (z. B. über die Registrierung), erscheint sie als Text im ersten Terminal-Fenster statt im echten Postfach.

Für den echten Einsatz später müsste `MAIL_SERVER` in `config.py` auf einen echten E-Mail-Anbieter (z. B. den Firmen-Mailserver) umgestellt werden.
