import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from src.logger import logger

class HomeTab(ttk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.context = context
        self.pack(fill=tk.BOTH, expand=True)

        self.create_dashboard()

    def create_dashboard(self):
        # Apply padding to the whole tab
        main_pad = ttk.Frame(self, padding=20)
        main_pad.pack(fill=tk.BOTH, expand=True)

        # --- Top Status Bar ---
        self.status_frame = ttk.Frame(main_pad)
        self.status_frame.pack(fill=tk.X, pady=(0, 20))

        # Using a Frame with a "Card" look isn't direct in tk, but we use LabelFrame or colored frames
        # Simple clean text for status
        self.lbl_broker = ttk.Label(self.status_frame, text="● Disconnected", bootstyle="danger", font=("Helvetica", 10))
        self.lbl_broker.pack(side=tk.LEFT)

        self.lbl_time = ttk.Label(self.status_frame, text="00:00:00", font=("Helvetica", 14, "bold"))
        self.lbl_time.pack(side=tk.RIGHT)

        # --- Main Grid ---
        # 3 Columns: Indices, PnL, Market Stats
        self.grid_frame = ttk.Frame(main_pad)
        self.grid_frame.pack(fill=tk.BOTH, expand=True)
        self.grid_frame.columnconfigure(0, weight=1)
        self.grid_frame.columnconfigure(1, weight=1)
        self.grid_frame.columnconfigure(2, weight=1)

        # 1. Indices Card
        self.create_card(self.grid_frame, "Market Indices", 0, 0, self.create_indices_content)

        # 2. PnL Card (Center, slightly larger importance)
        self.create_card(self.grid_frame, "Profit & Loss", 0, 1, self.create_pnl_content)

        # 3. FII/DII Card
        self.create_card(self.grid_frame, "Institutional Activity", 0, 2, self.create_fii_content)

    def create_card(self, parent, title, row, col, content_func):
        card = ttk.Labelframe(parent, text=title, bootstyle="info", padding=15)
        card.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
        content_func(card)
        return card

    def create_indices_content(self, parent):
        self.indices_labels = {}
        indices = ["NIFTY 50", "BANKNIFTY", "FINNIFTY", "INDIA VIX"]

        for idx, name in enumerate(indices):
            row_frame = ttk.Frame(parent)
            row_frame.pack(fill=tk.X, pady=5)

            ttk.Label(row_frame, text=name, font=("Helvetica", 10), foreground="#aaaaaa").pack(side=tk.LEFT)
            lbl = ttk.Label(row_frame, text="0.00", font=("Helvetica", 11, "bold"))
            lbl.pack(side=tk.RIGHT)
            self.indices_labels[name] = lbl

    def create_pnl_content(self, parent):
        # Total PnL Big Display
        self.lbl_total_pnl = ttk.Label(parent, text="₹ 0.00", font=("Helvetica", 24, "bold"), bootstyle="success")
        self.lbl_total_pnl.pack(pady=(10, 20), anchor="center")

        # Separator
        ttk.Separator(parent).pack(fill=tk.X, pady=10)

        # Details
        row1 = ttk.Frame(parent)
        row1.pack(fill=tk.X, pady=2)
        ttk.Label(row1, text="Realized P&L", foreground="#aaaaaa").pack(side=tk.LEFT)
        ttk.Label(row1, text="₹ 0.00").pack(side=tk.RIGHT)

        row2 = ttk.Frame(parent)
        row2.pack(fill=tk.X, pady=2)
        ttk.Label(row2, text="Unrealized P&L", foreground="#aaaaaa").pack(side=tk.LEFT)
        ttk.Label(row2, text="₹ 0.00").pack(side=tk.RIGHT)

    def create_fii_content(self, parent):
        self.lbl_fii = ttk.Label(parent, text="FII Cash: --", font=("Helvetica", 10))
        self.lbl_fii.pack(anchor="w", pady=5)

        self.lbl_dii = ttk.Label(parent, text="DII Cash: --", font=("Helvetica", 10))
        self.lbl_dii.pack(anchor="w", pady=5)

        ttk.Button(parent, text="Refresh Data", bootstyle="outline-secondary", command=self.refresh_fii_dii).pack(pady=10, fill=tk.X)

    def refresh_fii_dii(self):
        # Trigger scraper (threaded ideally, but simple here)
        pass

    def update_ui(self):
        # Time
        import time
        self.lbl_time.config(text=time.strftime("%H:%M:%S"))

        # Status
        if self.context['broker'].connected:
            self.lbl_broker.config(text="● Connected", bootstyle="success")
        else:
            self.lbl_broker.config(text="● Disconnected", bootstyle="danger")

        # Indices
        data_engine = self.context.get('data_engine')
        if data_engine:
            for name, label in self.indices_labels.items():
                tick = data_engine.get_latest_tick(name)
                price = tick.get('ltp', 0.0)
                label.config(text=f"{price:.2f}")

        self.after(200, self.update_ui)
