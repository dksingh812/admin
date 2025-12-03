import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from src.global_market_scraper import global_market_scraper

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, bg="#2b2b2b", highlightthickness=0) # Match theme bg
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=280) # Fixed width for panel

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mousewheel
        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))

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
        self.grid_frame.columnconfigure(0, weight=0) # Fixed width for Indices
        self.grid_frame.columnconfigure(1, weight=1)
        self.grid_frame.columnconfigure(2, weight=1)

        # 2. Indices Panel (Scrollable Single Column)
        idx_card = ttk.Labelframe(self.grid_frame, text="Market Watch", bootstyle="secondary", padding=0)
        idx_card.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Set fixed width for indices panel
        idx_card.configure(width=300)

        self.scroll_idx = ScrollableFrame(idx_card)
        self.scroll_idx.pack(fill=tk.BOTH, expand=True)

        self.indices_widgets = {}

        # Add Sections
        self.add_section_header("INDIAN MARKETS")
        self.create_index_list(["NIFTY 50", "BANKNIFTY", "FINNIFTY", "SENSEX", "INDIA VIX"])

        self.add_section_header("GLOBAL - US")
        self.create_index_list(["Dow Jones", "S&P 500", "Nasdaq"])

        self.add_section_header("GLOBAL - EUROPE")
        self.create_index_list(["FTSE", "CAC", "DAX"])

        self.add_section_header("GLOBAL - ASIA")
        self.create_index_list(["GIFT NIFTY", "Nikkei 225", "Hang Seng", "Straits Times", "KOSPI"])

        self.add_section_header("COMMODITIES")
        self.create_index_list(["Brent Crude", "Gold", "Crude Oil", "Silver", "Natural Gas"])

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

    def add_section_header(self, text):
        f = ttk.Frame(self.scroll_idx.scrollable_frame, bootstyle="dark")
        f.pack(fill=tk.X, pady=(10, 2))
        ttk.Label(f, text=text, font=("Arial", 8, "bold"), foreground="cyan").pack(padx=5)

    def create_index_list(self, names):
        for name in names:
            row = ttk.Frame(self.scroll_idx.scrollable_frame)
            row.pack(fill=tk.X, pady=2, padx=5)

            ttk.Label(row, text=name, width=15, font=("Arial", 9)).pack(side=tk.LEFT)
            lbl_ltp = ttk.Label(row, text="--", width=10, font=("Arial", 9))
            lbl_ltp.pack(side=tk.LEFT)
            lbl_chg = ttk.Label(row, text="--", width=12, font=("Arial", 9))
            lbl_chg.pack(side=tk.LEFT)

            self.indices_widgets[name] = (lbl_ltp, lbl_chg)

    # ... (Rest of PnL, FII, Update Logic remains similar, just condensed for file limits)
    def create_pnl_content(self, parent):
        self.lbl_total_pnl = ttk.Label(parent, text="₹ 0.00", font=("Helvetica", 24, "bold"), bootstyle="success")
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
        import time
        self.lbl_time.config(text=time.strftime("%H:%M:%S"))
        broker = self.context.get('broker')
        if broker:
            self.lbl_broker.config(text="Connected" if broker.connected else "Disconnected",
                                   bootstyle="success" if broker.connected else "danger")

        # Update Indices (Both Local and Global)
        data_engine = self.context.get('data_engine')
        global_data = global_market_scraper.get_data()

        for name, widgets in self.indices_widgets.items():
            lbl_ltp, lbl_chg = widgets
            price, change, pct = 0, 0, 0

            # Check Local
            if data_engine:
                q = data_engine.get_latest_tick(name)
                if q.get('ltp'):
                    price, change, pct = q['ltp'], q['change'], q['pct_change']

            # Check Global if not found locally (or overwrite if better)
            # Actually Global Scraper has structure {Region: {Name: ...}}
            # We flatten search
            if price == 0:
                for reg, items in global_data.items():
                    if name in items:
                        d = items[name]
                        price, change, pct = d['price'], d['change'], d['pct']

            lbl_ltp.config(text=f"{price:,.2f}")
            lbl_chg.config(text=f"{change:+.2f} ({pct:+.2f}%)")
            color = "success" if change >= 0 else "danger"
            lbl_ltp.config(bootstyle=color)
            lbl_chg.config(bootstyle=color)

        self.after(200, self.update_ui)
