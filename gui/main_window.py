# src/gui/main_window.py
import customtkinter as ctk
from datetime import datetime


class MainWindow(ctk.CTk):

    def __init__(self, db_queries):
        super().__init__()
        self.db_queries = db_queries
        self.user_role = None

        self.categories = [
            "Ramen",
            "Takumi Special Ramen",
            "Vorspeisen",
            "Nachspeisen",
            "Alkoholische Getränke",
            "Alkoholfreie Getränke",
            "Premium Sake",
            "Wein",
            "Cupnudeln",
            "Merchandise",
        ]

        self.active_orders = self.db_queries.load_active_orders()
        self.current_table = None
        self.table_buttons = {}
        self.admin_window = None

        self.title("SmartPOS - Takumi Edition")
        self.geometry("1350x780")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self._show_login_screen()

    def _show_login_screen(self):
        self.login_frame = ctk.CTkFrame(
            self, corner_radius=15, width=400, height=350
        )
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.login_frame.pack_propagate(False)

        title = ctk.CTkLabel(
            self.login_frame,
            text="🍜 Takumi SmartPOS\nAnmeldung",
            font=("Arial", 22, "bold"),
        )
        title.pack(pady=30)

        self.entry_user = ctk.CTkEntry(
            self.login_frame,
            placeholder_text="Benutzername",
            width=280,
            height=35,
        )
        self.entry_user.pack(pady=10)

        self.entry_pass = ctk.CTkEntry(
            self.login_frame, placeholder_text="Passwort", show="*", width=280, height=35
        )
        self.entry_pass.pack(pady=10)

        self.lbl_error = ctk.CTkLabel(
            self.login_frame, text="", text_color="#e74c3c", font=("Arial", 13)
        )
        self.lbl_error.pack(pady=5)

        btn_login = ctk.CTkButton(
            self.login_frame,
            text="Einloggen",
            width=280,
            height=40,
            font=("Arial", 14, "bold"),
            fg_color="#3498db",
            command=self._try_login,
        )
        btn_login.pack(pady=15)

    def _try_login(self):
        user = self.entry_user.get().strip()
        pas = self.entry_pass.get().strip()

        role = self.db_queries.check_login(user, pas)
        if role:
            self.user_role = role
            self.login_frame.destroy()
            self.title(f"SmartPOS - Takumi Edition (User: {self.user_role})")
            self._setup_pos_interface()
        else:
            self.lbl_error.configure(text="Ungültige Anmeldedaten!")

    def _setup_pos_interface(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._create_left_sidebar()
        self._create_menu_frame()
        self._create_cart_frame()

        # STARTET DEN LIVE-TIMER-LOOP (Tickt ab jetzt im Hintergrund)
        self._refresh_live_timers()

    def _create_left_sidebar(self):
        sidebar_frame = ctk.CTkFrame(self, fg_color="transparent")
        sidebar_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        table_frame = ctk.CTkFrame(sidebar_frame, corner_radius=10)
        table_frame.pack(fill="both", expand=True, pady=(0, 15))

        title = ctk.CTkLabel(
            table_frame, text="Restaurant Tables", font=("Arial", 20, "bold")
        )
        title.pack(pady=15)

        for tn in range(1, 7):
            table_button = ctk.CTkButton(
                table_frame,
                text=f"Table {tn}\n(Wird geladen...)",
                font=("Arial", 14),
                height=55,
                command=lambda t=tn: self._select_table(t),
            )
            table_button.pack(pady=8, padx=20, fill="x")
            self.table_buttons[tn] = table_button

        if self.user_role == "Admin":
            admin_frame = ctk.CTkFrame(sidebar_frame, corner_radius=10, height=80)
            admin_frame.pack(fill="x")
            admin_frame.pack_propagate(False)

            admin_button = ctk.CTkButton(
                admin_frame,
                text="⚙️ Global Admin Settings",
                font=("Arial", 14, "bold"),
                fg_color="#7f8c8d",
                hover_color="#95a5a6",
                height=45,
                command=self._open_admin_dashboard,
            )
            admin_button.pack(pady=17, padx=20, fill="x")

    # --- NEU: DIE AUTOMATISCHE ZEITBERECHNUNGS-SCHLEIFE ---
    def _refresh_live_timers(self):
        """Berechnet alle 10 Sekunden live die Belegungsdauer besetzter Tische."""
        for tn in range(1, 7):
            has_items = len(self.active_orders.get(tn, [])) > 0

            if has_items:
                ts_str = self.db_queries.get_table_timestamp(tn)
                if ts_str:
                    try:
                        # Berechne Differenz zwischen Jetzt und Start-Zeitstempel
                        start_time = datetime.strptime(
                            ts_str, "%Y-%m-%d %H:%M:%S"
                        )
                        diff = datetime.now() - start_time
                        minutes = int(diff.total_seconds() // 60)

                        self.table_buttons[tn].configure(
                            fg_color="#e74c3c",
                            text=f"Table {tn}\n({minutes} Min. aktiv)",
                        )
                    except Exception:
                        self.table_buttons[tn].configure(
                            fg_color="#e74c3c", text=f"Table {tn}\n(Occupied)"
                        )
                else:
                    self.table_buttons[tn].configure(
                        fg_color="#e74c3c", text=f"Table {tn}\n(Occupied)"
                    )
            else:
                self.table_buttons[tn].configure(
                    fg_color="#2ecc71", text=f"Table {tn}\n(Free)"
                )

        # Triggert sich selbst in 10.000 Millisekunden (10 Sek) neu
        self.after(10000, self._refresh_live_timers)

    def _create_menu_frame(self):
        if not hasattr(self, "_menu_frame_widget"):
            self._menu_frame_widget = ctk.CTkFrame(self, corner_radius=10)
            self._menu_frame_widget.grid(
                row=0, column=1, padx=15, pady=15, sticky="nsew"
            )

            title = ctk.CTkLabel(
                self._menu_frame_widget,
                text="Menu Selection",
                font=("Arial", 20, "bold"),
            )
            title.pack(pady=15)

            self.menu_container = ctk.CTkFrame(
                self._menu_frame_widget, fg_color="transparent"
            )
            self.menu_container.pack(
                fill="both", expand=True, padx=10, pady=10
            )

            self.menu_container.grid_columnconfigure(0, weight=1)
            self.menu_container.grid_columnconfigure(1, weight=2)
            self.menu_container.grid_rowconfigure(0, weight=1)

            self.category_sidebar = ctk.CTkFrame(
                self.menu_container, corner_radius=8, fg_color="#212f3d"
            )
            self.category_sidebar.grid(
                row=0, column=0, padx=(0, 10), pady=5, sticky="nsew"
            )

            self.items_scrollframe = ctk.CTkScrollableFrame(
                self.menu_container, corner_radius=8
            )
            self.items_scrollframe.grid(row=0, column=1, pady=5, sticky="nsew")

            self.selected_category = self.categories[0]
            self.category_buttons = {}

            for cat in self.categories:
                cat_btn = ctk.CTkButton(
                    self.category_sidebar,
                    text=f"  {cat}",
                    font=("Arial", 12, "bold"),
                    height=42,
                    anchor="w",
                    fg_color="#34495e",
                    hover_color="#1abc9c",
                    command=lambda c=cat: self._select_category(c),
                )
                cat_btn.pack(pady=4, padx=8, fill="x")
                self.category_buttons[cat] = cat_btn

        self._display_category_items()

    def _select_category(self, category_name):
        self.selected_category = category_name
        self._display_category_items()

    def _display_category_items(self):
        for widget in self.items_scrollframe.winfo_children():
            widget.destroy()

        for cat, btn in self.category_buttons.items():
            if cat == self.selected_category:
                btn.configure(fg_color="#1abc9c")
            else:
                btn.configure(fg_color="#34495e")

        items = self.db_queries.get_menu_items_by_category(
            self.selected_category
        )

        if not items:
            lbl_empty = ctk.CTkLabel(
                self.items_scrollframe,
                text="Keine Artikel in dieser Kategorie.",
                font=("Arial", 13, "italic"),
            )
            lbl_empty.pack(pady=30)
            return

        for item in items:
            item_text = f"{item['name']}\n{item['price']:.2f} €"
            item_button = ctk.CTkButton(
                self.items_scrollframe,
                text=item_text,
                font=("Arial", 13),
                fg_color="#2c3e50",
                height=55,
                command=lambda n=item["name"], p=item[
                    "price"
                ]: self._add_item_to_cart(n, p),
            )
            item_button.pack(pady=6, padx=10, fill="x")

    def _create_cart_frame(self):
        cart_frame = ctk.CTkFrame(self, corner_radius=10)
        cart_frame.grid(row=0, column=2, padx=15, pady=15, sticky="nsew")

        self.cart_title = ctk.CTkLabel(
            cart_frame, text="Current Cart", font=("Arial", 20, "bold")
        )
        self.cart_title.pack(pady=15)

        self.cart_list = ctk.CTkTextbox(
            cart_frame, font=("Courier New", 13), height=350
        )
        self.cart_list.pack(pady=10, padx=20, fill="both", expand=True)
        self._update_cart_display()

        storno_button = ctk.CTkButton(
            cart_frame,
            text="↩️ Letzten Artikel stornieren",
            font=("Arial", 14, "bold"),
            fg_color="#e67e22",
            hover_color="#d35400",
            height=40,
            command=self._cancel_last_item,
        )
        storno_button.pack(pady=(10, 0), padx=20, fill="x")

        pay_button = ctk.CTkButton(
            cart_frame,
            text="Proceed to Payment",
            font=("Arial", 16, "bold"),
            fg_color="#3498db",
            height=50,
            command=self._checkout_table,
        )
        pay_button.pack(pady=20, padx=20, fill="x")

    def _select_table(self, table_number):
        self.current_table = table_number
        self.cart_title.configure(text=f"Cart - Table {table_number}")
        self._update_cart_display()

    def _add_item_to_cart(self, item_name, item_price):
        if self.current_table is None:
            return

        success = self.db_queries.add_item_to_order(
            self.current_table, item_name
        )
        if success:
            if self.current_table not in self.active_orders:
                self.active_orders[self.current_table] = []

            self.active_orders[self.current_table].append(
                {"name": item_name, "price": item_price}
            )
            # Sofort-Update des Timers triggern
            self._refresh_live_timers()
            self._update_cart_display()

    def _cancel_last_item(self):
        if self.current_table is None or not self.active_orders.get(
            self.current_table, []
        ):
            return

        success = self.db_queries.cancel_last_item(self.current_table)

        if success:
            self.active_orders[self.current_table].pop()
            # Sofort-Update des Timers triggern
            self._refresh_live_timers()
            self._update_cart_display()

    def _update_cart_display(self):
        self.cart_list.configure(state="normal")
        self.cart_list.delete("0.0", "end")

        if self.current_table is None:
            self.cart_list.insert(
                "0.0", "No table selected.\nSelect a table to view order."
            )
            self.cart_list.configure(state="disabled")
            return

        items = self.active_orders.get(self.current_table, [])
        if not items:
            self.cart_list.insert("0.0", "Table is empty.\nAdd items below.")
            self.cart_list.configure(state="disabled")
            return

        receipt_text = f"TAKUMI POS - RECEIPT\nTable: {self.current_table}\n-------------------------\n"
        total = 0.0
        for item in items:
            receipt_text += f"{item['name']:<18} {item['price']:>5.2f} €\n"
            total += item["price"]
        receipt_text += "-------------------------\n"
        receipt_text += f"TOTAL: {total:>17.2f} €"

        self.cart_list.insert("0.0", receipt_text)
        self.cart_list.configure(state="disabled")

    def _checkout_table(self):
        import os

        if self.current_table is None or not self.active_orders.get(
            self.current_table, []
        ):
            return

        items = self.active_orders[self.current_table]

        zeit_datei = datetime.now().strftime("%Y%m%d_%H%M%S")
        zeit_beleg = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

        os.makedirs("rechnungen", exist_ok=True)
        dateiname = (
            f"rechnungen/rechnung_tisch_{self.current_table}_{zeit_datei}.txt"
        )

        bon_text = "=========================================\n"
        bon_text += "            TAKUMI RESTAURANT            \n"
        bon_text += "            KÖLN - SMARTPOS              \n"
        bon_text += "=========================================\n"
        bon_text += f"Datum/Zeit: {zeit_beleg}\n"
        bon_text += f"Tisch-Nr. : Tisch {self.current_table}\n"
        bon_text += "-----------------------------------------\n"

        total = 0.0
        for item in items:
            bon_text += f"{item['name']:<30} {item['price']:>7.2f} €\n"
            total += item["price"]

        bon_text += "-----------------------------------------\n"
        bon_text += f"GESAMTSUMME:                  {total:>7.2f} €\n"
        bon_text += "=========================================\n"
        bon_text += "     Vielen Dank für Ihren Besuch!       \n"
        bon_text += "            Gochisousama deshita         \n"
        bon_text += "=========================================\n"

        try:
            with open(dateiname, "w", encoding="utf-8") as datei:
                datei.write(bon_text)
        except Exception as e:
            print(f"[PRINTER ERROR] Drucken fehlgeschlagen: {e}")

        success = self.db_queries.settle_open_order(self.current_table)
        if success:
            self.active_orders[self.current_table] = []
            # Sofort-Update des Timers triggern (stellt den Tisch zurück auf Free)
            self._refresh_live_timers()
            self._update_cart_display()

    def _open_admin_dashboard(self):
        if self.admin_window is not None and self.admin_window.winfo_exists():
            self.admin_window.lift()
            self.admin_window.focus()
            return
        from gui.admin_window import AdminWindow

        self.admin_window = AdminWindow(
            self, self.db_queries, self._refresh_menu_display
        )

    def _refresh_menu_display(self):
        self._create_menu_frame()