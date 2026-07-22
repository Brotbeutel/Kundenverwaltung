# Projektplan: Kundenverwaltungssystem für Sportless GmbH

## 1. Projektübersicht

| Punkt | Details |
|---|---|
| **Auftraggeber** | Sportless GmbH, Frau Anette Ganz |
| **Projektname** | Kundenverwaltung (digitale Kundendatenbank) |
| **Frist** | **5 Arbeitstage (hart, nicht verhandelbar)** |
| **Ziel** | Ablösung der papierbasierten Kundenverwaltung durch ein digitales, rollenbasiertes System mit E-Mail-Funktion |

## 2. Technologie-Stack (Begründung)

Für ein MVP in 5 Tagen wird bewusst auf minimalen Overhead gesetzt – kein Build-Prozess, keine Microservices, ein einziges deploybares Artefakt:

| Bereich | Technologie | Begründung |
|---|---|---|
| Backend | **Python + Flask** | Sehr schneller Projektstart, kaum Boilerplate im Vergleich zu Django |
| Datenbank | **SQLite + SQLAlchemy (ORM)** | Keine separate DB-Server-Installation nötig, reicht für MVP völlig aus |
| Authentifizierung | **Flask-Login + Werkzeug (Passwort-Hashing)** | Etablierte, gut dokumentierte Lösung, wenig Eigenentwicklung nötig |
| Frontend | **Jinja2-Templates + Tailwind CSS (via CDN)** | Kein Frontend-Build-Tool nötig, dennoch modernes UI möglich |
| E-Mail-Versand | **Flask-Mail (SMTP)** | Standardlösung, einfache Integration von Vorlagen |
| Versionierung | **Git** | Nachvollziehbarkeit, Absicherung des Fortschritts |

## 3. Tagesplan

### 📅 Tag 1 – Setup, Anforderungen & Datenmodell
**Tagesziel:** Projektgrundlage steht, Datenmodell und Rollenkonzept sind final definiert.

| Aufgabe | Zeitaufwand |
|---|---|
| Anforderungen aus Anschreiben schriftlich fixieren (Scope einfrieren) | 1 h |
| Projektstruktur aufsetzen (Flask, virtuelle Umgebung, Ordnerstruktur) | 1 h |
| Git-Repository initialisieren | 0,5 h |
| Datenbankschema entwerfen (Kunde: Name, Vorname, Firma, Anschrift, Kontaktdaten) | 1,5 h |
| Mitarbeiter-Modell mit Rollen (Mitarbeiter / Admin) entwerfen | 1,5 h |
| SQLite-DB + Modelle via SQLAlchemy implementieren | 1,5 h |
| **Summe** | **7 h** |

### 📅 Tag 2 – Login & Rechteverwaltung
**Tagesziel:** Mitarbeiter können sich sicher einloggen; Rollen steuern den Zugriff.

| Aufgabe | Zeitaufwand |
|---|---|
| Login/Logout mit Flask-Login implementieren | 2 h |
| Passwort-Hashing einrichten | 1 h |
| Rollenbasierte Zugriffskontrolle (z. B. `@admin_required`-Decorator) | 2 h |
| Mitarbeiterkonten anlegen (Seed-Daten für Test) | 1 h |
| Session-Handling testen | 1 h |
| **Summe** | **7 h** |

### 📅 Tag 3 – Kundenverwaltung (CRUD)
**Tagesziel:** Kundendaten können vollständig verwaltet werden, Löschen ist Admin-exklusiv.

| Aufgabe | Zeitaufwand |
|---|---|
| Formular „Kunde anlegen" inkl. Validierung | 2 h |
| Kundenliste + Detailansicht + Such-/Filterfunktion | 2 h |
| Kunde bearbeiten | 1,5 h |
| Kunde löschen – **nur für Admin-Rolle**, mit DSGVO-Bestätigungsdialog | 1,5 h |
| **Summe** | **7 h** |

### 📅 Tag 4 – E-Mail-Modul & UI-Feinschliff
**Tagesziel:** Automatisierte E-Mails funktionieren, Oberfläche ist präsentabel.

| Aufgabe | Zeitaufwand |
|---|---|
| SMTP-Konfiguration / Flask-Mail einrichten | 2 h |
| E-Mail-Vorlagen erstellen (z. B. Begrüßung, Bestätigung) | 1,5 h |
| Trigger für automatisierten Versand (z. B. bei Kundenanlage) | 1,5 h |
| UI mit Tailwind CSS verschönern, responsives Grundlayout | 2 h |
| **Summe** | **7 h** |

### 📅 Tag 5 – Test, Dokumentation & Übergabe
**Tagesziel:** System ist stabil, dokumentiert und übergabefertig.

| Aufgabe | Zeitaufwand |
|---|---|
| Manuelle Tests aller CRUD- und Login-Abläufe | 2 h |
| Bugfixing | 2 h |
| Kurzanleitung für Mitarbeiter (inkl. Screenshots) | 1,5 h |
| Deployment/Bereitstellung + Vorbereitung der Abnahme-Demo | 1,5 h |
| **Summe** | **7 h** |

**Gesamtaufwand:** ca. 35 Stunden über 5 Tage (≈ 7 h/Tag)

## 4. Risikoanalyse

| # | Risiko | Auswirkung | Mitigierung |
|---|---|---|---|
| 1 | **DSGVO-konforme Löschung wird unterschätzt** – Sonderregeln (nur Admin, Nachweispflicht) benötigen mehr Zeit als geplant | Verzögerung an Tag 3 | Löschkonzept bereits an Tag 1 klar definieren (Soft-Delete + Admin-Hard-Delete), keine Feinheiten erst am Ende klären |
| 2 | **E-Mail-Versand funktioniert nicht wie erwartet** (fehlende SMTP-Zugangsdaten, Spam-Filter, Firewall) | Feature an Tag 4 nicht testbar/lieferbar | Frühzeitig Test-SMTP-Dienst (z. B. Mailtrap) nutzen; Fallback: E-Mails zunächst nur protokollieren statt real versenden |
| 3 | **Scope Creep** – die Chefin der Kundin äußert während der Woche neue Wünsche (siehe Anschreiben: Unsicherheit über den tatsächlichen Bedarf) | Zeitplan komplett gefährdet | Angebot/Anforderungen schriftlich fixieren, weitere Wünsche explizit auf „Phase 2" nach MVP-Abgabe verschieben |
| 4 | **Fehler im Rollenmodell** führen zu Sicherheitslücke (z. B. normale Mitarbeiter können löschen) | Compliance-Verstoß, Vertrauensverlust beim Kunden | Zugriffsrechte durch zentrale Decorators/Middleware statt Einzelprüfungen umsetzen; gezielte Tests der Rechteprüfung an Tag 2 und Tag 5 |

## 5. Hinweis
Der Zeitplan ist bewusst eng kalkuliert (kein Puffer). Sollte an einem Tag ein Blocker aus der Risikoanalyse eintreten, verschiebt sich der Puffer auf Kosten des UI-Feinschliffs (Tag 4), da dieser das am wenigsten kritische Element für die Funktionsfähigkeit ist.
