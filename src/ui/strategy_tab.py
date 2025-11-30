import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb

class StrategyTab(ttk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.context = context
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Strategy Selector
        frame_top = ttk.Frame(self)
        frame_top.pack(fill=tk.X, pady=10)

        ttk.Label(frame_top, text="Select Strategy:").pack(side=tk.LEFT, padx=5)
        self.combo_strategy = ttk.Combobox(frame_top, values=["SMA_RSI"]) # Currently only one implemented
        self.combo_strategy.current(0)
        self.combo_strategy.pack(side=tk.LEFT, padx=5)

        # Parameters Grid
        self.frame_params = ttk.LabelFrame(self, text="Strategy Parameters")
        self.frame_params.pack(fill=tk.X, pady=10)

        self.create_param_input("Capital Allocation", "10000", 0)
        self.create_param_input("Stop Loss %", "1.0", 1)
        self.create_param_input("Target %", "2.0", 2)
        self.create_param_input("Trailing SL (Bool)", "True", 3)

        # Control Buttons
        frame_controls = ttk.Frame(self)
        frame_controls.pack(fill=tk.X, pady=20)

        self.btn_start = ttk.Button(frame_controls, text="START STRATEGY", bootstyle="success", command=self.start_strategy)
        self.btn_start.pack(side=tk.LEFT, padx=20, expand=True, fill=tk.X)

        self.btn_stop = ttk.Button(frame_controls, text="STOP STRATEGY", bootstyle="danger", command=self.stop_strategy)
        self.btn_stop.pack(side=tk.RIGHT, padx=20, expand=True, fill=tk.X)
        self.btn_stop.config(state="disabled")

        # Live Signals Log
        ttk.Label(self, text="Strategy Logs / Signals:").pack(anchor="w")
        self.txt_log = tk.Text(self, height=10)
        self.txt_log.pack(fill=tk.BOTH, expand=True)

    def create_param_input(self, label, default, row):
        ttk.Label(self.frame_params, text=label).grid(row=row, column=0, padx=5, pady=5, sticky="e")
        entry = ttk.Entry(self.frame_params)
        entry.insert(0, default)
        entry.grid(row=row, column=1, padx=5, pady=5, sticky="w")

    def start_strategy(self):
        strategy_name = self.combo_strategy.get()
        strategies = self.context.get("strategies", [])

        # Find the strategy instance
        target_strat = next((s for s in strategies if s.name == strategy_name), None)

        if target_strat:
            target_strat.start()
            self.btn_start.config(state="disabled")
            self.btn_stop.config(state="normal")
            self.log_message(f"Started {strategy_name}")
        else:
            self.log_message(f"Error: Strategy {strategy_name} not found in context.")

    def stop_strategy(self):
        strategy_name = self.combo_strategy.get()
        strategies = self.context.get("strategies", [])

        target_strat = next((s for s in strategies if s.name == strategy_name), None)

        if target_strat:
            target_strat.stop()
            self.btn_start.config(state="normal")
            self.btn_stop.config(state="disabled")
            self.log_message(f"Stopped {strategy_name}")

    def log_message(self, msg):
        self.txt_log.insert(tk.END, msg + "\n")
        self.txt_log.see(tk.END)
