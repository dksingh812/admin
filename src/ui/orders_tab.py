import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb

class OrdersTab(ttk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.context = context
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title
        ttk.Label(self, text="Open Positions & Orders", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=5)

        # Columns
        # Instrument | Qty | Entry | Current | P&L | SL | Tgt | Time
        columns = ("inst", "qty", "entry", "ltp", "pnl", "sl", "tgt", "time")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", bootstyle="info", height=15)

        self.tree.heading("inst", text="Instrument")
        self.tree.heading("qty", text="Qty")
        self.tree.heading("entry", text="Entry ₹")
        self.tree.heading("ltp", text="LTP ₹")
        self.tree.heading("pnl", text="P&L ₹")
        self.tree.heading("sl", text="SL")
        self.tree.heading("tgt", text="Target")
        self.tree.heading("time", text="Time")

        self.tree.column("inst", width=150)
        self.tree.column("qty", width=50, anchor="center")
        self.tree.column("entry", width=80, anchor="e")
        self.tree.column("ltp", width=80, anchor="e")
        self.tree.column("pnl", width=80, anchor="e")
        self.tree.column("sl", width=60, anchor="center")
        self.tree.column("tgt", width=60, anchor="center")
        self.tree.column("time", width=80, anchor="center")

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Controls
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(btn_frame, text="Refresh", command=self.refresh_positions, bootstyle="secondary").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="EXIT SELECTED", command=self.exit_selected, bootstyle="warning").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="EXIT ALL POSITIONS", command=self.exit_all, bootstyle="danger").pack(side=tk.RIGHT, padx=5)

        # Auto refresh
        self.refresh_loop()

    def refresh_loop(self):
        self.refresh_positions()
        self.after(1000, self.refresh_loop) # 1 sec refresh

    def refresh_positions(self):
        # Save selection
        selected_ids = self.tree.selection()

        # Clear
        for i in self.tree.get_children():
            self.tree.delete(i)

        broker = self.context.get('broker')
        if not broker or not broker.connected:
            return

        try:
            positions = broker.get_positions()
            # positions is list of objects/dicts
            for p in positions:
                # Parse depending on API structure
                sym = getattr(p, 'tradingsymbol', 'Unknown')
                qty = getattr(p, 'quantity', 0)
                if qty == 0: continue # Skip closed

                avg = getattr(p, 'average_price', 0.0)
                ltp = getattr(p, 'last_price', 0.0)
                pnl = getattr(p, 'pnl', 0.0)

                # Mock SL/Tgt (Not in broker pos)
                sl = "-"
                tgt = "-"
                time_str = "00:00:00" # Placeholder

                # Insert
                item = self.tree.insert("", "end", values=(sym, qty, f"{avg:.2f}", f"{ltp:.2f}", f"{pnl:.2f}", sl, tgt, time_str))

                # Restore selection logic if item ID matched (complex, skipped for now)

        except Exception:
            pass

    def exit_selected(self):
        sel = self.tree.selection()
        if not sel: return

        broker = self.context.get('broker')
        for item in sel:
            vals = self.tree.item(item)['values']
            symbol = vals[0]
            qty = int(vals[1])
            if qty != 0:
                side = "SELL" if qty > 0 else "BUY"
                broker.place_order(symbol, abs(qty), side) # Close it

    def exit_all(self):
        # Loop through all items
        broker = self.context.get('broker')
        for item in self.tree.get_children():
            vals = self.tree.item(item)['values']
            symbol = vals[0]
            qty = int(vals[1])
            if qty != 0:
                side = "SELL" if qty > 0 else "BUY"
                broker.place_order(symbol, abs(qty), side)
