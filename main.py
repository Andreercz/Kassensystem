# main.py
from database.connection import DatabaseConnection
from database.queries import DatabaseQueries
from gui.main_window import MainWindow

if __name__ == "__main__":
    # 1. Datenbank initialisieren (erstellt Tabellen & füllt Beispieldaten)
    db_conn = DatabaseConnection()
    db_conn.initialize_database()

    # 2. SQL-Abfrage-Schnittstelle laden
    queries = DatabaseQueries(db_conn.db_path)

    # 3. Hauptanwendung direkt starten
    print("STARTE SOFTWARE...")
    app = MainWindow(queries)
    app.mainloop()