# 🍜 SmartPOS - Takumi Edition

Ein modernes, relationales Kassensystem (Point of Sale) für die Gastronomie, maßgeschneidert für das Menü und die Arbeitsabläufe des Restaurants **Takumi**. Entwickelt als eigenständige Desktop-Anwendung in Python mit einer modernen, hardwarebeschleunigten Benutzeroberfläche (`CustomTkinter`) und einer relationalen SQLite3-Datenbank.

---

## 📊 Kernfeatures auf Enterprise-Level

Das System wurde für den produktiven Einsatz im Restaurantbetrieb optimiert und umfasst folgende Software-Konzepte:

1. **Sicheres In-Window Login-System:**
   * Zentraler Anmeldebildschirm direkt beim App-Start ohne störendes Fenster-Flackern.
   * Rollenbasierte Rechteverteilung (RBAC): Mitarbeiter loggen sich entweder als *Waiter* (Kellner) oder *Admin* (Chef) ein.

2. **Dynamische UI-Rechteverwaltung:**
   * Der Zugriff auf sensible Umsatzdaten und die Speisekarten-Verwaltung (`⚙️ Global Admin Settings`) wird für Kellner komplett ausgeblendet und gesperrt. Nur Admins besitzen vollen Zugriff.

3. **Interaktive Tisch- & Bestellverwaltung:**
   * Visuelle Übersicht über 6 Restaurant-Tische mit automatischer Farbcodierung (Grün = Frei, Rot = Besetzt).
   * Zweistufige Speisekarten-Navigation mit 10 originalen Takumi-Kategorien (Ramen, Specials, Drinks, Merchandise etc.).

4. **Live-Belegungs-Timer (Gastro-Uhrwerk):**
   * Besetzte Tische berechnen im Hintergrund automatisch alle 10 Sekunden live ihre aktive Verweildauer basierend auf dem DB-Zeitstempel und zeigen diese direkt auf dem Tisch-Button an (z. B. `Table 3 (14 Min. aktiv)`).

5. **Echtzeit-Datenanalyse (Admin Dashboard):**
   * Automatische Auswertung des exakten Live-Gesamtumsatzes über SQL-Aggregatfunktionen (`SUM`).
   * Dynamische Rangliste der Top-3-Bestseller (meistverkaufte Gerichte) mittels Tabellen-Joins und Gruppierung (`COUNT`, `GROUP BY`, `ORDER BY DESC`).

6. **Echtes Fehlermanagement (Storno-Funktion):**
   * Ein intelligenter Rückgängig-Button (`Letzten Artikel stornieren`) erlaubt es Kellnern, Tippfehler sofort zeilenweise aus der DB und dem RAM-Speicher zu entfernen. Leere Tische springen automatisch in den Freigabemodus (Grün) zurück.

7. **Bondrucker-Simulation (Datei-Export):**
   * Beim Abschließen des Bezahlvorgangs (`Proceed to Payment`) generiert die App eine perfekt formatierte Textdatei (`.txt`) im Archivordner `rechnungen` inklusive sekundengenauem Zeitstempel für die Buchhaltung.

---

## 📂 Projektstruktur & Architektur

Das Projekt folgt einer sauberen Schichtenarchitektur (Separation of Concerns), um Wartbarkeit und Erweiterbarkeit zu garantieren:

```text
Takumi/
│
├── main.py                  # Zentraler Startpunkt der Applikation
├── .gitignore               # Filtert temporäre Dateien für Git/GitHub heraus
├── README.md                # Projektdokumentation und Bedienungsanleitung
│
├── database/                # Datenhaltungs-Schicht (Backend)
│   ├── connection.py        # DB-Initialisierung, Tabellen-Setup & Seed-Daten
│   └── queries.py           # SQL-Logik (CRUD, Storno, Umsatz-Berechnungen, Login)
│
├── gui/                     # Präsentations-Schicht (Frontend)
│   ├── main_window.py       # Hauptkasse, Login-Maske, Warenkorb & Live-Timer
│   └── admin_window.py      # Admin-Zentrale mit CRUD-Tabs und SQL-Statistiken
│
├── data/                    # Speicherverzeichnis der relationalen DB
│   └── smartpos.db          # SQLite3 Datenbankdatei (wird automatisch generiert)
│
└── rechnungen/              # Rechnungsarchiv (Exportierte Belege)
    └── rechnung_tisch_*.txt # Generierte Kassenbons


Technische Voraussetzungen & Installation
Voraussetzungen
Betriebssystem: macOS (optimiert), Windows oder Linux
Python-Version: Python 3.11 oder neuer
Datenbank: SQLite3 (standardmäßig in Python integriert)

Installation der Abhängigkeiten
Die App nutzt die moderne GUI-Bibliothek CustomTkinter. Öffnen Sie das Terminal im Projektverzeichnis und installieren Sie die Bibliothek mit folgendem Befehl:
Bash
pip install customtkinter

Programm starten
Führen Sie die Hauptdatei aus, um das Kassen-Login zu starten:
Bash
python main.py


Standard-Testzugänge
Für die Überprüfung der rollenbasierten Ansichten sind folgende Accounts in den Beispieldaten hinterlegt:

Administrator-Konto (Voller Zugriff + Statistiken):
Benutzername: admin
Passwort: admin123

Kellner-Konto (Nur Kassenbetrieb, Admin-Button gesperrt):
Benutzername: kellner1
Passwort: takumi1
