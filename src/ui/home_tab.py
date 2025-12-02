import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from src.logger import logger
import threading

class HomeTab(ttk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.context = context
        self.pack(fill=tk.BOTH, expand=True)

        self.create_dashboard()
        self.fii_refresh_counter = 0

    def create_dashboard(self):
        main_pad = ttk.Frame(self, padding=10)
        main_pad.pack(fill=tk.BOTH, expand=True)

        # 1. Top Bar & Toggle
        top_frame = ttk.Frame(main_pad)
        top_frame.pack(fill=tk.X, pady=(0, 10))

        # Engine Toggle
        self.btn_toggle = ttk.Checkbutton(top_frame, text="TRADING ENGINE", bootstyle="success-round-toggle", command=self.toggle_engine)
        self.btn_toggle.invoke() # Default On
        self.btn_toggle.pack(side=tk.LEFT, padx=10)

        # Status Fields
        self.lbl_broker = ttk.Label(top_frame, text="Broker: Disconnected", bootstyle="danger")
        self.lbl_broker.pack(side=tk.LEFT, padx=10)

        self.lbl_market = ttk.Label(top_frame, text="Market: OPEN", bootstyle="info")
        self.lbl_market.pack(side=tk.LEFT, padx=10)

        self.lbl_mode = ttk.Label(top_frame, text="Mode: LIVE", bootstyle="warning")
        self.lbl_mode.pack(side=tk.LEFT, padx=10)

        self.lbl_time = ttk.Label(top_frame, text="00:00:00", font=("Helvetica", 12, "bold"))
        self.lbl_time.pack(side=tk.RIGHT, padx=10)

        # Main Grid
        self.grid_frame = ttk.Frame(main_pad)
        self.grid_frame.pack(fill=tk.BOTH, expand=True)
        self.grid_frame.columnconfigure(0, weight=1)
        self.grid_frame.columnconfigure(1, weight=1)
        self.grid_frame.columnconfigure(2, weight=1)

        # 2. Indices Panel
        self.create_card(self.grid_frame, "Indices", 0, 0, self.create_indices_content)

        # 3. PnL Panel
        self.create_card(self.grid_frame, "PnL Summary", 0, 1, self.create_pnl_content)

        # 4. FII/DII Panel
        self.create_card(self.grid_frame, "FII / DII Data", 0, 2, self.create_fii_content)

        # 5. System Summary (Bottom)
        self.create_system_summary(main_pad)

    def create_card(self, parent, title, row, col, content_func):
        card = ttk.Labelframe(parent, text=title, bootstyle="secondary", padding=10)
        card.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
        content_func(card)
        return card

    def create_indices_content(self, parent):
        # Header
        h_frame = ttk.Frame(parent)
        h_frame.pack(fill=tk.X)
        ttk.Label(h_frame, text="Index", width=15, font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        ttk.Label(h_frame, text="LTP", width=10, font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        ttk.Label(h_frame, text="Chg (%)", width=10, font=("Arial", 9, "bold")).pack(side=tk.LEFT)

        self.indices_widgets = {}
        indices = ["NIFTY 50", "BANKNIFTY", "FINNIFTY", "SENSEX", "INDIA VIX"]

        for name in indices:
            row = ttk.Frame(parent)
            row.pack(fill=tk.X, pady=2)

            lbl_name = ttk.Label(row, text=name, width=15)
            lbl_name.pack(side=tk.LEFT)

            lbl_ltp = ttk.Label(row, text="0.00", width=10)
            lbl_ltp.pack(side=tk.LEFT)

            lbl_chg = ttk.Label(row, text="0.00 (0.00%)", width=15)
            lbl_chg.pack(side=tk.LEFT)

            self.indices_widgets[name] = (lbl_ltp, lbl_chg)

    def create_pnl_content(self, parent):
        # Cards
        pnl_row = ttk.Frame(parent)
        pnl_row.pack(fill=tk.X, pady=10)

        self.lbl_realized = ttk.Label(pnl_row, text="Realised: ₹0.00", bootstyle="info")
        self.lbl_realized.pack(fill=tk.X)

        self.lbl_unrealized = ttk.Label(pnl_row, text="Unrealised: ₹0.00", bootstyle="info")
        self.lbl_unrealized.pack(fill=tk.X)

        self.lbl_total_pnl = ttk.Label(pnl_row, text="Total: ₹0.00", font=("Helvetica", 16, "bold"), bootstyle="success")
        self.lbl_total_pnl.pack(pady=10)

        ttk.Separator(parent).pack(fill=tk.X, pady=5)
        ttk.Label(parent, text="Strategy Status", font=("Arial", 9, "bold")).pack(anchor="w")

        self.strat_frame = ttk.Frame(parent)
        self.strat_frame.pack(fill=tk.BOTH, expand=True)
        # Will populate dynamically

    def create_fii_content(self, parent):
        self.lbl_fii = ttk.Label(parent, text="FII Net: Loading...", font=("Arial", 10))
        self.lbl_fii.pack(anchor="w", pady=5)

        self.lbl_dii = ttk.Label(parent, text="DII Net: Loading...", font=("Arial", 10))
        self.lbl_dii.pack(anchor="w", pady=5)

        self.lbl_fii_update = ttk.Label(parent, text="Last Update: --", font=("Arial", 8))
        self.lbl_fii_update.pack(anchor="e", pady=10)

        ttk.Button(parent, text="Force Refresh", command=self.refresh_fii_dii, bootstyle="outline").pack(fill=tk.X)

    def create_system_summary(self, parent):
        b_frame = ttk.Frame(parent)
        b_frame.pack(fill=tk.X, pady=10)

        # Stats
        self.lbl_stats = ttk.Label(b_frame, text="Open Positions: 0 | Trades: 0 | DD: 0%")
        self.lbl_stats.pack(side=tk.LEFT, padx=10)

        # Buttons
        ttk.Button(b_frame, text="Panic EXIT ALL", bootstyle="danger", command=self.panic_exit).pack(side=tk.RIGHT, padx=5)
        ttk.Button(b_frame, text="Go to Strategies", command=lambda: self.master.select(2)).pack(side=tk.RIGHT, padx=5)

    def toggle_engine(self):
        # Logic to start/stop Data Engine
        pass # Bound to variable ideally

    def panic_exit(self):
        if self.context.get('broker'):
            # Implement exit all
            pass

    def refresh_fii_dii(self):
        import threading
        from src.fii_dii_scraper import fetch_fii_dii_data
        threading.Thread(target=fetch_fii_dii_data, daemon=True).start()

    def update_ui(self):
        # 1. Time
        import time
        self.lbl_time.config(text=time.strftime("%H:%M:%S"))

        # 2. Broker Status
        broker = self.context.get('broker')
        if broker:
            if broker.connected:
                self.lbl_broker.config(text="Broker: Connected", bootstyle="success")
            else:
                self.lbl_broker.config(text="Broker: Disconnected", bootstyle="danger")

        # 3. Indices Update (0.2s)
        data_engine = self.context.get('data_engine')
        if data_engine:
            for name, widgets in self.indices_widgets.items():
                lbl_ltp, lbl_chg = widgets
                quote = data_engine.get_latest_tick(name)
                # Expects dict {ltp, change, pct_change}
                ltp = quote.get('ltp', 0.0)
                chg = quote.get('change', 0.0)
                pct = quote.get('pct_change', 0.0)

                lbl_ltp.config(text=f"{ltp:,.2f}")
                lbl_chg.config(text=f"{chg:+.2f} ({pct:+.2f}%)")

                color = "success" if chg >= 0 else "danger"
                lbl_ltp.config(bootstyle=color)
                lbl_chg.config(bootstyle=color)

        # 4. PnL Update
        if broker and broker.connected:
            try:
                positions = broker.get_positions()
                total_pnl = 0.0
                open_pos = 0

                for p in positions:
                    val = 0.0
                    if hasattr(p, 'pnl'): val = float(p.pnl)
                    elif isinstance(p, dict): val = float(p.get('pnl', 0.0))
                    total_pnl += val

                    qty = 0
                    if hasattr(p, 'quantity'): qty = p.quantity
                    elif isinstance(p, dict): qty = p.get('quantity', 0)
                    if qty != 0: open_pos += 1

                color = "success" if total_pnl >= 0 else "danger"
                self.lbl_total_pnl.config(text=f"Total: ₹{total_pnl:,.2f}", bootstyle=color)
                self.lbl_stats.config(text=f"Open Positions: {open_pos} | Trades: -- | DD: --")

            except Exception:
                pass

        # 5. FII Refresh Logic (60s)
        self.fii_refresh_counter += 1
        if self.fii_refresh_counter >= 300: # 300 * 200ms = 60s
            self.refresh_fii_dii()
            self.fii_refresh_counter = 0

        # Update FII Labels from cache
        from src.fii_dii_scraper import get_recent_fii_dii
        fii_data = get_recent_fii_dii()
        if fii_data:
            latest = fii_data[-1]
            # Parse if possible
            self.lbl_fii.config(text=f"FII Data Available") # Placeholder until parse logic matches scraper

        # Loop
        self.after(200, self.update_ui)
