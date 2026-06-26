# src/database/connection.py
import os
import sqlite3


class DatabaseConnection:

    def __init__(self, db_path="data/smartpos.db"):
        self.db_path = db_path

    def initialize_database(self):
        """Erstellt den Datenordner und initialisiert alle Tabellen."""
        # Erstellt den Ordner 'data', falls er noch fehlt
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            self._create_tables(cursor)
            self._insert_sample_data(cursor)
            conn.commit()
        print("[SUCCESS] Database initialized successfully.")

    def _create_tables(self, cursor):
        """Erstellt alle notwendigen Tabellen für das Takumi POS-System."""
        # 1. Tische
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tables (
                table_number INTEGER PRIMARY KEY
            )
        """)

        # 2. Speisekarte (menu_items)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                price REAL,
                category TEXT
            )
        """)

        # 3. Bestellungen (Bestell-Kopfdaten)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_number INTEGER,
                total_amount REAL DEFAULT 0.0,
                status TEXT DEFAULT 'Open',
                timestamp TEXT,
                FOREIGN KEY (table_number) REFERENCES tables(table_number)
            )
        """)

        # 4. Bestell-Positionen (Die einzelnen Gerichte pro Bestellung)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                item_id INTEGER,
                quantity INTEGER DEFAULT 1,
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                FOREIGN KEY (item_id) REFERENCES menu_items(id)
            )
        """)

        # 5. Mitarbeiter-Logins (User-Tabelle)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT
            )
        """)

    def _insert_sample_data(self, cursor):
        """Trägt die offiziellen Takumi-Kategorien und die Benutzer-Logins ein."""
        # Tische eintragen
        cursor.execute("SELECT COUNT(*) FROM tables")
        if cursor.fetchone()[0] == 0:
            tables = [(1,), (2,), (3,), (4,), (5,), (6,)]
            cursor.executemany(
                "INSERT INTO tables (table_number) VALUES (?)", tables
            )
        #----------------------
        # Speisekarte befüllen
        #----------------------

        cursor.execute("SELECT COUNT(*) FROM menu_items")
        if cursor.fetchone()[0] == 0:
            items = [

                # Ramen
                ("1 Shio Ramen", 11.80, "Ramen"),
                ("2 Shoyu Ramen", 11.80, "Ramen"),
                ("3 Miso Ramen", 12.80, "Ramen"),
                ("4 Shio Ramen", 14.80, "Ramen"),
                ("5 Shoyu Ramen", 14.80, "Ramen"),
                ("6 Miso Ramen", 15.80, "Ramen"),
                ("7 Traditionelle Tokyo Shoyu Ramen", 14.80, "Ramen"),
                ("11 Surf & Turf Takumi Style Ramen", 18.80, "Ramen"),
                ("11A Ebi Tako Tan Tan Men", 18.80, "Ramen"),
                ("12 Karaage Tan Tan Men", 17.80, "Ramen"),
                ("13 Tan Tan Men", 15.80, "Ramen"),
                ("13A Gyoza & Karaage Miso Ramen", 17.80, "Ramen"),
                ("14 Karaage Miso Ramen", 16.80, "Ramen"),
                ("15 Teriyaki Miso Ramen", 16.80, "Ramen"),
                ("16 Vegi Miso Ramen", 17.80, "Ramen"),
                ("16a Vegi Miso Ramen", 19.80, "Ramen"),
                ("17 Vegi Miso Ramen", 15.80, "Ramen"),
                ("17A Spezial Vegan Creamy Potage Ramen", 19.80, "Ramen"),
                ("18 Oro-Chon Ramen", 14.80, "Ramen"),

                # Takumi Special Ramen
                ("20 Spezielle Ramen Shoyu", 17.80, "Takumi Special Ramen"),
                ("21 Spezielle Ramen Miso", 18.80, "Takumi Special Ramen"),
                ("22 Spezielle Ramen Spicy Curry", 18.80, "Takumi Special Ramen"),

                # Vorspeisen
                ("59 Veggie Gyoza", 5.80, "Vorspeisen"),
                ("60 Gyoza", 5.50, "Vorspeisen"),
                ("61 Karaage (5stk)", 7.00, "Vorspeisen"),
                ("62 Karaage (10stk)", 7.50, "Vorspeisen"),
                ("63 Takoyaki", 5.80, "Vorspeisen"),
                ("64 Toriteri (Half)", 7.00, "Vorspeisen"),
                ("640  Karaage (Full)", 13.00, "Vorspeisen"),
                ("65 Jumbo Garnelen", 6.70, "Vorspeisen"),
                ("66 Kimchi", 4.20, "Vorspeisen"),
                ("67 Gekochte Sojabohnen", 4.20, "Vorspeisen"),
                ("68 Buta Karubi Don", 8.30, "Vorspeisen"),
                ("68A Gurken leichtscharf", 4.20, "Vorspeisen"),
                ("69 Karaage Don", 8.30, "Vorspeisen"),
                ("70 Gyoza Karaage Don", 8.30, "Vorspeisen"),
                ("71 Teriyaki Don", 8.30, "Vorspeisen"),
                ("72 Veggie Kakiage Don", 7.80, "Vorspeisen"),
                ("73 Seetang-Salat", 4.20, "Vorspeisen"),
                ("74 Gyoza & Karaage Teishoko", 15.80, "Vorspeisen"),
                ("75 Vegan Tofu & Gyoza Don", 8.30, "Vorspeisen"),

                # Nachspeisen
                ("76 Grüntee Eis", 3.50, "Nachspeisen"),
                ("77 Yuzu Sherbet  Eis", 3.80, "Nachspeisen"),
                ("78 Sesam Eis", 3.50, "Nachspeisen"),

                # Alkoholfreie getränke
                ("82 Warmer Grüner Tee", 2.50, "Alkoholfreie Getränke"),
                ("83 Wasser", 2.50, "Alkoholfreie Getränke"),
                ("85 Apfelsaft", 3.00, "Alkoholfreie Getränke"),
                ("87 Coca-Cola", 3.50, "Alkoholfreie Getränke"),
                ("90 Wasser mit Kohlensäure", 2.50, "Alkoholfreie Getränke"),
                ("90 Apfelschorle", 3.20, "Alkoholfreie Getränke"),
                ("93 Coca-Cola Zero", 3.20, "Alkoholfreie Getränke"),
                ("94 Ramune Japan Limonade", 4.20, "Alkoholfreie Getränke"),
                ("97 Hausgemachter Eistee", 4.50, "Alkoholfreie Getränke"),

                # Alkoholische Getränke
                ("80 Kirin BEER vom Fass", 4.20, "Alkoholische Getränke"),
                ("86 Gaffel Kölsch", 3.50, "Alkoholische Getränke"),
                ("91 One Cup", 5.40, "Alkoholische Getränke"),
                ("Kirin BEER 4er Angebot", 12.80, "Alkoholische Getränke"),

                # Premium Sake
                ("Amabuki Marigold Sake Cup 180ml", 10.80, "Premium Sake"),
                ("Toko PURE RICE Junmai 180ml", 10.80, "Premium Sake"),
                ("Dassai 300ml", 28.00, "Premium Sake"),
                ("Dassai 720ml", 59.00, "Premium Sake"),

                # Wein
                ("GRAUBURGUNDER trocken 2019", 14.80, "Wein"),
                ("SILVANER 2020", 19.80, "Wein"),
                ("CHARDONNAY trocken 2020", 14.80, "Wein"),
                ("RIESLING Elegance trocken 2019", 19.80, "Wein"),
                ("WEISBURGUNDER König trocken 2019", 25.80, "Wein"),


                #Cupnudeln
                ("Takumi Cupnudeln", 3.50, "Cupnudeln"),

                #Merchandise
                ("Takumi Team Shirt (L)", 29.00, "Merchandise"),
            ]
            cursor.executemany(
                "INSERT INTO menu_items (name, price, category) VALUES (?, ?, ?)",
                items,
            )

        #---------------------------
        # Benutzer-Accounts anlegen
        #---------------------------

        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            users = [
                ("admin", "admin123", "Admin"),
                ("kellner1", "takumi1", "Waiter"),
                ("kellner2", "takumi2", "Waiter"),
            ]
            cursor.executemany(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                users,
            )