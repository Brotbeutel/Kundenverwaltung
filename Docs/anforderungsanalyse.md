Hier ist die strukturierte Anforderungsanalyse aus der Mail der Sportless GmbH:

## Funktionale Anforderungen

**Kundenverwaltung**
- Erfassen von Kundendaten: Name, Vorname, Firma, Anschrift (weitere Felder mit "und so weiter" nur vage angedeutet – hier nachfragen!)
- Anlegen neuer Kundendatensätze
- Bearbeiten (Editieren) bestehender Kundendaten
- Löschen von Kundendatensätzen – **aber:** nur durch Nutzer mit Admin-Rechte (DSGVO-konform)

**Benutzerverwaltung / Login**
- Mitarbeiter müssen sich einloggen können (Authentifizierung)
- Rollenkonzept erforderlich: mind. zwei Rollen – "normaler" Mitarbeiter und Admin
- Admin-Rolle mit erweiterten Rechten (insbesondere Löschrecht)

**E-Mail-Funktion**
- Versand automatisierter E-Mails an Kunden (Details unklar: Anlässe/Trigger, Inhalte, Vorlagen? – Klärungsbedarf)

## Nicht-funktionale Anforderungen

- **Datenschutz/DSGVO-Konformität**: explizit gefordert, insbesondere beim Löschen von Kundendaten
- **Zeitrahmen**: 5 Tage Bearbeitungszeit (sehr knapp bemessen – ggf. kritisch zu hinterfragen)
- **Benutzerfreundlichkeit**: implizit, da Vergleich zum bereits positiv aufgenommenen Kalender-Tool gezogen wird
- **Zugriffskontrolle/Berechtigungskonzept**: unterschiedliche Rechte für Mitarbeiter vs. Admin

## Offene Punkte / Klärungsbedarf (nicht eindeutig aus der Mail ableitbar)

- Welche genauen Datenfelder außer Name, Vorname, Firma, Anschrift sind gewünscht?
- Soll es eine Kundenhistorie/Terminverknüpfung zum bereits vorhandenen Kalender-Tool geben?
- Anlässe und Inhalte der automatisierten E-Mails
- Anzahl der Nutzer/Mitarbeiter, die das System gleichzeitig nutzen sollen
- Technische Rahmenbedingungen (Web-Anwendung? Lokale Installation? Vorhandene Systeme, mit denen integriert werden muss?)
- Budget

**Hinweis:** Der Zeitrahmen von 5 Tagen wirkt für den beschriebenen Funktionsumfang (Login, Rollenkonzept, DSGVO-Löschung, automatisierter Mailversand) sehr ambitioniert – das würde ich in einer Rückfrage an die Kundin ansprechen.

Soll ich daraus ein formales Lastenheft erstellen oder die offenen Punkte in eine Rückfrage-Mail packen?