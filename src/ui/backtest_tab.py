import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import glob
import os
import json
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

        # Strategy Selector
        ttk.Label(f_cfg, text="Strategy:").pack(side=tk.LEFT)
        self.v_strat = tk.StringVar()
        self.cb_strat = ttk.Combobox(f_cfg, textvariable=self.v_strat, width=25, state="readonly")
        self.cb_strat.pack(side=tk.LEFT, padx=5)
        self.refresh_strategies()

        # Symbol
        ttk.Label(f_cfg, text="Symbol:").pack(side=tk.LEFT, padx=10)
        self.v_sym = tk.StringVar(value="^NSEI")
        ttk.Entry(f_cfg, textvariable=self.v_sym, width=15).pack(side=tk.LEFT, padx=5)

        # Period/Interval
        ttk.Label(f_cfg, text="Period:").pack(side=tk.LEFT, padx=10)
        self.v_per = tk.StringVar(value="3mo")
        ttk.Combobox(f_cfg, textvariable=self.v_per, values=["1mo", "3mo", "6mo", "1y", "2y"], width=5, state="readonly").pack(side=tk.LEFT)

        ttk.Label(f_cfg, text="Interval:").pack(side=tk.LEFT, padx=10)
        self.v_int = tk.StringVar(value="1d")
        ttk.Combobox(f_cfg, textvariable=self.v_int, values=["5m", "15m", "1h", "1d"], width=5, state="readonly").pack(side=tk.LEFT)

        ttk.Button(f_cfg, text="Run Backtest", bootstyle="success", command=self.run_backtest).pack(side=tk.LEFT, padx=20)
        ttk.Button(f_cfg, text="Refresh Strategies", bootstyle="info-outline", command=self.refresh_strategies).pack(side=tk.LEFT, padx=5)

        # --- Dashboard ---
        self.dash_scroll = ttk.Frame(self)
        self.dash_scroll.pack(fill=tk.BOTH, expand=True)

        # Use a canvas for scrolling if needed, but for now just frames
        self.f_summary = ttk.Frame(self.dash_scroll)
        self.f_summary.pack(fill=tk.X, pady=10)

        # Summary Cards
        self.cards = {}
        card_keys = ["Total Trades", "Win Rate", "Profit Factor", "Max Drawdown", "Total PnL", "Avg Trade"]
        for i, key in enumerate(card_keys):
            f = ttk.Frame(self.f_summary, bootstyle="secondary", padding=10, relief="solid", borderwidth=1)
            f.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            ttk.Label(f, text=key, font=("Helvetica", 8)).pack()
            l = ttk.Label(f, text="-", font=("Helvetica", 12, "bold"))
            l.pack()
            self.cards[key] = l

        # Charts Area
        self.f_charts = ttk.Frame(self.dash_scroll)
        self.f_charts.pack(fill=tk.BOTH, expand=True)

        # Left: Equity Curve
        self.f_equity = ttk.Frame(self.f_charts)
        self.f_equity.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # Right: Daywise Heatmap (Simulated via Matplotlib Grid)
        self.f_heatmap = ttk.Frame(self.f_charts)
        self.f_heatmap.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

    def refresh_strategies(self):
        files = glob.glob("Data/strategies/*.json")
        names = [os.path.basename(f) for f in files]
        self.cb_strat['values'] = names
        if names: self.cb_strat.current(0)

    def run_backtest(self):
        strat_file = self.v_strat.get()
        if not strat_file:
            messagebox.showerror("Error", "Please select a strategy.")
            return

        try:
            with open(f"Data/strategies/{strat_file}", "r") as f:
                config = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load strategy: {e}")
            return

        sym = self.v_sym.get()
        per = self.v_per.get()
        inv = self.v_int.get()

        self.cards["Total PnL"].config(text="Running...", foreground="black")
        self.update_idletasks()

        # Run
        df = self.engine.download_data(sym, per, inv)
        if df is None or df.empty:
            messagebox.showerror("Error", "No data found.")
            return

        results = self.engine.run(BuilderStrategy, config, sym, df)
        metrics = results["metrics"]

        # Update Cards
        self.cards["Total Trades"].config(text=str(metrics["total_trades"]))
        self.cards["Win Rate"].config(text=f"{metrics['win_rate']:.1f}%")

        pf = abs(metrics['max_profit'] / metrics['max_loss']) if metrics['max_loss'] != 0 else 0
        self.cards["Profit Factor"].config(text=f"{pf:.2f}")

        self.cards["Max Drawdown"].config(text=f"₹{metrics['max_drawdown']:.0f}", foreground="red")

        pnl = metrics["total_pnl"]
        color = "success" if pnl >= 0 else "danger"
        self.cards["Total PnL"].config(text=f"₹{pnl:.2f}", bootstyle=color)

        self.cards["Avg Trade"].config(text=f"₹{(metrics['avg_profit'] + metrics['avg_loss']):.2f}")

        # Plot Equity Curve
        self._plot_equity(results["equity_curve"])

        # Plot Heatmap (or Monthly Bar Chart)
        self._plot_daywise(results["day_pnl"])

    def _plot_equity(self, data):
        for widget in self.f_equity.winfo_children(): widget.destroy()

        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(data["equity"], color="blue", linewidth=1)
        ax.fill_between(range(len(data["equity"])), data["equity"], alpha=0.1, color="blue")
        ax.set_title("Equity Curve")
        ax.grid(True, alpha=0.3)

        canvas = FigureCanvasTkAgg(fig, master=self.f_equity)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def _plot_daywise(self, day_pnl):
        for widget in self.f_heatmap.winfo_children(): widget.destroy()

        if not day_pnl: return

        dates = list(day_pnl.keys())
        pnls = list(day_pnl.values())

        colors = ['green' if p > 0 else 'red' for p in pnls]

        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(dates, pnls, color=colors)
        ax.set_title("Daily PnL Breakdown")
        ax.tick_params(axis='x', rotation=45, labelsize=8)
        ax.grid(axis='y', alpha=0.3)

        # If too many dates, simplify x-axis
        if len(dates) > 10:
            ax.set_xticks(range(0, len(dates), len(dates)//10))

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.f_heatmap)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
