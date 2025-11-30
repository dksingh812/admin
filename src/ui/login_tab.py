import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from src.logger import logger
import webbrowser

class LoginTab(ttk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.context = context
        self.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.create_widgets()

    def create_widgets(self):
        lbl_title = ttk.Label(self, text="Broker Login", font=("Helvetica", 16, "bold"))
        lbl_title.pack(pady=10)

        # Mode Selection
        self.mode_var = tk.StringVar(value="PAPER")
        frame_mode = ttk.LabelFrame(self, text="Trading Mode")
        frame_mode.pack(fill=tk.X, pady=10)

        ttk.Radiobutton(frame_mode, text="Paper Trading (Mock)", variable=self.mode_var, value="PAPER").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(frame_mode, text="Upstox Sandbox", variable=self.mode_var, value="SANDBOX").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(frame_mode, text="Upstox Live", variable=self.mode_var, value="LIVE").pack(side=tk.LEFT, padx=10)

        # Credentials Input
        frame_creds = ttk.LabelFrame(self, text="API Credentials")
        frame_creds.pack(fill=tk.X, pady=10)

        ttk.Label(frame_creds, text="API Key:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_key = ttk.Entry(frame_creds, width=40)
        self.entry_key.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_creds, text="API Secret:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_secret = ttk.Entry(frame_creds, show="*", width=40)
        self.entry_secret.grid(row=1, column=1, padx=5, pady=5)

        # Action Buttons
        btn_login = ttk.Button(self, text="Login / Authorize", command=self.on_login, bootstyle="primary")
        btn_login.pack(pady=20)

        self.lbl_status = ttk.Label(self, text="Status: Waiting for input...")
        self.lbl_status.pack()

        # Load from config if available
        config = self.context.get("config", {})
        if config.get("api_key"):
            self.entry_key.insert(0, config["api_key"])
        if config.get("api_secret"):
            self.entry_secret.insert(0, config["api_secret"])

    def on_login(self):
        mode = self.mode_var.get()
        api_key = self.entry_key.get()
        api_secret = self.entry_secret.get()

        logger.info(f"Attempting Login. Mode: {mode}")

        if mode == "PAPER":
            # Switch Broker to Mock
            from src.mock_broker import MockBroker
            self.context['broker'] = MockBroker()
            success = self.context['broker'].authenticate(api_key, api_secret)
            self.lbl_status.config(text="Status: Mock Broker Connected", bootstyle="success")

        else:
            # Switch Broker to Upstox
            from src.upstox_broker import UpstoxBroker
            broker = UpstoxBroker(redirect_uri="http://127.0.0.1:5000/callback")
            self.context['broker'] = broker

            # Open Browser for OAuth
            login_url = broker.get_login_url(api_key)
            webbrowser.open(login_url)

            # Prompt user for code (Simplification for Desktop App without local server listener)
            # In a full app, we'd run a Flask server to catch the callback.
            # Here, we ask the user to paste the code or url.
            self.ask_for_code_popup(broker, api_key, api_secret)

    def ask_for_code_popup(self, broker, api_key, api_secret):
        # Create a Toplevel window
        top = ttk.Toplevel(self)
        top.title("Enter Auth Code")
        top.geometry("400x200")

        ttk.Label(top, text="Please login in the browser.\nThen copy the 'code' from the URL and paste it here:").pack(pady=10)
        entry_code = ttk.Entry(top, width=40)
        entry_code.pack(pady=5)

        def submit_code():
            code = entry_code.get()
            if broker.authenticate(api_key, api_secret, code=code):
                self.lbl_status.config(text="Status: Upstox Connected", bootstyle="success")
                top.destroy()
            else:
                self.lbl_status.config(text="Status: Auth Failed", bootstyle="danger")

        ttk.Button(top, text="Submit Code", command=submit_code).pack(pady=10)
