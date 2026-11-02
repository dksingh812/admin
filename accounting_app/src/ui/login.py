import customtkinter as ctk
from src.database.session import get_db
from src.services.auth import authenticate_user

class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_login_success, **kwargs):
        super().__init__(master, **kwargs)
        self.on_login_success = on_login_success

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.login_frame = ctk.CTkFrame(self, width=400, corner_radius=15)
        self.login_frame.grid(row=0, column=0, padx=20, pady=20)
        self.login_frame.grid_columnconfigure(0, weight=1)

        # Title
        self.title_label = ctk.CTkLabel(self.login_frame, text="Accounting Software", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(30, 20))

        # Username
        self.username_entry = ctk.CTkEntry(self.login_frame, width=250, placeholder_text="Username")
        self.username_entry.grid(row=1, column=0, padx=20, pady=10)

        # Password
        self.password_entry = ctk.CTkEntry(self.login_frame, width=250, placeholder_text="Password", show="*")
        self.password_entry.grid(row=2, column=0, padx=20, pady=10)
        self.password_entry.bind("<Return>", lambda event: self.login())

        # Error Label
        self.error_label = ctk.CTkLabel(self.login_frame, text="", text_color="red")
        self.error_label.grid(row=3, column=0, padx=20, pady=5)

        # Login Button
        self.login_button = ctk.CTkButton(self.login_frame, text="Login", width=250, command=self.login)
        self.login_button.grid(row=4, column=0, padx=20, pady=(10, 30))

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            self.error_label.configure(text="Please enter username and password")
            return

        db = next(get_db())
        user = authenticate_user(db, username, password)
        db.close()

        if user:
            self.error_label.configure(text="")
            self.on_login_success(user)
        else:
            self.error_label.configure(text="Invalid credentials")
