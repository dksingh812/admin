import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from src.logger import logger
import webbrowser
import threading

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
        self.mode_var = tk.StringVar(value="LIVE")
        frame_mode = ttk.LabelFrame(self, text="Environment")
        frame_mode.pack(fill=tk.X, pady=10)

        ttk.Radiobutton(frame_mode, text="Live Trading", variable=self.mode_var, value="LIVE").pack(side=tk.LEFT, padx=20)
        ttk.Radiobutton(frame_mode, text="Sandbox (Testing)", variable=self.mode_var, value="SANDBOX").pack(side=tk.LEFT, padx=20)

        # Credentials Input
        frame_creds = ttk.LabelFrame(self, text="API Credentials")
        frame_creds.pack(fill=tk.X, pady=10)

        ttk.Label(frame_creds, text="API Key:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_key = ttk.Entry(frame_creds, width=50)
        self.entry_key.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_creds, text="API Secret:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_secret = ttk.Entry(frame_creds, show="*", width=50)
        self.entry_secret.grid(row=1, column=1, padx=5, pady=5)

        # Redirect URI (Exposed for easier debugging)
        ttk.Label(frame_creds, text="Redirect URI:").grid(row=2, column=0, padx=5, pady=5)
        self.entry_uri = ttk.Entry(frame_creds, width=50)
        self.entry_uri.grid(row=2, column=1, padx=5, pady=5)

        # Load defaults
        config = self.context.get("config", {})
        if config.get("api_key"): self.entry_key.insert(0, config["api_key"])
        if config.get("api_secret"): self.entry_secret.insert(0, config["api_secret"])

        default_uri = config.get("redirect_uri", "http://127.0.0.1:5000/callback")
        self.entry_uri.insert(0, default_uri)

        # Action Buttons
        self.btn_login = ttk.Button(self, text="Login & Authorize", command=self.on_login, bootstyle="primary")
        self.btn_login.pack(pady=20)

        self.lbl_status = ttk.Label(self, text="Status: Disconnected")
        self.lbl_status.pack()

        ttk.Label(self, text="Tip: Ensure 'Redirect URI' matches exactly what is in your Upstox App Settings.", font=("Helvetica", 8), bootstyle="secondary").pack()

    def on_login(self):
        mode = self.mode_var.get()
        api_key = self.entry_key.get()
        api_secret = self.entry_secret.get()
        redirect_uri = self.entry_uri.get().strip()

        logger.info(f"Initiating Login. Mode: {mode}, URI: {redirect_uri}")

        self.btn_login.config(state="disabled")
        self.lbl_status.config(text="Status: Waiting for Browser Login...", bootstyle="warning")

        # Setup Broker
        from src.upstox_broker import UpstoxBroker
        broker = UpstoxBroker(redirect_uri=redirect_uri)

        # Update Context
        self.context['broker'] = broker
        self.context['data_engine'].broker = broker
        self.context['risk_engine'].broker = broker
        broker.set_risk_engine(self.context['risk_engine'])

        # Update Strategies
        for strategy in self.context.get('strategies', []):
            strategy.broker = broker

        # Start Server
        try:
            from urllib.parse import urlparse
            parsed = urlparse(redirect_uri)
            port = parsed.port if parsed.port else 5000
        except:
            port = 5000

        from src.auth_server import AuthServer
        server = AuthServer(port=port)

        try:
            server.start_server()
        except Exception as e:
            logger.error(f"Failed to start auth server: {e}")
            self.lbl_status.config(text=f"Error: Port {port} busy?", bootstyle="danger")
            self.btn_login.config(state="normal")
            return

        # Open Browser
        login_url = broker.get_login_url(api_key)
        webbrowser.open(login_url)

        threading.Thread(target=self.wait_for_auth, args=(server, broker, api_key, api_secret, redirect_uri), daemon=True).start()

    def wait_for_auth(self, server, broker, api_key, api_secret, redirect_uri):
        code = server.wait_for_code(timeout=120)
        if code:
            self.after(0, lambda: self.finish_login(broker, api_key, api_secret, code, redirect_uri))
        else:
            self.after(0, lambda: self.fail_login("Timeout"))

    def finish_login(self, broker, api_key, api_secret, code, redirect_uri):
        if broker.authenticate(api_key, api_secret, code=code):
            self.lbl_status.config(text="Status: Connected Successfully", bootstyle="success")

            # Save credentials & URI
            config = self.context.get("config", {})
            config["api_key"] = api_key
            config["api_secret"] = api_secret
            config["redirect_uri"] = redirect_uri
            from src.config import save_config
            save_config(config)

        else:
            self.lbl_status.config(text="Status: Auth Failed at Upstox", bootstyle="danger")

        self.btn_login.config(state="normal")

    def fail_login(self, reason):
        self.lbl_status.config(text=f"Status: Login Failed ({reason})", bootstyle="danger")
        self.btn_login.config(state="normal")
