# Kundenverwaltungssystem – Sportless GmbH

Digitale Verwaltung von Kundendaten für die Sportless GmbH als Ablösung der bisherigen papierbasierten Kundenlisten. Ergänzt das bereits bestehende Kalender-Tool der Abteilung.

## Projektbeschreibung

Aktuell werden Kundeninformationen handschriftlich in Blöcken und Büchern erfasst. Dieses Projekt digitalisiert die Kundenverwaltung und bietet zusätzlich die Möglichkeit, automatisierte E-Mails an Kunden zu versenden.

## Funktionen

- **Kundenverwaltung**: Anlegen, Anzeigen und Bearbeiten von Kundendatensätzen (Name, Vorname, Firma, Anschrift u. a.)
- **Login-System**: Authentifizierung für Mitarbeiter*innen
- **Rollenkonzept**:
  - *Mitarbeiter*: Kundendaten anlegen und bearbeiten
  - *Admin*: zusätzlich berechtigt, Kundendaten DSGVO-konform zu löschen
- **Automatisierter E-Mail-Versand**: E-Mails werden mit Kontaktdaten aus der Datenbank automatisch befüllt und verschickt

## Technologie-Stack

> Platzhalter – bitte an das tatsächlich gewählte Setup anpassen.

- **Datenbank**: SQL (z. B. MySQL/PostgreSQL)
- **Backend**: _TBD_
- **Frontend**: _TBD_
- **E-Mail-Versand**: SMTP über kostenlosen Anbieter mit Freikontingent (z. B. Brevo)

## Installation

```bash
# Repository klonen
git clone <repo-url>
cd <projektordner>

# Abhängigkeiten installieren
_TBD_

# Datenbank einrichten
_TBD_

# Umgebungsvariablen konfigurieren (siehe .env.example)
_TBD_

# Anwendung starten
_TBD_
```

## Konfiguration

Folgende Umgebungsvariablen werden benötigt (Beispiel):

```
DB_HOST=
DB_USER=
DB_PASSWORD=
DB_NAME=
SMTP_HOST=
SMTP_PORT=
SMTP_USER=
SMTP_PASSWORD=
```

## Berechtigungen & DSGVO

- Nur Nutzer mit der Rolle **Admin** dürfen Kundendaten löschen.
- Vor dem produktiven Einsatz des E-Mail-Versands muss die Einwilligung der Kunden zum automatisierten Mailkontakt vorliegen.
- Für den genutzten E-Mail-Dienstleister ist ein Auftragsverarbeitungsvertrag (AVV) abzuschließen.
- SPF/DKIM/DMARC sollten für die Versanddomain korrekt eingerichtet sein, um Zustellprobleme zu vermeiden.

## Offene Punkte

- Vollständige Liste der zu erfassenden Kundenfelder
- Anlässe/Trigger für automatisierte E-Mails sowie Inhalte der Vorlagen
- Technische Rahmenbedingungen (Hosting, vorhandene Infrastruktur)
- Anzahl gleichzeitiger Nutzer

## Projektstatus

In Entwicklung.

## Kontakt

Sportless GmbH, Abentheuer
