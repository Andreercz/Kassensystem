# src/database/queries.py
import sqlite3


class DatabaseQueries:

    def __init__(self, db_path):
        self.db_path = db_path

    def check_login(self, username, password):
        """Überprüft die Logindaten der Mitarbeiter in der DB."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT role FROM users WHERE username = ? AND password = ?",
                    (username, password),
                )
                row = cursor.fetchone()
                return row[0] if row else None
        except sqlite3.Error as e:
            print(f"[ERROR] check_login fehlgeschlagen: {e}")
            return None

    def load_active_orders(self):
        """Lädt alle noch offenen Bestellungen gruppiert nach Tischnummer."""
        orders_dict = {i: [] for i in range(1, 7)}
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # FEHLER BEHOBEN: o.table_number statt o.table_id verwendet!
                cursor.execute("""
                    SELECT o.table_number, m.name, m.price
                    FROM orders o
                    JOIN order_items oi ON o.id = oi.order_id
                    JOIN menu_items m ON oi.item_id = m.id
                    WHERE o.status = 'Open'
                """)
                for row in cursor.fetchall():
                    t_num, name, price = row
                    orders_dict[t_num].append({"name": name, "price": price})
        except sqlite3.Error as e:
            print(f"[DIAGNOSE ERROR] load_active_orders fehlgeschlagen: {e}")
        return orders_dict

    def get_menu_items_by_category(self, category):
        """Holt alle Produkte einer bestimmten Kategorie."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name, price FROM menu_items WHERE category = ?",
                    (category,),
                )
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"[ERROR] get_menu_items_by_category fehlgeschlagen: {e}")
            return []

    def add_item_to_order(self, table_number, item_name):
        """Fügt einer offenen (oder neuen) Bestellung ein Gericht hinzu."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 1. Offene Bestellung suchen
                cursor.execute(
                    "SELECT id FROM orders WHERE table_number = ? AND status = 'Open'",
                    (table_number,),
                )
                row = cursor.fetchone()

                if row:
                    order_id = row[0]
                else:
                    from datetime import datetime

                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute(
                        "INSERT INTO orders (table_number, status, timestamp) VALUES (?, 'Open', ?)",
                        (table_number, now),
                    )
                    order_id = cursor.lastrowid

                # 2. Item-ID & Preis holen
                cursor.execute(
                    "SELECT id, price FROM menu_items WHERE name = ?",
                    (item_name,),
                )
                item_row = cursor.fetchone()
                if not item_row:
                    return False
                item_id, price = item_row

                # 3. Position speichern
                cursor.execute(
                    "INSERT INTO order_items (order_id, item_id, quantity) VALUES (?, ?, 1)",
                    (order_id, item_id),
                )

                # 4. Gesamtsumme aktualisieren
                cursor.execute(
                    "UPDATE orders SET total_amount = total_amount + ? WHERE id = ?",
                    (price, order_id),
                )
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"[ERROR] add_item_to_order fehlgeschlagen: {e}")
            return False

    def settle_open_order(self, table_number):
        """Schließt eine Bestellung ab (wird beim Bezahlen auf 'Paid' gesetzt)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE orders SET status = 'Paid' WHERE table_number = ? AND status = 'Open'",
                    (table_number,),
                )
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"[ERROR] settle_open_order fehlgeschlagen: {e}")
            return False

    def get_all_menu_items_raw(self):
        """Holt die komplette Speisekarte für das Admin-Dropdown."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name, price, category FROM menu_items ORDER BY name ASC"
                )
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[ERROR] get_all_menu_items_raw fehlgeschlagen: {e}")
            return []

    def add_menu_item(self, name, price, category):
        """Erstellt ein neues Produkt."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO menu_items (name, price, category) VALUES (?, ?, ?)",
                    (name, price, category),
                )
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"[ERROR] add_menu_item fehlgeschlagen: {e}")
            return False

    def update_menu_item_price(self, name, new_price):
        """Ändert den Preis eines Artikels."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE menu_items SET price = ? WHERE name = ?",
                    (new_price, name),
                )
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"[ERROR] update_menu_item_price fehlgeschlagen: {e}")
            return False

    def delete_menu_item(self, name):
        """Löscht ein Produkt vollständig."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM menu_items WHERE name = ?", (name,))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"[ERROR] delete_menu_item fehlgeschlagen: {e}")
            return []

    def get_total_revenue(self):
        """Berechnet den Gesamtumsatz der bezahlten Bestellungen."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT SUM(total_amount) FROM orders WHERE status = 'Paid'"
                )
                row = cursor.fetchone()
                return row[0] if row[0] is not None else 0.0
        except sqlite3.Error as e:
            print(f"[ERROR] get_total_revenue fehlgeschlagen: {e}")
            return 0.0

    def get_top_sellers(self, limit=3):
        """Ermittelt die am häufigsten verkauften Produkte."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT m.name, SUM(oi.quantity) as total_qty
                    FROM order_items oi
                    JOIN menu_items m ON oi.item_id = m.id
                    JOIN orders o ON oi.order_id = o.id
                    WHERE o.status = 'Paid'
                    GROUP BY m.name
                    ORDER BY total_qty DESC
                    LIMIT ?
                """,
                    (limit,),
                )
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[ERROR] get_top_sellers fehlgeschlagen: {e}")
            return []

    def cancel_last_item(self, table_number) -> bool:
        """Sucht den am neuesten hinzugefügten Artikel eines offenen Tisches und löscht ihn."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 1. Die ID der aktuell offenen Bestellung holen
                cursor.execute("SELECT id FROM orders WHERE table_number = ? AND status = 'Open'", (table_number,))
                row = cursor.fetchone()
                if not row:
                    return False
                order_id = row[0]

                # 2. Den neuesten Eintrag (höchste ID) aus order_items für diese Bestellung finden
                cursor.execute("""
                               SELECT oi.id, m.price
                               FROM order_items oi
                                        JOIN menu_items m ON oi.item_id = m.id
                               WHERE oi.order_id = ?
                               ORDER BY oi.id DESC LIMIT 1
                               """, (order_id,))
                item_row = cursor.fetchone()

                if not item_row:
                    return False
                oi_id, price = item_row

                # 3. Diese eine Position unwiderruflich löschen
                cursor.execute("DELETE FROM order_items WHERE id = ?", (oi_id,))

                # 4. Die Gesamtsumme der Bestellung in der DB korrigieren (darf nicht unter 0 fallen)
                cursor.execute("UPDATE orders SET total_amount = MAX(0.0, total_amount - ?) WHERE id = ?",
                               (price, order_id))

                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"[ERROR] Stornieren in DB fehlgeschlagen: {e}")
            return False

    def get_table_timestamp(self, table_number) -> str:
        """Holt den originalen Start-Zeitstempel einer offenen Tisch-Bestellung."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT timestamp FROM orders WHERE table_number = ? AND status = 'Open'",
                               (table_number,))
                row = cursor.fetchone()
                return row[0] if row else None
        except sqlite3.Error as e:
            print(f"[ERROR] get_table_timestamp fehlgeschlagen: {e}")
            return None