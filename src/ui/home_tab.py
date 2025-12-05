import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from src.global_market_scraper import global_market_scraper

class HomeTab(ttk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.context = context
        self.pack(fill=tk.BOTH, expand=True)

        self.create_dashboard()

    def create_dashboard(self):
        self.paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Left Panel: Indices ---
        self.f_indices = ttk.Labelframe(self.paned, text="Market Watch", padding=5)
        self.paned.add(self.f_indices, weight=0)

        canvas = tk.Canvas(self.f_indices, bg="#2b2b2b", highlightthickness=0, width=280)
        scrollbar = ttk.Scrollbar(self.f_indices, orient="vertical", command=canvas.yview)
        self.idx_content = ttk.Frame(canvas)

        self.idx_content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.idx_content, anchor="nw", width=280)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.indices_widgets = {}
        self.add_indices_content()

        # --- Right Panel: Dashboard ---
        self.f_dash = ttk.Frame(self.paned, padding=10)
        self.paned.add(self.f_dash, weight=3)

        # Top Bar
        f_top = ttk.Frame(self.f_dash)
        f_top.pack(fill=tk.X, pady=10)
        self.btn_toggle = ttk.Checkbutton(f_top, text="TRADING ENGINE", bootstyle="success-round-toggle", command=self.toggle_engine)
        self.btn_toggle.invoke()
        self.btn_toggle.pack(side=tk.LEFT)
        self.lbl_broker = ttk.Label(f_top, text="Disconnected", bootstyle="danger")
        self.lbl_broker.pack(side=tk.LEFT, padx=20)
        self.lbl_time = ttk.Label(f_top, text="00:00:00", font=("Helvetica", 16, "bold"))
        self.lbl_time.pack(side=tk.RIGHT)

        # Grid
        f_grid = ttk.Frame(self.f_dash)
        f_grid.pack(fill=tk.BOTH, expand=True)
        f_grid.columnconfigure(0, weight=1)
        f_grid.columnconfigure(1, weight=1)
        f_grid.columnconfigure(2, weight=1) # New column for OI Analysis

        # 1. PnL Card
        card_pnl = ttk.Labelframe(f_grid, text="PnL Summary", padding=20)
        card_pnl.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.lbl_realised = ttk.Label(card_pnl, text="Realised: ₹ 0.00", font=("Helvetica", 12))
        self.lbl_realised.pack(pady=5)
        self.lbl_unrealised = ttk.Label(card_pnl, text="Unrealised: ₹ 0.00", font=("Helvetica", 12))
        self.lbl_unrealised.pack(pady=5)
        ttk.Separator(card_pnl).pack(fill=tk.X, pady=15)
        self.lbl_total_pnl = ttk.Label(card_pnl, text="₹ 0.00", font=("Helvetica", 28, "bold"), bootstyle="success")
        self.lbl_total_pnl.pack()

        # 2. FII/DII Card
        card_fii = ttk.Labelframe(f_grid, text="FII / DII Activity", padding=20)
        card_fii.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.lbl_fii = ttk.Label(card_fii, text="FII Net: Loading...", font=("Helvetica", 14))
        self.lbl_fii.pack(pady=10, anchor="w")
        self.lbl_dii = ttk.Label(card_fii, text="DII Net: Loading...", font=("Helvetica", 14))
        self.lbl_dii.pack(pady=10, anchor="w")
        ttk.Button(card_fii, text="Refresh Now", bootstyle="info-outline", command=self.update_fii_dii).pack(pady=10)
        self.lbl_fii_time = ttk.Label(card_fii, text="Last Updated: --", font=("Arial", 8), foreground="grey")
        self.lbl_fii_time.pack()

        # 3. OI Analysis Card
        card_oi = ttk.Labelframe(f_grid, text="Live OI Analysis", padding=10)
        card_oi.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

        # Nifty OI Change
        self.lbl_nifty_oi = ttk.Label(card_oi, text="Nifty OI Chg: 0%", font=("Helvetica", 12))
        self.lbl_nifty_oi.pack(anchor="w", pady=5)

        # Buildup Status
        self.lbl_buildup = ttk.Label(card_oi, text="Status: Neutral", font=("Helvetica", 12, "bold"))
        self.lbl_buildup.pack(anchor="w", pady=5)

        # Signal
        self.lbl_signal = ttk.Label(card_oi, text="SIGNAL: WAIT", font=("Helvetica", 14, "bold"), bootstyle="secondary-inverse")
        self.lbl_signal.pack(anchor="center", pady=10)

        # System Status
        f_sys = ttk.Labelframe(self.f_dash, text="System Status", padding=10)
        f_sys.pack(fill=tk.X, pady=10)
        self.lbl_open_pos = ttk.Label(f_sys, text="Open Positions: 0", bootstyle="warning")
        self.lbl_open_pos.pack(side=tk.LEFT, padx=10)
        ttk.Button(f_sys, text="Panic EXIT ALL", bootstyle="danger", command=self.panic_exit).pack(side=tk.RIGHT)

    def add_indices_content(self):
        # ... (Same as before)
        def add_header(txt):
            lbl = ttk.Label(self.idx_content, text=txt, font=("Arial", 10, "bold"), foreground="#00bc8c", background="#2b2b2b")
            lbl.pack(fill=tk.X, pady=(15, 5), padx=5)

        def add_row(name):
            f = ttk.Frame(self.idx_content)
            f.pack(fill=tk.X, pady=2, padx=5)
            n = ttk.Label(f, text=name, width=15, font=("Arial", 9))
            n.pack(side=tk.LEFT)
            l = ttk.Label(f, text="--", width=10, font=("Arial", 9, "bold"))
            l.pack(side=tk.LEFT)
            c = ttk.Label(f, text="--", width=10, font=("Arial", 9))
            c.pack(side=tk.LEFT)
            self.indices_widgets[name] = (l, c)

        add_header("INDIAN INDICES")
        for i in ["NIFTY 50", "BANKNIFTY", "FINNIFTY", "SENSEX", "INDIA VIX"]: add_row(i)
        add_header("GLOBAL INDICES")
        for i in ["Dow Jones", "S&P 500", "Nasdaq", "DAX", "FTSE"]: add_row(i)
        add_header("COMMODITIES")
        for i in ["Gold", "Silver", "Crude Oil", "Brent Crude"]: add_row(i)

    def toggle_engine(self): pass

    def panic_exit(self):
        if self.context.get('risk_engine'):
            self.context['risk_engine'].emergency_stop()

    def update_fii_dii(self):
        de = self.context.get('data_engine')
        if de:
            data = de.get_fii_dii()
            self.lbl_fii.config(text=f"FII Net: {data.get('fii', '--')}")
            self.lbl_dii.config(text=f"DII Net: {data.get('dii', '--')}")
            self.lbl_fii_time.config(text=f"Last Updated: {data.get('last_updated', '--')}")

    def update_ui(self):
        import time
        self.lbl_time.config(text=time.strftime("%H:%M:%S"))

        broker = self.context.get('broker')
        connected = broker and getattr(broker, 'connected', False)
        self.lbl_broker.config(text="Connected" if connected else "Disconnected", bootstyle="success" if connected else "danger")

        de = self.context.get('data_engine')
        global_data = global_market_scraper.get_data()

        # 1. Update Indices and OI Analysis
        for name, widgets in self.indices_widgets.items():
            lbl_ltp, lbl_chg = widgets
            price, change, pct = 0, 0, 0

            # Local Data (Upstox)
            if de:
                q = de.get_latest_tick(name)
                if q.get('ltp'):
                    price = q['ltp']
                    change = q['change']
                    pct = q['pct_change']

                    # OI Logic for Nifty 50 only (Demo)
                    if name == "NIFTY 50":
                        self.update_oi_card(q)

            # Global Fallback
            if price == 0:
                 for reg, items in global_data.items():
                    if name in items:
                        d = items[name]
                        price, change, pct = d['price'], d['change'], d['pct']

            if price != 0:
                lbl_ltp.config(text=f"{price:,.2f}")
                lbl_chg.config(text=f"{change:+.2f} ({pct:+.2f}%)")
                color = "success" if change >= 0 else "danger"
                lbl_ltp.config(bootstyle=color)
                lbl_chg.config(bootstyle=color)

        self.update_fii_dii()
        self.after(500, self.update_ui)

    def update_oi_card(self, tick_data):
        # Logic:
        # Price Up, OI Up -> Long Buildup (Green)
        # Price Down, OI Up -> Short Buildup (Red)
        # Price Down, OI Down -> Long Unwinding (Orange)
        # Price Up, OI Down -> Short Covering (Blue)

        current_oi = tick_data.get('oi', 0)
        initial_oi = tick_data.get('initial_oi', 0)
        price_change = tick_data.get('change', 0)

        if initial_oi > 0:
            oi_change_pct = ((current_oi - initial_oi) / initial_oi) * 100
            self.lbl_nifty_oi.config(text=f"Nifty OI Chg: {oi_change_pct:+.2f}%")

            status = "Neutral"
            color = "secondary"
            signal = "WAIT"
            sig_color = "secondary-inverse"

            # Simple threshold for noise
            if abs(oi_change_pct) > 0.1:
                if price_change > 0 and oi_change_pct > 0:
                    status = "Long Buildup"
                    color = "success"
                    signal = "BUY"
                    sig_color = "success"
                elif price_change < 0 and oi_change_pct > 0:
                    status = "Short Buildup"
                    color = "danger"
                    signal = "SELL"
                    sig_color = "danger"
                elif price_change < 0 and oi_change_pct < 0:
                    status = "Long Unwinding"
                    color = "warning"
                    signal = "EXIT BUY"
                    sig_color = "warning"
                elif price_change > 0 and oi_change_pct < 0:
                    status = "Short Covering"
                    color = "info"
                    signal = "EXIT SELL"
                    sig_color = "info"

            self.lbl_buildup.config(text=f"Status: {status}", bootstyle=color)
            self.lbl_signal.config(text=f"SIGNAL: {signal}", bootstyle=sig_color)
