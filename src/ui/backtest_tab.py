import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
from src.backtest_engine import BacktestEngine
from src.strategies.builder_strategy import BuilderStrategy
from src.logger import logger

class BacktestTab(ttk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.context = context
        self.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.engine = BacktestEngine()

        # --- Top: Config ---
        f_cfg = ttk.Labelframe(self, text="Backtest Configuration", padding=10)
        f_cfg.pack(fill=tk.X, pady=10)

        ttk.Label(f_cfg, text="Symbol:").pack(side=tk.LEFT)
        self.v_sym = tk.StringVar(value="^NSEI")
        ttk.Entry(f_cfg, textvariable=self.v_sym, width=15).pack(side=tk.LEFT, padx=5)

        ttk.Label(f_cfg, text="Period:").pack(side=tk.LEFT, padx=10)
        self.v_per = tk.StringVar(value="1mo")
        ttk.Combobox(f_cfg, textvariable=self.v_per, values=["5d", "1mo", "3mo", "6mo", "1y"], width=5, state="readonly").pack(side=tk.LEFT)

        ttk.Label(f_cfg, text="Interval:").pack(side=tk.LEFT, padx=10)
        self.v_int = tk.StringVar(value="15m")
        ttk.Combobox(f_cfg, textvariable=self.v_int, values=["1m", "5m", "15m", "1h", "1d"], width=5, state="readonly").pack(side=tk.LEFT)

        ttk.Button(f_cfg, text="Run Backtest", bootstyle="success", command=self.run_backtest).pack(side=tk.LEFT, padx=20)

        # --- Results ---
        f_res = ttk.Frame(self)
        f_res.pack(fill=tk.BOTH, expand=True)

        # Left: Stats
        self.f_stats = ttk.Labelframe(f_res, text="Statistics", padding=10, width=300)
        self.f_stats.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.lbl_res = ttk.Label(self.f_stats, text="Run to see results.")
        self.lbl_res.pack()

        # Right: Chart
        self.f_chart = ttk.Frame(f_res)
        self.f_chart.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def run_backtest(self):
        sym = self.v_sym.get()
        per = self.v_per.get()
        inv = self.v_int.get()

        # 1. Download Data
        df = self.engine.download_data(sym, per, inv)
        if df is None or df.empty:
            self.lbl_res.config(text="No Data Found.")
            return

        # 2. Setup Strategy Config (Hardcoded or fetch from StrategyTab?)
        # For V1, we create a simple demo config or ask user to select a saved one.
        # I'll create a default "SMA Crossover" config for testing.
        config = {
            "name": "Backtest_SMA",
            "entry_conditions": [
                {"ind1": "SMA", "op": ">", "ind2": "LTP", "p1": {"period": 20}, "p2": {}}
            ],
            "legs": [
                ("CE", "ATM", "BUY", "1", "20", "Pts", "10", "Pts", "0", "Pts", "0", "Pts")
            ]
        }

        # 3. Run
        results = self.engine.run(BuilderStrategy, config, sym, df)

        # 4. Display
        self.lbl_res.config(text=f"Trades: {results.get('trades')}\nFinal Equity: N/A (WIP)")

        # 5. Plot Close Price
        for widget in self.f_chart.winfo_children(): widget.destroy()

        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(df.index, df['close'], label='Close')
        ax.set_title(f"{sym} Price History")
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=self.f_chart)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
