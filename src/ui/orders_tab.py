import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from datetime import datetime

class OrdersTab(ttk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.context = context
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Split Layout: Top (Positions) / Bottom (Orders)
        self.paned = ttk.PanedWindow(self, orient=tk.VERTICAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        # 1. Top Pane: Positions
        self.f_pos = ttk.Labelframe(self.paned, text="Net Positions", padding=5)
        self.paned.add(self.f_pos, weight=1)

        self._init_positions_table()

        # 2. Bottom Pane: Orders (Open / Closed)
        self.f_orders = ttk.Labelframe(self.paned, text="Order Book", padding=5)
        self.paned.add(self.f_orders, weight=1)

        self._init_orders_table()

        # Auto refresh loop
        self.refresh_loop()

    def _init_positions_table(self):
        # Columns
        cols = ("inst", "qty", "entry", "ltp", "pnl", "tgt", "sl", "tsl")
        self.tree_pos = ttk.Treeview(self.f_pos, columns=cols, show="headings", bootstyle="info", height=8, selectmode="extended")

        headers = {
            "inst": "Instrument", "qty": "Net Qty", "entry": "Avg Price",
            "ltp": "LTP", "pnl": "PnL", "tgt": "Target",
            "sl": "Stop Loss", "tsl": "Trailed SL"
        }

        for k, v in headers.items():
            self.tree_pos.heading(k, text=v)
            width = 150 if k == "inst" else 80
            self.tree_pos.column(k, width=width, anchor="center")

        scrollbar = ttk.Scrollbar(self.f_pos, orient="vertical", command=self.tree_pos.yview)
        self.tree_pos.configure(yscrollcommand=scrollbar.set)

        self.tree_pos.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Controls (Bottom of Positions)
        btn_frame = ttk.Frame(self.f_pos)
        btn_frame.pack(side="bottom", fill="x", pady=5)

        # Added explicit multi-selection hint
        ttk.Label(btn_frame, text="(Use Ctrl/Shift to select multiple)", font=("Arial", 8), foreground="grey").pack(side=tk.LEFT, padx=5)

        ttk.Button(btn_frame, text="EXIT SELECTED", command=self.exit_selected_pos, bootstyle="warning").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="EXIT ALL", command=self.exit_all_pos, bootstyle="danger").pack(side=tk.RIGHT, padx=5)

    def _init_orders_table(self):
        # Filter Tabs (Open / All)
        self.nb_orders = ttk.Notebook(self.f_orders)
        self.nb_orders.pack(fill=tk.BOTH, expand=True)

        # Open Orders Tab
        self.tab_open_ord = ttk.Frame(self.nb_orders)
        self.nb_orders.add(self.tab_open_ord, text="Open / Pending")

        # All Orders Tab
        self.tab_all_ord = ttk.Frame(self.nb_orders)
        self.nb_orders.add(self.tab_all_ord, text="Order History")

        # Setup Tree for Open
        cols = ("id", "time", "inst", "type", "qty", "price", "status")
        self.tree_open_ord = ttk.Treeview(self.tab_open_ord, columns=cols, show="headings", height=8, selectmode="extended")

        for c in cols:
            self.tree_open_ord.heading(c, text=c.upper())
            self.tree_open_ord.column(c, width=80, anchor="center")
        self.tree_open_ord.column("inst", width=120)
        self.tree_open_ord.pack(fill=tk.BOTH, expand=True)

        # Setup Tree for All
        self.tree_all_ord = ttk.Treeview(self.tab_all_ord, columns=cols, show="headings", height=8, selectmode="extended")
        for c in cols:
            self.tree_all_ord.heading(c, text=c.upper())
            self.tree_all_ord.column(c, width=80, anchor="center")
        self.tree_all_ord.column("inst", width=120)
        self.tree_all_ord.pack(fill=tk.BOTH, expand=True)

        # Cancel Button for Open Orders
        btn_frame_ord = ttk.Frame(self.tab_open_ord)
        btn_frame_ord.pack(pady=5, fill="x")
        ttk.Label(btn_frame_ord, text="(Use Ctrl/Shift to select multiple)", font=("Arial", 8), foreground="grey").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame_ord, text="Cancel Selected", command=self.cancel_selected_order, bootstyle="danger-outline").pack(side=tk.LEFT, padx=5)

    def refresh_loop(self):
        self.update_positions()
        self.update_orders()
        self.after(1000, self.refresh_loop)

    def update_positions(self):
        # Save selection
        sel_items = self.tree_pos.selection()
        sel_symbols = []
        for i in sel_items:
            try: sel_symbols.append(self.tree_pos.item(i)['values'][0])
            except: pass

        # 1. Clear
        for i in self.tree_pos.get_children(): self.tree_pos.delete(i)

        broker = self.context.get('broker')
        strategies = self.context.get('strategies', [])

        # 2. Get Broker Pos
        broker_positions = {}
        if broker and getattr(broker, 'connected', False):
            try:
                raw = broker.get_positions()
                for p in raw:
                    sym = getattr(p, 'tradingsymbol', 'Unknown')
                    qty = getattr(p, 'quantity', 0)
                    if qty != 0:
                        broker_positions[sym] = {
                            "qty": qty,
                            "avg": getattr(p, 'average_price', 0.0),
                            "ltp": getattr(p, 'last_price', 0.0)
                        }
            except: pass

        # 3. Get Strategy Logical Info
        strat_info = {}
        for s in strategies:
            for p in s.active_positions:
                if p['status'] == 'OPEN':
                    strat_info[p['symbol']] = {
                        "sl": p.get('sl'), "tgt": p.get('tgt'), "tsl": p.get('sl') # TSL modifies SL usually
                    }

        # 4. Render
        for sym, data in broker_positions.items():
            qty = data['qty']
            avg = data['avg']
            ltp = data['ltp']
            pnl = (ltp - avg) * qty

            info = strat_info.get(sym, {})
            sl = info.get('sl', '-')
            tgt = info.get('tgt', '-')
            tsl = info.get('tsl', '-') # Simplification

            sl_s = f"{sl:.2f}" if isinstance(sl, float) else sl
            tgt_s = f"{tgt:.2f}" if isinstance(tgt, float) else tgt
            tsl_s = f"{tsl:.2f}" if isinstance(tsl, float) else tsl

            tags = ("profit",) if pnl >= 0 else ("loss",)
            item_id = self.tree_pos.insert("", "end", values=(
                sym, qty, f"{avg:.2f}", f"{ltp:.2f}", f"{pnl:.2f}", tgt_s, sl_s, tsl_s
            ), tags=tags)

            # Reselect
            if sym in sel_symbols:
                self.tree_pos.selection_add(item_id)

        self.tree_pos.tag_configure("profit", foreground="#00bc8c") # Success color
        self.tree_pos.tag_configure("loss", foreground="#e74c3c")   # Danger color

    def update_orders(self):
        # Similar Logic for orders (omitted deep re-selection logic for brevity)
        # Clear
        for i in self.tree_open_ord.get_children(): self.tree_open_ord.delete(i)
        for i in self.tree_all_ord.get_children(): self.tree_all_ord.delete(i)

        broker = self.context.get('broker')
        if not broker or not getattr(broker, 'connected', False): return

        try:
            orders = broker.get_orders() # List of order objects
            # Reverse to show newest first
            for o in reversed(orders):
                oid = getattr(o, 'order_id', '-')
                otime = getattr(o, 'order_timestamp', '-')
                osym = getattr(o, 'tradingsymbol', '-')
                otype = getattr(o, 'transaction_type', '-')
                oqty = getattr(o, 'quantity', 0)
                oprice = getattr(o, 'price', 0.0)
                ostatus = getattr(o, 'status', 'UNKNOWN')

                vals = (oid, otime, osym, otype, oqty, oprice, ostatus)

                # Add to All
                self.tree_all_ord.insert("", "end", values=vals)

                # Add to Open if active
                if ostatus in ["open", "trigger pending", "validation pending"]:
                    self.tree_open_ord.insert("", "end", values=vals)

        except: pass

    def exit_selected_pos(self):
        sel = self.tree_pos.selection()
        broker = self.context.get('broker')
        if not broker: return
        for item in sel:
            vals = self.tree_pos.item(item)['values']
            sym, qty = vals[0], int(vals[1])
            side = "SELL" if qty > 0 else "BUY"
            broker.place_order(sym, abs(qty), side)

    def exit_all_pos(self):
        # Panic Logic already exists in RiskEngine/HomeTab, duplicating simpler version here
        broker = self.context.get('broker')
        if not broker: return
        for item in self.tree_pos.get_children():
            vals = self.tree_pos.item(item)['values']
            sym, qty = vals[0], int(vals[1])
            side = "SELL" if qty > 0 else "BUY"
            broker.place_order(sym, abs(qty), side)

    def cancel_selected_order(self):
        sel = self.tree_open_ord.selection()
        broker = self.context.get('broker')
        if not broker: return
        for item in sel:
            oid = self.tree_open_ord.item(item)['values'][0]
            # broker.cancel_order(oid) # Assuming method exists
            pass
