import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from src.ui.widgets import SearchableCombobox
from src.instrument_manager import instrument_manager
from src.logger import logger
from src.strategies.sma_rsi import SMARSIStrategy # Assuming we reuse this class type

class StrategyCard(ttk.Frame):
    def __init__(self, parent, strategy, on_stop, on_square_off):
        super().__init__(parent, bootstyle="secondary", padding=10)
        self.strategy = strategy
        self.on_stop = on_stop
        self.on_square_off = on_square_off
        self.pack(fill=tk.X, pady=5)

        # Row Layout
        # Name | Status | PnL | Buttons

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
        win.geometry("1100x700") # Wider

        frame = ttk.Frame(win, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # --- Top: Symbol & Config ---
        f_top = ttk.Frame(frame)
        f_top.pack(fill=tk.X, pady=10)

        ttk.Label(f_top, text="Underlying Symbol:").pack(side=tk.LEFT, padx=5)
        cb_sym = SearchableCombobox(f_top, all_values=instrument_manager.get_all_symbols(), width=30)
        cb_sym.pack(side=tk.LEFT, padx=5)
        if instrument_manager.get_all_symbols(): cb_sym.set_values(instrument_manager.get_all_symbols())

        # --- Middle: Leg List ---
        f_list = ttk.Labelframe(frame, text="Configured Legs", padding=10)
        f_list.pack(fill=tk.BOTH, expand=True, pady=10)

        cols = ("type", "strike", "action", "qty", "tgt", "tgt_u", "sl", "sl_u", "trail", "trail_u", "buf", "buf_u")
        tree = ttk.Treeview(f_list, columns=cols, show="headings", height=6)

        # Headers
        h_map = {
            "type": "Type", "strike": "Strike", "action": "Side", "qty": "Qty",
            "tgt": "Target", "tgt_u": "Unit",
            "sl": "SL", "sl_u": "Unit",
            "trail": "Trail", "trail_u": "Unit",
            "buf": "Buffer", "buf_u": "Unit"
        }
        for c in cols:
            tree.heading(c, text=h_map[c])
            w = 40 if "_u" in c else 60
            tree.column(c, width=w, anchor="center")

        tree.pack(fill=tk.BOTH, expand=True)

        ttk.Button(f_list, text="Remove Selected", bootstyle="danger-outline",
                   command=lambda: [tree.delete(x) for x in tree.selection()]).pack(anchor="e", pady=5)

        # --- Bottom: Add Leg Form (Spacious) ---
        f_add = ttk.Labelframe(frame, text="Add New Leg", padding=15, bootstyle="info")
        f_add.pack(fill=tk.X, pady=10)

        # Row 1: Instrument Basics
        r1 = ttk.Frame(f_add)
        r1.pack(fill=tk.X, pady=5)

        ttk.Label(r1, text="Instrument Type:", width=15).pack(side=tk.LEFT)
        v_type = tk.StringVar(value="CE")
        ttk.Combobox(r1, textvariable=v_type, values=["CE","PE","FUT"], width=10, state="readonly").pack(side=tk.LEFT, padx=5)

        ttk.Label(r1, text="Strike:", width=10).pack(side=tk.LEFT, padx=(20, 0))
        v_str = tk.StringVar(value="ATM")
        strikes = ["ATM"] + [f"ATM{s}{i}" for s in ["+","-"] for i in [50,100,150,200,250,300,400,500]]
        ttk.Combobox(r1, textvariable=v_str, values=strikes, width=15).pack(side=tk.LEFT, padx=5)

        ttk.Label(r1, text="Action:", width=10).pack(side=tk.LEFT, padx=(20, 0))
        v_act = tk.StringVar(value="BUY")
        ttk.Combobox(r1, textvariable=v_act, values=["BUY","SELL"], width=10, state="readonly").pack(side=tk.LEFT, padx=5)

        ttk.Label(r1, text="Qty:", width=5).pack(side=tk.LEFT, padx=(20, 0))
        v_qty = tk.StringVar(value="1")
        ttk.Entry(r1, textvariable=v_qty, width=8).pack(side=tk.LEFT, padx=5)

        # Row 2: Risk Params (Wider inputs with units)
        r2 = ttk.Frame(f_add)
        r2.pack(fill=tk.X, pady=10)

        def create_field(parent, label, default_val):
            f = ttk.Frame(parent)
            f.pack(side=tk.LEFT, padx=10)
            ttk.Label(f, text=label, font=("Arial", 8)).pack(anchor="w")

            sub = ttk.Frame(f)
            sub.pack()
            val = tk.StringVar(value=default_val)
            ttk.Entry(sub, textvariable=val, width=8).pack(side=tk.LEFT)

            unit = tk.StringVar(value="%")
            ttk.Combobox(sub, textvariable=unit, values=["%", "Pts"], width=4, state="readonly").pack(side=tk.LEFT)
            return val, unit

        v_tgt, u_tgt = create_field(r2, "Target", "10")
        v_sl, u_sl = create_field(r2, "Stop Loss", "5")
        v_trail, u_trail = create_field(r2, "Trailing SL", "0")
        v_buf, u_buf = create_field(r2, "Buffer", "0")

        # Add Button
        def add_leg():
            tree.insert("", "end", values=(
                v_type.get(), v_str.get(), v_act.get(), v_qty.get(),
                v_tgt.get(), u_tgt.get(),
                v_sl.get(), u_sl.get(),
                v_trail.get(), u_trail.get(),
                v_buf.get(), u_buf.get()
            ))

        ttk.Button(r2, text="+ ADD LEG TO LIST", bootstyle="success", command=add_leg).pack(side=tk.RIGHT, padx=20)

        # --- Deploy ---
        def deploy():
            sym = cb_sym.get()
            legs = []
            for item in tree.get_children(): legs.append(tree.item(item)['values'])

            broker = self.context.get('broker')
            config = {"sma_period": 14, "rsi_period": 14}
            strategy = SMARSIStrategy(broker, config)
            strategy.set_symbol(sym)
            strategy.legs = legs
            strategy.start()

            self.add_strategy_card(strategy)
            win.destroy()

        ttk.Button(frame, text="DEPLOY STRATEGY", bootstyle="primary", command=deploy).pack(fill=tk.X, pady=10)
