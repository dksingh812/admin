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

        # Two columns layout
        left_col = ttk.Frame(self)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        right_col = ttk.Frame(self)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # --- Left Column: Configuration ---
        config_card = ttk.Labelframe(left_col, text="Configuration", padding=15, bootstyle="primary")
        config_card.pack(fill=tk.BOTH, expand=True)

        # Strategy Selector
        ttk.Label(config_card, text="Strategy Algorithm", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.combo_strategy = ttk.Combobox(config_card, values=["SMA_RSI"], state="readonly")
        self.combo_strategy.current(0)
        self.combo_strategy.pack(fill=tk.X, pady=(0, 15))

        # Symbol Selector (Searchable)
        ttk.Label(config_card, text="Trading Symbol", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(0, 5))

        # We start with empty list, will populate if loaded
        self.combo_symbol = SearchableCombobox(config_card, all_values=[])
        self.combo_symbol.pack(fill=tk.X, pady=(0, 15))

        # Check if instruments are already loaded, else show placeholder
        self.refresh_symbols()

        # Parameters
        params_frame = ttk.LabelFrame(config_card, text="Parameters", padding=10)
        params_frame.pack(fill=tk.X, pady=10)

        self.create_param_input(params_frame, "Capital (₹)", "10000", 0)
        self.create_param_input(params_frame, "Stop Loss (%)", "1.0", 1)
        self.create_param_input(params_frame, "Target (%)", "2.0", 2)

        # Start/Stop Buttons
        btn_frame = ttk.Frame(config_card)
        btn_frame.pack(fill=tk.X, pady=20)

        self.btn_start = ttk.Button(btn_frame, text="START ENGINE", bootstyle="success", command=self.start_strategy)
        self.btn_start.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.btn_stop = ttk.Button(btn_frame, text="STOP ENGINE", bootstyle="danger", command=self.stop_strategy)
        self.btn_stop.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        self.btn_stop.config(state="disabled")

        # --- Right Column: Logs/Output ---
        log_card = ttk.Labelframe(right_col, text="Live Execution Logs", padding=15, bootstyle="secondary")
        log_card.pack(fill=tk.BOTH, expand=True)

        self.txt_log = tk.Text(log_card, height=20, font=("Consolas", 9))
        self.txt_log.pack(fill=tk.BOTH, expand=True)

    def refresh_symbols(self):
        all_symbols = instrument_manager.get_all_symbols()
        if all_symbols:
            self.combo_symbol.set_values(all_symbols)
        else:
            # Maybe loading?
            self.combo_symbol.set_values(["Loading Instruments...", "NIFTY 50", "BANKNIFTY"])
            # Retry after 2 seconds
            self.after(2000, self.refresh_symbols)

    def create_param_input(self, parent, label, default, row):
        ttk.Label(parent, text=label).grid(row=row, column=0, padx=5, pady=5, sticky="e")
        entry = ttk.Entry(parent, width=15)
        entry.insert(0, default)
        entry.grid(row=row, column=1, padx=5, pady=5, sticky="w")

    def start_strategy(self):
        symbol = self.combo_symbol.get()
        if not symbol or "Loading" in symbol:
            self.log_message("Error: Please select a valid symbol.")
            return

        self.log_message(f"Initializing Strategy on {symbol}...")

        # 1. Subscribe to Data Engine
        data_engine = self.context.get("data_engine")
        if data_engine:
            data_engine.subscribe([symbol])
            self.log_message(f"Subscribed to {symbol} feed.")

        # 2. Configure and Start Strategy
        strategies = self.context.get("strategies", [])
        if strategies:
            s = strategies[0]
            s.set_symbol(symbol)
            if s.start():
                self.btn_start.config(state="disabled")
                self.btn_stop.config(state="normal")
            else:
                self.log_message("Error: Failed to start strategy.")

    def stop_strategy(self):
        strategies = self.context.get("strategies", [])
        if strategies:
            strategies[0].stop()
            self.btn_start.config(state="normal")
            self.btn_stop.config(state="disabled")
            self.log_message("Strategy Stopped.")

    def log_message(self, msg):
        self.txt_log.insert(tk.END, f">> {msg}\n")
        self.txt_log.see(tk.END)
