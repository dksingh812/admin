import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from src.logger import logger
import threading
from src.global_market_scraper import global_market_scraper

class HomeTab(ttk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.context = context
        self.pack(fill=tk.BOTH, expand=True)

        self.create_dashboard()
        self.fii_refresh_counter = 0
        self.global_refresh_counter = 0

    def create_dashboard(self):
        main_pad = ttk.Frame(self, padding=10)
        main_pad.pack(fill=tk.BOTH, expand=True)

        # 1. Top Bar
        top_frame = ttk.Frame(main_pad)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        self.btn_toggle = ttk.Checkbutton(top_frame, text="TRADING ENGINE", bootstyle="success-round-toggle", command=self.toggle_engine)
        self.btn_toggle.invoke()
        self.btn_toggle.pack(side=tk.LEFT, padx=10)
        self.lbl_broker = ttk.Label(top_frame, text="Broker: Disconnected", bootstyle="danger")
        self.lbl_broker.pack(side=tk.LEFT, padx=10)
        self.lbl_time = ttk.Label(top_frame, text="00:00:00", font=("Helvetica", 12, "bold"))
        self.lbl_time.pack(side=tk.RIGHT, padx=10)

        # Main Grid
        self.grid_frame = ttk.Frame(main_pad)
        self.grid_frame.pack(fill=tk.BOTH, expand=True)
        self.grid_frame.columnconfigure(0, weight=2) # Indices wider
        self.grid_frame.columnconfigure(1, weight=1)
        self.grid_frame.columnconfigure(2, weight=1)

        # 2. Indices Panel (Tabs)
        idx_card = ttk.Labelframe(self.grid_frame, text="Market Watch", bootstyle="secondary", padding=5)
        idx_card.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.idx_notebook = ttk.Notebook(idx_card)
        self.idx_notebook.pack(fill=tk.BOTH, expand=True)

        # Tabs
        self.tab_indian = ttk.Frame(self.idx_notebook)
        self.tab_us = ttk.Frame(self.idx_notebook)
        self.tab_eu = ttk.Frame(self.idx_notebook)
        self.tab_asia = ttk.Frame(self.idx_notebook)
        self.tab_comm = ttk.Frame(self.idx_notebook)

        self.idx_notebook.add(self.tab_indian, text="Indian")
        self.idx_notebook.add(self.tab_us, text="US")
        self.idx_notebook.add(self.tab_eu, text="Europe")
        self.idx_notebook.add(self.tab_asia, text="Asia")
        self.idx_notebook.add(self.tab_comm, text="Comm.")

        # Populate
        self.indices_widgets = {} # Stores label refs
        self.create_index_list(self.tab_indian, ["NIFTY 50", "BANKNIFTY", "FINNIFTY", "SENSEX", "INDIA VIX"])
        self.create_index_list(self.tab_us, ["Dow Jones", "S&P 500", "Nasdaq"])
        self.create_index_list(self.tab_eu, ["FTSE", "CAC", "DAX"])
        self.create_index_list(self.tab_asia, ["GIFT NIFTY", "Nikkei 225", "Hang Seng", "Straits Times", "KOSPI"])
        self.create_index_list(self.tab_comm, ["Brent Crude", "Gold", "Crude Oil", "Silver", "Natural Gas"])

        # 3. PnL Panel
        self.create_card(self.grid_frame, "PnL Summary", 0, 1, self.create_pnl_content)

        # 4. FII/DII Panel
        self.create_card(self.grid_frame, "FII / DII Data", 0, 2, self.create_fii_content)

        # 5. System Summary
        self.create_system_summary(main_pad)

    def create_card(self, parent, title, row, col, content_func):
        card = ttk.Labelframe(parent, text=title, bootstyle="secondary", padding=10)
        card.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
        content_func(card)
        return card

    def create_index_list(self, parent, names):
        # Header
        h_frame = ttk.Frame(parent)
        h_frame.pack(fill=tk.X)
        ttk.Label(h_frame, text="Name", width=15, font=("Arial", 8, "bold")).pack(side=tk.LEFT)
        ttk.Label(h_frame, text="Price", width=10, font=("Arial", 8, "bold")).pack(side=tk.LEFT)
        ttk.Label(h_frame, text="Chg", width=10, font=("Arial", 8, "bold")).pack(side=tk.LEFT)

        for name in names:
            row = ttk.Frame(parent)
            row.pack(fill=tk.X, pady=2)
            ttk.Label(row, text=name, width=15, font=("Arial", 9)).pack(side=tk.LEFT)
            lbl_ltp = ttk.Label(row, text="--", width=10, font=("Arial", 9))
            lbl_ltp.pack(side=tk.LEFT)
            lbl_chg = ttk.Label(row, text="--", width=15, font=("Arial", 9))
            lbl_chg.pack(side=tk.LEFT)
            self.indices_widgets[name] = (lbl_ltp, lbl_chg)

    def create_pnl_content(self, parent):
        self.lbl_total_pnl = ttk.Label(parent, text="₹ 0.00", font=("Helvetica", 20, "bold"), bootstyle="success")
        self.lbl_total_pnl.pack(pady=20, anchor="center")

    def create_fii_content(self, parent):
        self.lbl_fii = ttk.Label(parent, text="FII Net: --")
        self.lbl_fii.pack(anchor="w")
        self.lbl_dii = ttk.Label(parent, text="DII Net: --")
        self.lbl_dii.pack(anchor="w")

    def create_system_summary(self, parent):
        b_frame = ttk.Frame(parent)
        b_frame.pack(fill=tk.X, pady=10)
        ttk.Button(b_frame, text="Panic EXIT", bootstyle="danger", command=self.panic_exit).pack(side=tk.RIGHT)

    def toggle_engine(self): pass
    def panic_exit(self): pass

    def update_ui(self):
        # Time & Broker
        import time
        self.lbl_time.config(text=time.strftime("%H:%M:%S"))
        broker = self.context.get('broker')
        if broker:
            self.lbl_broker.config(text="Broker: Connected" if broker.connected else "Broker: Disconnected",
                                   bootstyle="success" if broker.connected else "danger")

        # 1. Update Indian Indices (Fast - Upstox)
        data_engine = self.context.get('data_engine')
        if data_engine:
            for name in ["NIFTY 50", "BANKNIFTY", "FINNIFTY", "SENSEX", "INDIA VIX"]:
                if name in self.indices_widgets:
                    quote = data_engine.get_latest_tick(name)
                    self._update_widget(name, quote.get('ltp', 0), quote.get('change', 0), quote.get('pct_change', 0))

        # 2. Update Global/Commodities (Slow - Scraper)
        # We fetch from global_market_scraper cache
        global_data = global_market_scraper.get_data()
        for region, items in global_data.items():
            for name, data in items.items():
                if name in self.indices_widgets:
                    self._update_widget(name, data['price'], data['change'], data['pct'])

        # 3. PnL (as before)
        # ... (simplified for this update)

        self.after(200, self.update_ui)

    def _update_widget(self, name, price, change, pct):
        lbl_ltp, lbl_chg = self.indices_widgets[name]
        lbl_ltp.config(text=f"{price:,.2f}")
        lbl_chg.config(text=f"{change:+.2f} ({pct:+.2f}%)")
        color = "success" if change >= 0 else "danger"
        lbl_ltp.config(bootstyle=color)
        lbl_chg.config(bootstyle=color)
