import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from datetime import datetime

class OrdersTab(ttk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.context = context
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Split into Open and Closed
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Live Positions
        self.tab_open = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_open, text="Live Positions")
        self._init_open_tab()

        # Tab 2: Closed History
        self.tab_closed = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_closed, text="Closed Positions")
        self._init_closed_tab()

        # Auto refresh
        self.refresh_loop()

    def _init_open_tab(self):
        # Columns
        # Instrument | Qty | Entry | LTP | PnL | Target | SL | Trailed SL | Time
        cols = ("inst", "qty", "entry", "ltp", "pnl", "tgt", "sl", "tsl", "time")
        self.tree_open = ttk.Treeview(self.tab_open, columns=cols, show="headings", bootstyle="info", height=15)

        headers = {
            "inst": "Instrument", "qty": "Qty", "entry": "Avg Price",
            "ltp": "LTP", "pnl": "PnL", "tgt": "Target",
            "sl": "Stop Loss", "tsl": "Trailed SL", "time": "Entry Time"
        }

        for k, v in headers.items():
            self.tree_open.heading(k, text=v)
            width = 150 if k == "inst" else 80
            self.tree_open.column(k, width=width, anchor="center")

        self.tree_open.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Controls
        btn_frame = ttk.Frame(self.tab_open)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="EXIT SELECTED", command=self.exit_selected, bootstyle="warning").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="EXIT ALL POSITIONS", command=self.exit_all, bootstyle="danger").pack(side=tk.RIGHT, padx=5)

    def _init_closed_tab(self):
        cols = ("inst", "qty", "entry", "exit", "pnl", "exit_time")
        self.tree_closed = ttk.Treeview(self.tab_closed, columns=cols, show="headings", height=15)

        self.tree_closed.heading("inst", text="Instrument")
        self.tree_closed.heading("qty", text="Qty")
        self.tree_closed.heading("entry", text="Entry Price")
        self.tree_closed.heading("exit", text="Exit Price")
        self.tree_closed.heading("pnl", text="Realized PnL")
        self.tree_closed.heading("exit_time", text="Exit Time")

        self.tree_closed.pack(fill=tk.BOTH, expand=True)

    def refresh_loop(self):
        self.update_live_positions()
        self.update_closed_positions()
        self.after(1000, self.refresh_loop)

    def update_live_positions(self):
        # Clear current
        for i in self.tree_open.get_children():
            self.tree_open.delete(i)

        # We need a unified view of positions.
        # The 'RiskEngine' or 'Strategy' tracks logical stops (SL/Target).
        # The 'Broker' tracks actual exchange positions.
        # We try to merge them.

        broker = self.context.get('broker')
        strategies = self.context.get('strategies', [])

        # 1. Gather Broker Positions (Base Truth)
        broker_positions = {}
        if broker and broker.connected:
            try:
                raw_pos = broker.get_positions()
                for p in raw_pos:
                    sym = getattr(p, 'tradingsymbol', 'Unknown')
                    qty = getattr(p, 'quantity', 0)
                    if qty != 0:
                        broker_positions[sym] = {
                            "qty": qty,
                            "avg": getattr(p, 'average_price', 0.0),
                            "ltp": getattr(p, 'last_price', 0.0),
                            "pnl": getattr(p, 'pnl', 0.0)
                        }
            except: pass

        # 2. Gather Strategy Logical Info (SL/Target)
        strategy_info = {}
        for s in strategies:
            for p in s.active_positions:
                if p['status'] == 'OPEN':
                    strategy_info[p['symbol']] = {
                        "sl": p.get('sl', 0.0),
                        "tgt": p.get('tgt', 0.0),
                        "tsl": p.get('sl', 0.0), # Assuming TSL updates the SL field
                        "time": "00:00" # TODO: Store entry time
                    }

        # 3. Merge and Display
        # Display everything from Broker (Real)
        for sym, data in broker_positions.items():
            qty = data['qty']
            avg = data['avg']
            ltp = data['ltp']
            pnl = (ltp - avg) * qty

            # Enrich with strategy info
            info = strategy_info.get(sym, {})
            sl = info.get('sl', '-')
            tgt = info.get('tgt', '-')
            tsl = info.get('tsl', '-')
            time_str = info.get('time', '-')

            # Formatting
            sl_str = f"{sl:.2f}" if isinstance(sl, float) else sl
            tgt_str = f"{tgt:.2f}" if isinstance(tgt, float) else tgt
            tsl_str = f"{tsl:.2f}" if isinstance(tsl, float) else tsl

            # Color PnL
            tags = ("profit",) if pnl >= 0 else ("loss",)

            self.tree_open.insert("", "end", values=(
                sym, qty, f"{avg:.2f}", f"{ltp:.2f}", f"{pnl:.2f}",
                tgt_str, sl_str, tsl_str, time_str
            ), tags=tags)

        self.tree_open.tag_configure("profit", foreground="green")
        self.tree_open.tag_configure("loss", foreground="red")

    def update_closed_positions(self):
        # This usually comes from a "TradeBook" or internal log
        # For V1, we can check if strategies store closed trades history
        # Or Broker.get_trades()

        # Avoid full redraw every second to prevent flicker?
        # Only redraw if count changes?
        # For simplicity V1: Redraw.

        for i in self.tree_closed.get_children():
            self.tree_closed.delete(i)

        broker = self.context.get('broker')
        if broker and hasattr(broker, 'trades'):
            # Assuming broker.trades is a list of completed trade dicts
            # We need to aggregate buys/sells to show "Closed Position PnL"
            # This is complex. For now, let's just list Strategy Closed positions if available.
            pass

        # Strategy Internal History fallback
        strategies = self.context.get('strategies', [])
        for s in strategies:
            # If strategy has a 'closed_positions' list
            if hasattr(s, 'active_positions'):
                for p in s.active_positions:
                    if p['status'] == 'CLOSED':
                        # Calculate PnL
                        entry = p['entry']
                        exit_p = p.get('exit_price', 0.0) # Need to record this
                        qty = p['qty']
                        mult = 1 if p['side'] == 'BUY' else -1
                        pnl = (exit_p - entry) * qty * mult if exit_p > 0 else 0.0

                        self.tree_closed.insert("", "end", values=(
                            p['symbol'], qty, f"{entry:.2f}", f"{exit_p:.2f}",
                            f"{pnl:.2f}", "Today"
                        ))

    def exit_selected(self):
        sel = self.tree_open.selection()
        broker = self.context.get('broker')
        if not broker: return

        for item in sel:
            vals = self.tree_open.item(item)['values']
            symbol = vals[0]
            qty = int(vals[1])
            side = "SELL" if qty > 0 else "BUY"
            broker.place_order(symbol, abs(qty), side)

    def exit_all(self):
        broker = self.context.get('broker')
        if not broker: return

        for item in self.tree_open.get_children():
            vals = self.tree_open.item(item)['values']
            symbol = vals[0]
            qty = int(vals[1])
            side = "SELL" if qty > 0 else "BUY"
            broker.place_order(symbol, abs(qty), side)
