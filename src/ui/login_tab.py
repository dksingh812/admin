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
        self.entry_key = ttk.Entry(frame_creds, width=40)
        self.entry_key.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_creds, text="API Secret:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_secret = ttk.Entry(frame_creds, show="*", width=40)
        self.entry_secret.grid(row=1, column=1, padx=5, pady=5)

        # Action Buttons
        self.btn_login = ttk.Button(self, text="Login & Authorize", command=self.on_login, bootstyle="primary")
        self.btn_login.pack(pady=20)

        self.lbl_status = ttk.Label(self, text="Status: Disconnected")
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

        logger.info(f"Initiating Login. Mode: {mode}")

        # Disable button
        self.btn_login.config(state="disabled")
        self.lbl_status.config(text="Status: Waiting for Browser Login...", bootstyle="warning")

        # Setup Broker
        from src.upstox_broker import UpstoxBroker

        # Read Redirect URI from config, default to standard
        config = self.context.get("config", {})
        redirect_uri = config.get("redirect_uri", "http://127.0.0.1:5000/callback")

        broker = UpstoxBroker(redirect_uri=redirect_uri)

        self.context['broker'] = broker
        self.context['data_engine'].broker = broker
        self.context['risk_engine'].broker = broker
        broker.set_risk_engine(self.context['risk_engine'])

        # Start Local Server
        # Parse port from URI
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

        # Run waiting loop in a separate thread to not freeze UI
        threading.Thread(target=self.wait_for_auth, args=(server, broker, api_key, api_secret), daemon=True).start()

    def wait_for_auth(self, server, broker, api_key, api_secret):
        code = server.wait_for_code(timeout=120) # 2 minutes timeout

        if code:
            self.after(0, lambda: self.finish_login(broker, api_key, api_secret, code))
        else:
            self.after(0, lambda: self.fail_login("Timeout"))

    def finish_login(self, broker, api_key, api_secret, code):
        if broker.authenticate(api_key, api_secret, code=code):
            self.lbl_status.config(text="Status: Connected Successfully", bootstyle="success")

            # Save credentials
            config = self.context.get("config", {})
            config["api_key"] = api_key
            config["api_secret"] = api_secret
            from src.config import save_config
            save_config(config)

        else:
            self.lbl_status.config(text="Status: Auth Failed at Upstox", bootstyle="danger")

        self.btn_login.config(state="normal")

    def fail_login(self, reason):
        self.lbl_status.config(text=f"Status: Login Failed ({reason})", bootstyle="danger")
        self.btn_login.config(state="normal")
