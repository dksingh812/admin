import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb

class RiskTab(ttk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.context = context
        self.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(self, text="Risk Management", font=("Helvetica", 14, "bold")).pack(pady=10)

        # Current Risk State
        self.lbl_pnl = ttk.Label(self, text="Current Daily P&L: ₹0.00", font=("Helvetica", 12))
        self.lbl_pnl.pack(pady=5)

        # Configuration
        frame_config = ttk.LabelFrame(self, text="Safety Limits", padding=15)
        frame_config.pack(fill=tk.X, pady=10)

        self.create_entry(frame_config, "Max Daily Loss (₹)", "risk_max_loss", 0)
        self.create_entry(frame_config, "Max Open Trades", "risk_max_trades", 1)

        ttk.Button(self, text="Update Risk Limits", bootstyle="warning", command=self.save_risk).pack(pady=20)

        # Emergency Button
        ttk.Button(self, text="PANIC BUTTON: CLOSE ALL POSITIONS", bootstyle="danger", command=self.panic_close).pack(pady=20, fill=tk.X)

    def create_entry(self, parent, label, key, row):
        ttk.Label(parent, text=label).grid(row=row, column=0, padx=10, pady=10, sticky="e")
        entry = ttk.Entry(parent)
        # Load from config
        val = self.context['config']['risk'].get('max_loss_per_day' if 'loss' in key else 'max_open_trades', "")
        entry.insert(0, str(val))
        entry.grid(row=row, column=1, padx=10, pady=10, sticky="w")
        setattr(self, f"entry_{key}", entry)

    def save_risk(self):
        # Update context config
        try:
            max_loss = float(self.entry_risk_max_loss.get())
            max_trades = int(self.entry_risk_max_trades.get())

            self.context['config']['risk']['max_loss_per_day'] = max_loss
            self.context['config']['risk']['max_open_trades'] = max_trades

            # Update Engine
            self.context['risk_engine'].max_loss_daily = max_loss
            self.context['risk_engine'].max_open_trades = max_trades

            # Save to file
            from src.config import save_config
            save_config(self.context['config'])

            tk.messagebox.showinfo("Success", "Risk limits updated!")
        except ValueError:
            tk.messagebox.showerror("Error", "Invalid input values")

    def panic_close(self):
        if tk.messagebox.askyesno("Confirm", "Are you sure you want to close ALL positions?"):
            # Implement close all logic
            pass
