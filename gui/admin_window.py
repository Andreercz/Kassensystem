# src/gui/admin_window.py
import customtkinter as ctk


class AdminWindow(ctk.CTkToplevel):

    def __init__(self, parent, db_queries, on_refresh_callback):
        super().__init__()
        self.db_queries = db_queries
        self.on_refresh_callback = on_refresh_callback
        self.categories = parent.categories

        self.title("SmartPOS - Admin Control Center")
        self.geometry("500x500")  # Leicht erhöht für die Statistik-Anzeige
        self.resizable(False, False)
        self.lift()
        self.attributes("-topmost", True)

        title = ctk.CTkLabel(
            self, text="⚙️ Admin Management", font=("Arial", 22, "bold")
        )
        title.pack(pady=15)

        # Tabs erstellen
        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True, padx=15, pady=10)
        self.tabs.add("➕ Hinzufügen")
        self.tabs.add("🔧 Bearbeiten & Löschen")
        self.tabs.add("📊 Statistiken")  # <-- Der neue Statistik-Tab!

        self._setup_add_tab()
        self._setup_manage_tab()
        self._setup_stats_tab()  # <-- UI für Statistiken aufbauen

    def _setup_add_tab(self):
        tab = self.tabs.tab("➕ Hinzufügen")
        lbl = ctk.CTkLabel(
            tab,
            text="Neues Produkt registrieren",
            font=("Arial", 14, "bold"),
        )
        lbl.pack(pady=10)

        self.entry_name = ctk.CTkEntry(tab, placeholder_text="Name (z.B. Gyoza)")
        self.entry_name.pack(pady=6, padx=30, fill="x")

        self.entry_price = ctk.CTkEntry(
            tab, placeholder_text="Preis in € (z.B. 6.50)"
        )
        self.entry_price.pack(pady=6, padx=30, fill="x")

        lbl_cat = ctk.CTkLabel(tab, text="Kategorie auswählen:")
        lbl_cat.pack(pady=(5, 2))

        self.dropdown_add_cat = ctk.CTkOptionMenu(tab, values=self.categories)
        self.dropdown_add_cat.pack(pady=6, padx=30, fill="x")

        btn_save = ctk.CTkButton(
            tab,
            text="In Datenbank speichern",
            fg_color="#2ecc71",
            hover_color="#27ae60",
            font=("Arial", 13, "bold"),
            command=self._add_item,
        )
        btn_save.pack(pady=15)

    def _setup_manage_tab(self):
        tab = self.tabs.tab("🔧 Bearbeiten & Löschen")
        lbl = ctk.CTkLabel(
            tab, text="Produkt auswählen", font=("Arial", 14, "bold")
        )
        lbl.pack(pady=10)

        self.menu_items = self.db_queries.get_all_menu_items_raw()
        item_names = (
            [item[0] for item in self.menu_items]
            if self.menu_items
            else ["Keine Artikel"]
        )

        self.dropdown_items = ctk.CTkOptionMenu(tab, values=item_names)
        self.dropdown_items.pack(pady=8, padx=30, fill="x")

        self.entry_new_price = ctk.CTkEntry(
            tab, placeholder_text="Neuer Preis in € (z.B. 10.50)"
        )
        self.entry_new_price.pack(pady=8, padx=30, fill="x")

        btn_update = ctk.CTkButton(
            tab,
            text="Preis aktualisieren",
            fg_color="#3498db",
            hover_color="#2980b9",
            command=self._update_price,
        )
        btn_update.pack(pady=10)

        line = ctk.CTkLabel(tab, text="___________________________________")
        line.pack(pady=5)

        btn_delete = ctk.CTkButton(
            tab,
            text="🗑️ Produkt unwiderruflich löschen",
            fg_color="#e74c3c",
            hover_color="#c0392b",
            font=("Arial", 13, "bold"),
            command=self._delete_item,
        )
        btn_delete.pack(pady=15)

    def _setup_stats_tab(self):
        """Baut das Interface für den neuen Statistik-Reiter auf."""
        tab = self.tabs.tab("📊 Statistiken")

        lbl = ctk.CTkLabel(
            tab, text="Finanz- & Produkt-Auswertung", font=("Arial", 14, "bold")
        )
        lbl.pack(pady=10)

        # Container für den Umsatz (schick hervorgehoben)
        self.revenue_frame = ctk.CTkFrame(tab, corner_radius=8, fg_color="#1a252f")
        self.revenue_frame.pack(pady=15, padx=30, fill="x")

        self.lbl_revenue = ctk.CTkLabel(
            self.revenue_frame,
            text="Gesamtumsatz: 0.00 €",
            font=("Arial", 16, "bold"),
            text_color="#2ecc71",
        )
        self.lbl_revenue.pack(pady=15)

        # Bereich für Top-Seller
        lbl_top = ctk.CTkLabel(
            tab, text="Die Top 3 Takumi Bestseller:", font=("Arial", 13, "bold")
        )
        lbl_top.pack(pady=(10, 5))

        # Textbox für die Liste, damit die Formatierung schön untereinander steht
        self.lbl_topsellers = ctk.CTkLabel(
            tab, text="", font=("Courier New", 13), justify="left"
        )
        self.lbl_topsellers.pack(pady=5)

        # Manueller Aktualisieren-Button
        btn_refresh = ctk.CTkButton(
            tab,
            text="🔄 Daten aktualisieren",
            fg_color="#95a5a6",
            hover_color="#7f8c8d",
            command=self._calculate_live_stats,
        )
        btn_refresh.pack(pady=20)

        # Beim ersten Öffnen direkt einmal berechnen
        self._calculate_live_stats()

    def _calculate_live_stats(self):
        """Holt die frischen Berechnungen aus der DB und schreibt sie in die GUI."""
        # Umsatz anzeigen
        revenue = self.db_queries.get_total_revenue()
        self.lbl_revenue.configure(text=f"Gesamtumsatz: {revenue:.2f} €")

        # Top Seller anzeigen
        top_items = self.db_queries.get_top_sellers(limit=3)
        if not top_items:
            self.lbl_topsellers.configure(
                text="Noch keine bezahlten Verkäufe in der DB."
            )
        else:
            text_lines = []
            for idx, (name, qty) in enumerate(top_items, 1):
                text_lines.append(f"{idx}. {name:<26} ({qty}x)")
            self.lbl_topsellers.configure(text="\n".join(text_lines))

    # --- BESTEHENDE LOGIK-FUNKTIONEN ---

    def _add_item(self):
        name = self.entry_name.get().strip()
        price_str = self.entry_price.get().strip()
        category = self.dropdown_add_cat.get()

        if not name or not price_str:
            return

        try:
            price = float(price_str.replace(",", "."))
            if self.db_queries.add_menu_item(name, price, category):
                self._reload_dropdown_data()
                self.on_refresh_callback()
                self.entry_name.delete(0, "end")
                self.entry_price.delete(0, "end")
                self._calculate_live_stats()  # Statistiken auffrischen
        except ValueError:
            print("[GUI] Fehler: Ungültiger Preis.")

    def _update_price(self):
        selected_name = self.dropdown_items.get()
        new_price_str = self.entry_new_price.get().strip()

        if selected_name == "Keine Artikel" or not new_price_str:
            return

        try:
            new_price = float(new_price_str.replace(",", "."))
            if self.db_queries.update_menu_item_price(selected_name, new_price):
                self.on_refresh_callback()
                self.entry_new_price.delete(0, "end")
                self._calculate_live_stats()
        except ValueError:
            print("[GUI] Fehler: Ungültiger Preis.")

    def _delete_item(self):
        selected_name = self.dropdown_items.get()
        if selected_name == "Keine Artikel":
            return

        if self.db_queries.delete_menu_item(selected_name):
            self._reload_dropdown_data()
            self.on_refresh_callback()
            self._calculate_live_stats()

    def _reload_dropdown_data(self):
        self.menu_items = self.db_queries.get_all_menu_items_raw()
        item_names = (
            [item[0] for item in self.menu_items]
            if self.menu_items
            else ["Keine Artikel"]
        )
        self.dropdown_items.configure(values=item_names)
        if item_names:
            self.dropdown_items.set(item_names[0])