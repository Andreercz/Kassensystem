# src/gui/login_window.py
import customtkinter as ctk


class LoginWindow(ctk.CTk):
    def __init__(self, db_queries, on_login_success_callback):
        super().__init__()
        self.db_queries = db_queries
        self.on_login_success = on_login_success_callback

        self.title("SmartPOS - Login")
        self.geometry("400x350")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")

        title = ctk.CTkLabel(self, text="🍜 Takumi SmartPOS\nAnmeldung", font=("Arial", 20, "bold"))
        title.pack(pady=25)

        self.entry_user = ctk.CTkEntry(self, placeholder_text="Benutzername", width=250)
        self.entry_user.pack(pady=10)

        self.entry_pass = ctk.CTkEntry(self, placeholder_text="Passwort", show="*", width=250)
        self.entry_pass.pack(pady=10)

        self.lbl_error = ctk.CTkLabel(self, text="", text_color="#e74c3c", font=("Arial", 12))
        self.lbl_error.pack(pady=5)

        btn_login = ctk.CTkButton(self, text="Einloggen", width=250, fg_color="#3498db", command=self._try_login)
        btn_login.pack(pady=15)

    def _try_login(self):
        user = self.entry_user.get().strip()
        pas = self.entry_pass.get().strip()

        role = self.db_queries.check_login(user, pas)
        if role:
            self.destroy()  # Schließt das Login-Fenster
            self.on_login_success(role)  # Startet das Hauptfenster mit der Rolle
        else:
            self.lbl_error.configure(text="Ungültige Anmeldedaten!")