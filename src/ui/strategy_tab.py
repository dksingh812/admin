import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from src.ui.widgets import SearchableCombobox
from src.instrument_manager import instrument_manager
from src.logger import logger

class StrategyTab(ttk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.context = context
        self.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Layout
        left_col = ttk.Frame(self)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        right_col = ttk.Frame(self)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # --- CONFIGURATION (Left) ---
        config_card = ttk.Labelframe(left_col, text="Strategy Configuration", padding=15, bootstyle="primary")
        config_card.pack(fill=tk.BOTH, expand=True)

        # 1. Base Symbol
        ttk.Label(config_card, text="Underlying Symbol (e.g. NIFTY)", font=("Helvetica", 10, "bold")).pack(anchor="w")
        self.combo_symbol = SearchableCombobox(config_card, all_values=[])
        self.combo_symbol.pack(fill=tk.X, pady=(0, 10))
        self.refresh_symbols()

        # 2. Strategy Logic
        ttk.Label(config_card, text="Signal Logic", font=("Helvetica", 10, "bold")).pack(anchor="w")
        self.combo_strategy = ttk.Combobox(config_card, values=["SMA_RSI_Options"], state="readonly")
        self.combo_strategy.current(0)
        self.combo_strategy.pack(fill=tk.X, pady=(0, 10))

        # 3. Leg Builder
        leg_frame = ttk.LabelFrame(config_card, text="Option Legs Manager", padding=10)
        leg_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Leg Input Row (Grid layout for more fields)
        input_row = ttk.Frame(leg_frame)
        input_row.pack(fill=tk.X, pady=5)

        # Headers for Input
        headers = ["Type", "Strike", "Action", "Qty", "Tgt%", "SL%", "Trail%", "Buf%"]
        for i, h in enumerate(headers):
            ttk.Label(input_row, text=h, font=("Arial", 8)).grid(row=0, column=i, padx=2)

        # Inputs
        self.var_type = tk.StringVar(value="CE")
        ttk.Combobox(input_row, textvariable=self.var_type, values=["CE", "PE", "FUT"], width=4, state="readonly").grid(row=1, column=0, padx=2)

        self.var_strike = tk.StringVar(value="ATM")
        ttk.Combobox(input_row, textvariable=self.var_strike, values=["ATM", "ATM+100", "ATM-100", "ATM+200", "ATM-200"], width=8).grid(row=1, column=1, padx=2)

        self.var_action = tk.StringVar(value="BUY")
        ttk.Combobox(input_row, textvariable=self.var_action, values=["BUY", "SELL"], width=4, state="readonly").grid(row=1, column=2, padx=2)

        self.var_qty = tk.StringVar(value="1")
        ttk.Entry(input_row, textvariable=self.var_qty, width=4).grid(row=1, column=3, padx=2)

        self.var_tgt = tk.StringVar(value="10.0")
        ttk.Entry(input_row, textvariable=self.var_tgt, width=4).grid(row=1, column=4, padx=2)

        self.var_sl = tk.StringVar(value="5.0")
        ttk.Entry(input_row, textvariable=self.var_sl, width=4).grid(row=1, column=5, padx=2)

        self.var_trail = tk.StringVar(value="0.0")
        ttk.Entry(input_row, textvariable=self.var_trail, width=4).grid(row=1, column=6, padx=2)

        self.var_buf = tk.StringVar(value="0.0")
        ttk.Entry(input_row, textvariable=self.var_buf, width=4).grid(row=1, column=7, padx=2)

        ttk.Button(input_row, text="+", command=self.add_leg, bootstyle="success-outline", width=3).grid(row=1, column=8, padx=5)

        # Leg List (Treeview)
        cols = ("type", "strike", "action", "qty", "tgt", "sl", "trail", "buf")
        self.tree_legs = ttk.Treeview(leg_frame, columns=cols, show="headings", height=5)

        self.tree_legs.heading("type", text="Type")
        self.tree_legs.heading("strike", text="Strk")
        self.tree_legs.heading("action", text="Side")
        self.tree_legs.heading("qty", text="Q")
        self.tree_legs.heading("tgt", text="Tgt")
        self.tree_legs.heading("sl", text="SL")
        self.tree_legs.heading("trail", text="Trl")
        self.tree_legs.heading("buf", text="Buf")

        for c in cols:
            self.tree_legs.column(c, width=40, anchor="center")
        self.tree_legs.column("strike", width=70)

        self.tree_legs.pack(fill=tk.BOTH, expand=True, pady=5)

        ttk.Button(leg_frame, text="Remove Selected Leg", command=self.remove_leg, bootstyle="danger-outline").pack(pady=5)

        # 4. Global Params
        params_frame = ttk.LabelFrame(config_card, text="Global Risk", padding=10)
        params_frame.pack(fill=tk.X, pady=10)
        self.create_param_input(params_frame, "Max Capital (₹)", "50000", 0)
        self.create_param_input(params_frame, "Max Loss/Day (₹)", "5000", 1)

        # Controls
        btn_frame = ttk.Frame(config_card)
        btn_frame.pack(fill=tk.X, pady=20)
        self.btn_start = ttk.Button(btn_frame, text="START STRATEGY", bootstyle="success", command=self.start_strategy)
        self.btn_start.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.btn_stop = ttk.Button(btn_frame, text="STOP", bootstyle="danger", command=self.stop_strategy, state="disabled")
        self.btn_stop.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

        # --- LOGS (Right) ---
        log_card = ttk.Labelframe(right_col, text="Strategy Logs", padding=15)
        log_card.pack(fill=tk.BOTH, expand=True)
        self.txt_log = tk.Text(log_card, height=20, font=("Consolas", 9))
        self.txt_log.pack(fill=tk.BOTH, expand=True)

    def refresh_symbols(self):
        all_symbols = instrument_manager.get_all_symbols()
        if all_symbols:
            self.combo_symbol.set_values(all_symbols)
        else:
            self.combo_symbol.set_values(["Loading..."])
            self.after(2000, self.refresh_symbols)

    def create_param_input(self, parent, label, default, row):
        ttk.Label(parent, text=label).grid(row=row, column=0, padx=5, pady=5, sticky="e")
        entry = ttk.Entry(parent, width=15)
        entry.insert(0, default)
        entry.grid(row=row, column=1, padx=5, pady=5, sticky="w")

    def add_leg(self):
        leg = (
            self.var_type.get(), self.var_strike.get(), self.var_action.get(), self.var_qty.get(),
            self.var_tgt.get(), self.var_sl.get(), self.var_trail.get(), self.var_buf.get()
        )
        self.tree_legs.insert("", "end", values=leg)

    def remove_leg(self):
        sel = self.tree_legs.selection()
        for item in sel:
            self.tree_legs.delete(item)

    def start_strategy(self):
        symbol = self.combo_symbol.get()
        if not symbol or "Loading" in symbol:
            self.log_message("Error: Select a valid underlying.")
            return

        legs = []
        for child in self.tree_legs.get_children():
            legs.append(self.tree_legs.item(child)["values"])

        self.log_message(f"Starting on {symbol} with {len(legs)} legs...")

        # Subscribe
        data_engine = self.context.get("data_engine")
        if data_engine:
            data_engine.subscribe([symbol])

        # Configure Strategy
        strategies = self.context.get("strategies", [])
        if strategies:
            s = strategies[0]
            s.set_symbol(symbol)
            s.legs = legs # Inject updated legs structure
            if s.start():
                self.btn_start.config(state="disabled")
                self.btn_stop.config(state="normal")
            else:
                self.log_message("Failed to start.")

    def stop_strategy(self):
        strategies = self.context.get("strategies", [])
        if strategies:
            strategies[0].stop()
            self.btn_start.config(state="normal")
            self.btn_stop.config(state="disabled")
            self.log_message("Stopped.")

    def log_message(self, msg):
        self.txt_log.insert(tk.END, f">> {msg}\n")
        self.txt_log.see(tk.END)
