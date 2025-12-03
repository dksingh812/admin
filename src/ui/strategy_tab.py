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

        # Name (Symbol + Algo)
        lbl_name = ttk.Label(self, text=f"{strategy.target_symbol}\n{strategy.name}", font=("Helvetica", 10, "bold"))
        lbl_name.pack(side=tk.LEFT, padx=10)

        # Status
        self.lbl_status = ttk.Label(self, text="RUNNING", bootstyle="success")
        self.lbl_status.pack(side=tk.LEFT, padx=20)

        # PnL (Placeholder for now, strategy needs to track its own pnl or we fetch from orders)
        self.lbl_pnl = ttk.Label(self, text="PnL: ₹0.00", font=("Helvetica", 10))
        self.lbl_pnl.pack(side=tk.LEFT, padx=20)

        # Buttons
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

        # Top Bar
        top = ttk.Frame(self)
        top.pack(fill=tk.X, pady=10)
        ttk.Label(top, text="Deployed Strategies", font=("Helvetica", 16, "bold")).pack(side=tk.LEFT)
        ttk.Button(top, text="+ Create New Strategy", bootstyle="primary", command=self.open_creator).pack(side=tk.RIGHT)

        # Dashboard List
        self.dash_frame = ttk.Frame(self)
        self.dash_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollable container for cards
        canvas = tk.Canvas(self.dash_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.dash_frame, orient="vertical", command=canvas.yview)
        self.card_list = ttk.Frame(canvas)

        self.card_list.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.card_list, anchor="nw", width=1100)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def add_strategy_card(self, strategy):
        # Add to backend list
        if 'strategies' not in self.context: self.context['strategies'] = []
        self.context['strategies'].append(strategy)

        # Register with Data Engine
        if self.context.get('data_engine'):
            self.context['data_engine'].register_strategy(strategy)
            self.context['data_engine'].subscribe([strategy.target_symbol])

        # Add UI Card
        card = StrategyCard(self.card_list, strategy, lambda: None, self.square_off_strategy)

    def square_off_strategy(self, strategy):
        # Implement logic to close all open legs for this strategy
        pass

    def open_creator(self):
        # Open Toplevel Window
        win = tb.Toplevel(self)
        win.title("Create Strategy")
        win.geometry("900x600")

        frame = ttk.Frame(win, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Symbol
        ttk.Label(frame, text="Symbol:").pack(anchor="w")
        cb_sym = SearchableCombobox(frame, all_values=instrument_manager.get_all_symbols())
        cb_sym.pack(fill=tk.X, pady=5)
        if instrument_manager.get_all_symbols(): cb_sym.set_values(instrument_manager.get_all_symbols())

        # Legs
        cols = ("type", "strike", "action", "qty", "tgt", "sl", "trail", "buf")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=8)
        for c in cols: tree.heading(c, text=c.upper()); tree.column(c, width=60)
        tree.pack(fill=tk.BOTH, expand=True, pady=10)

        # Add Leg Inputs
        i_row = ttk.Frame(frame)
        i_row.pack(fill=tk.X)

        v_type = tk.StringVar(value="CE")
        ttk.Combobox(i_row, textvariable=v_type, values=["CE","PE","FUT"], width=5).pack(side=tk.LEFT)
        v_str = tk.StringVar(value="ATM")

        # Enhanced Strike List
        strikes = ["ATM"]
        for i in [50, 100, 150, 200]:
            strikes.append(f"ATM+{i}")
            strikes.append(f"ATM-{i}")

        ttk.Combobox(i_row, textvariable=v_str, values=strikes, width=10).pack(side=tk.LEFT)
        v_act = tk.StringVar(value="BUY")
        ttk.Combobox(i_row, textvariable=v_act, values=["BUY","SELL"], width=5).pack(side=tk.LEFT)
        v_qty = tk.StringVar(value="1")
        ttk.Entry(i_row, textvariable=v_qty, width=5).pack(side=tk.LEFT)

        def add_leg():
            tree.insert("", "end", values=(v_type.get(), v_str.get(), v_act.get(), v_qty.get(), 0, 0, 0, 0))

        ttk.Button(i_row, text="+", command=add_leg).pack(side=tk.LEFT, padx=5)

        def deploy():
            sym = cb_sym.get()
            legs = []
            for item in tree.get_children(): legs.append(tree.item(item)['values'])

            # Create Strategy Instance
            broker = self.context.get('broker')
            config = {"sma_period": 14, "rsi_period": 14} # Default
            strategy = SMARSIStrategy(broker, config)
            strategy.set_symbol(sym)
            strategy.legs = legs
            strategy.start()

            self.add_strategy_card(strategy)
            win.destroy()

        ttk.Button(frame, text="DEPLOY STRATEGY", bootstyle="success", command=deploy).pack(fill=tk.X, pady=20)
