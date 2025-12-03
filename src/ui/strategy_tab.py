import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from src.ui.widgets import SearchableCombobox
from src.instrument_manager import instrument_manager
from src.logger import logger
from src.strategies.builder_strategy import BuilderStrategy

class StrategyCard(ttk.Frame):
    def __init__(self, parent, strategy, on_stop, on_square_off):
        super().__init__(parent, bootstyle="secondary", padding=10)
        self.strategy = strategy
        self.on_stop = on_stop
        self.on_square_off = on_square_off
        self.pack(fill=tk.X, pady=5)

        lbl_name = ttk.Label(self, text=f"{strategy.target_symbol}\n{strategy.name}", font=("Helvetica", 10, "bold"))
        lbl_name.pack(side=tk.LEFT, padx=10)

        self.lbl_status = ttk.Label(self, text="RUNNING", bootstyle="success")
        self.lbl_status.pack(side=tk.LEFT, padx=20)

        self.lbl_pnl = ttk.Label(self, text="PnL: ₹0.00", font=("Helvetica", 10))
        self.lbl_pnl.pack(side=tk.LEFT, padx=20)

        ttk.Button(self, text="Square Off", bootstyle="danger-outline", command=self.square_off, width=10).pack(side=tk.RIGHT, padx=5)
        self.btn_toggle = ttk.Button(self, text="Stop", bootstyle="warning", command=self.toggle, width=8)
        self.btn_toggle.pack(side=tk.RIGHT, padx=5)

    def toggle(self):
        if self.strategy.active:
            self.strategy.stop()
            self.lbl_status.config(text="STOPPED", bootstyle="secondary")
            self.btn_toggle.config(text="Start", bootstyle="success")
        else:
            self.strategy.start()
            self.lbl_status.config(text="RUNNING", bootstyle="success")
            self.btn_toggle.config(text="Stop", bootstyle="warning")

    def square_off(self):
        self.strategy.stop()
        self.lbl_status.config(text="CLOSED", bootstyle="danger")
        self.on_square_off(self.strategy)

class StrategyTab(ttk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.context = context
        self.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        top = ttk.Frame(self)
        top.pack(fill=tk.X, pady=10)
        ttk.Label(top, text="Deployed Strategies", font=("Helvetica", 16, "bold")).pack(side=tk.LEFT)
        ttk.Button(top, text="+ Create New Strategy", bootstyle="primary", command=self.open_creator).pack(side=tk.RIGHT)

        self.dash_frame = ttk.Frame(self)
        self.dash_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(self.dash_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.dash_frame, orient="vertical", command=canvas.yview)
        self.card_list = ttk.Frame(canvas)

        self.card_list.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.card_list, anchor="nw", width=1100)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def add_strategy_card(self, strategy):
        if 'strategies' not in self.context: self.context['strategies'] = []
        self.context['strategies'].append(strategy)

        if self.context.get('data_engine'):
            self.context['data_engine'].register_strategy(strategy)
            self.context['data_engine'].subscribe([strategy.target_symbol])

        card = StrategyCard(self.card_list, strategy, lambda: None, self.square_off_strategy)

    def square_off_strategy(self, strategy):
        pass

    def open_creator(self):
        win = tb.Toplevel(self)
        win.title("Create Multi-Leg Strategy")
        win.geometry("1200x800")

        main_scroll = ttk.Frame(win)
        main_scroll.pack(fill=tk.BOTH, expand=True)

        # --- Top: Symbol & Config ---
        f_top = ttk.Frame(main_scroll, padding=10)
        f_top.pack(fill=tk.X)

        ttk.Label(f_top, text="Strategy Name:").pack(side=tk.LEFT, padx=5)
        v_name = tk.StringVar(value="My Strategy")
        ttk.Entry(f_top, textvariable=v_name, width=20).pack(side=tk.LEFT, padx=5)

        ttk.Label(f_top, text="Underlying Symbol:").pack(side=tk.LEFT, padx=10)
        cb_sym = SearchableCombobox(f_top, all_values=instrument_manager.get_all_symbols(), width=30)
        cb_sym.pack(side=tk.LEFT, padx=5)
        if instrument_manager.get_all_symbols(): cb_sym.set_values(instrument_manager.get_all_symbols())

        # --- Entry Conditions Section ---
        f_cond = ttk.Labelframe(main_scroll, text="Entry Conditions (AND Logic)", padding=10)
        f_cond.pack(fill=tk.X, padx=10, pady=5)

        cond_frame = ttk.Frame(f_cond)
        cond_frame.pack(fill=tk.X)

        conditions_list = []

        def add_condition_row():
            row = ttk.Frame(cond_frame)
            row.pack(fill=tk.X, pady=2)

            # Indicator 1
            i1 = ttk.Combobox(row, values=["LTP", "SMA", "EMA", "RSI", "VWAP", "SuperTrend", "Bollinger H", "Bollinger L"], width=12, state="readonly")
            i1.set("LTP")
            i1.pack(side=tk.LEFT, padx=2)

            # Comparator
            comp = ttk.Combobox(row, values=[">", "<", ">=", "<=", "==", "Cross Above", "Cross Below"], width=10, state="readonly")
            comp.set(">")
            comp.pack(side=tk.LEFT, padx=2)

            # Indicator 2 / Value
            i2 = ttk.Combobox(row, values=["Value", "LTP", "SMA", "EMA", "RSI", "VWAP"], width=12)
            i2.set("Value")
            i2.pack(side=tk.LEFT, padx=2)

            # Param 1 (Simple for now)
            p1_val = tk.StringVar(value="14")
            ttk.Entry(row, textvariable=p1_val, width=5).pack(side=tk.LEFT, padx=2)

            # Delete
            btn_del = ttk.Button(row, text="X", bootstyle="danger-link", command=lambda: remove_row(row, entry_obj))
            btn_del.pack(side=tk.LEFT, padx=5)

            entry_obj = {"row": row, "i1": i1, "comp": comp, "i2": i2, "p1": p1_val}
            conditions_list.append(entry_obj)

        def remove_row(row, obj):
            row.destroy()
            if obj in conditions_list: conditions_list.remove(obj)

        ttk.Button(f_cond, text="+ Add Condition", command=add_condition_row, bootstyle="info-outline").pack(anchor="w", pady=5)
        add_condition_row() # Add one by default

        # --- Legs Section ---
        f_list = ttk.Labelframe(main_scroll, text="Leg Builder", padding=10)
        f_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        cols = ("type", "strike", "action", "qty", "tgt", "sl", "trail")
        tree = ttk.Treeview(f_list, columns=cols, show="headings", height=5)

        for c in cols:
            tree.heading(c, text=c.upper())
            tree.column(c, width=80, anchor="center")
        tree.pack(fill=tk.BOTH, expand=True)

        ttk.Button(f_list, text="Remove Selected", bootstyle="danger-outline",
                   command=lambda: [tree.delete(x) for x in tree.selection()]).pack(anchor="e", pady=5)

        # --- Add Leg Form ---
        f_add = ttk.Frame(main_scroll, padding=10)
        f_add.pack(fill=tk.X, padx=10)

        # Row 1
        r1 = ttk.Frame(f_add)
        r1.pack(fill=tk.X, pady=5)

        ttk.Label(r1, text="Type:").pack(side=tk.LEFT)
        v_type = tk.StringVar(value="CE")
        ttk.Combobox(r1, textvariable=v_type, values=["CE","PE","FUT"], width=5, state="readonly").pack(side=tk.LEFT, padx=5)

        ttk.Label(r1, text="Strike:").pack(side=tk.LEFT, padx=10)
        v_str = tk.StringVar(value="ATM")

        # Generate Strikes List: ATM-400 ... ATM ... ATM+400
        strikes = []
        for i in range(400, 0, -50): strikes.append(f"ATM-{i}")
        strikes.append("ATM")
        for i in range(50, 450, 50): strikes.append(f"ATM+{i}")

        cb_str = ttk.Combobox(r1, textvariable=v_str, values=strikes, width=10, state="readonly")
        cb_str.pack(side=tk.LEFT, padx=5)

        ttk.Label(r1, text="Action:").pack(side=tk.LEFT, padx=10)
        v_act = tk.StringVar(value="BUY")
        ttk.Combobox(r1, textvariable=v_act, values=["BUY","SELL"], width=6, state="readonly").pack(side=tk.LEFT, padx=5)

        ttk.Label(r1, text="Qty:").pack(side=tk.LEFT, padx=10)
        v_qty = tk.StringVar(value="1")
        ttk.Entry(r1, textvariable=v_qty, width=5).pack(side=tk.LEFT, padx=5)

        # Row 2 (Risk)
        r2 = ttk.Frame(f_add)
        r2.pack(fill=tk.X, pady=5)

        def add_risk_field(label, val):
            ttk.Label(r2, text=label).pack(side=tk.LEFT, padx=5)
            v = tk.StringVar(value=val)
            ttk.Entry(r2, textvariable=v, width=5).pack(side=tk.LEFT)
            return v

        v_tgt = add_risk_field("Target(Pts):", "20")
        v_sl = add_risk_field("SL(Pts):", "10")
        v_trail = add_risk_field("Trail(Pts):", "0")

        def add_leg():
            tree.insert("", "end", values=(v_type.get(), v_str.get(), v_act.get(), v_qty.get(), v_tgt.get(), v_sl.get(), v_trail.get()))

        ttk.Button(r2, text="ADD LEG", bootstyle="success", command=add_leg).pack(side=tk.RIGHT, padx=20)

        # --- Deploy ---
        def deploy():
            sym = cb_sym.get()
            legs = []
            for item in tree.get_children():
                vals = tree.item(item)['values']
                # Transform to 12-item tuple expected by strategy (backwards compatibility)
                # type, strike, action, qty, tgt, tgt_u, sl, sl_u, trail, trail_u, buf, buf_u
                leg = (vals[0], vals[1], vals[2], vals[3], vals[4], "Pts", vals[5], "Pts", vals[6], "Pts", "0", "Pts")
                legs.append(leg)

            # Parse Conditions
            parsed_conds = []
            for c in conditions_list:
                parsed_conds.append({
                    "ind1": c["i1"].get(),
                    "op": c["comp"].get(),
                    "ind2": c["i2"].get(),
                    "p1": {"period": c["p1"].get()},
                    "p2": {"period": "14"} # Default
                })

            config = {
                "name": v_name.get(),
                "entry_conditions": parsed_conds,
                "legs": legs
            }

            broker = self.context.get('broker')
            strategy = BuilderStrategy(broker, config)
            strategy.set_symbol(sym)
            strategy.start()

            self.add_strategy_card(strategy)
            win.destroy()

        ttk.Button(main_scroll, text="DEPLOY LIVE", bootstyle="primary", command=deploy).pack(fill=tk.X, pady=10, padx=20)
