import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from src.logger import logger

class HomeTab(ttk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.context = context # Holds references to brokers, engines
        self.pack(fill=tk.BOTH, expand=True)

        self.create_dashboard()

    def create_dashboard(self):
        # Top Status Bar
        self.status_frame = ttk.Frame(self)
        self.status_frame.pack(fill=tk.X, padx=10, pady=5)

        self.lbl_broker = ttk.Label(self.status_frame, text="Broker: Disconnected", bootstyle="danger")
        self.lbl_broker.pack(side=tk.LEFT, padx=5)

        self.lbl_time = ttk.Label(self.status_frame, text="00:00:00", font=("Helvetica", 12, "bold"))
        self.lbl_time.pack(side=tk.RIGHT, padx=5)

        # Main Content Area (Grid)
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 1. Indices Panel (Left)
        self.indices_frame = ttk.LabelFrame(self.content_frame, text="Indices")
        self.indices_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.indices_labels = {}
        indices = ["NIFTY 50", "BANKNIFTY", "RELIANCE"]
        for idx, name in enumerate(indices):
            lbl_name = ttk.Label(self.indices_frame, text=name, font=("Helvetica", 10))
            lbl_name.grid(row=idx, column=0, padx=5, pady=2, sticky="w")

            lbl_val = ttk.Label(self.indices_frame, text="0.00", font=("Helvetica", 10, "bold"))
            lbl_val.grid(row=idx, column=1, padx=5, pady=2, sticky="e")
            self.indices_labels[name] = lbl_val

        # 2. PnL Center
        self.pnl_frame = ttk.LabelFrame(self.content_frame, text="PnL Summary")
        self.pnl_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.lbl_total_pnl = ttk.Label(self.pnl_frame, text="₹ 0.00", font=("Helvetica", 18, "bold"), bootstyle="success")
        self.lbl_total_pnl.pack(pady=20)

        ttk.Label(self.pnl_frame, text="Realized: ₹0.00").pack()
        ttk.Label(self.pnl_frame, text="Unrealized: ₹0.00").pack()

        # 3. FII/DII Right
        self.fii_frame = ttk.LabelFrame(self.content_frame, text="FII / DII")
        self.fii_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)

        self.lbl_fii = ttk.Label(self.fii_frame, text="FII: Loading...")
        self.lbl_fii.pack(pady=5)
        self.lbl_dii = ttk.Label(self.fii_frame, text="DII: Loading...")
        self.lbl_dii.pack(pady=5)

        # Configure Grid Weights
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.columnconfigure(1, weight=2)
        self.content_frame.columnconfigure(2, weight=1)
        self.content_frame.rowconfigure(0, weight=1)

    def update_ui(self):
        # Update Time
        import time
        self.lbl_time.config(text=time.strftime("%H:%M:%S"))

        # Update Connection Status
        if self.context['broker'].connected:
            self.lbl_broker.config(text="Broker: Connected", bootstyle="success")
        else:
            self.lbl_broker.config(text="Broker: Disconnected", bootstyle="danger")

        # Update Indices (From Data Engine)
        data_engine = self.context.get('data_engine')
        if data_engine:
            for name, label in self.indices_labels.items():
                tick = data_engine.get_latest_tick(name)
                price = tick.get('ltp', 0.0)
                label.config(text=f"{price:.2f}")

        # Schedule Next Update (The 0.2s loop)
        self.after(200, self.update_ui)
