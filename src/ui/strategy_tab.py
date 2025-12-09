import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
import json
import os
import glob
from src.ui.widgets import SearchableCombobox
from src.instrument_manager import instrument_manager
from src.logger import logger
from src.strategies.builder_strategy import BuilderStrategy

STRATEGY_DIR = "Data/strategies"

class StrategyCard(ttk.Frame):
    def __init__(self, parent, strategy, on_stop, on_square_off):
        super().__init__(parent, bootstyle="secondary", padding=10)
        self.strategy = strategy
        self.on_stop = on_stop
        self.on_square_off = on_square_off
        self.pack(fill=tk.X, pady=5)

        # Checkbox for bulk actions
        self.var_sel = tk.BooleanVar()
        self.chk_sel = ttk.Checkbutton(self, variable=self.var_sel, bootstyle="round-toggle")
        self.chk_sel.pack(side=tk.LEFT, padx=5)

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

class SavedStrategyRow(ttk.Frame):
    def __init__(self, parent, config, filepath, on_deploy, on_edit):
        super().__init__(parent, bootstyle="light", padding=5)
        self.config = config
        self.filepath = filepath
        self.on_deploy = on_deploy
        self.on_edit = on_edit
        self.pack(fill=tk.X, pady=2, padx=5)

        self.var_sel = tk.BooleanVar()
        ttk.Checkbutton(self, variable=self.var_sel).pack(side=tk.LEFT, padx=5)

        # Deploy Toggle
        ttk.Checkbutton(self, text="Deploy", bootstyle="success-round-toggle", command=self.deploy_action).pack(side=tk.LEFT, padx=10)

        # Edit Button
        ttk.Button(self, text="Edit", bootstyle="info-outline", command=self.edit_action, width=6).pack(side=tk.LEFT, padx=5)

        # Name (No .json)
        name = os.path.basename(filepath).replace(".json", "")
        desc = config.get("description", "")
        if desc: name += f" ({desc[:30]}...)"
        ttk.Label(self, text=name, font=("Arial", 10)).pack(side=tk.LEFT, padx=10)

    def deploy_action(self):
        self.on_deploy(self.config)

    def edit_action(self):
        self.on_edit(self.filepath)

class StrategyTab(ttk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.context = context
        self.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Tabs for "Deployed", "My Strategies", "Create New"
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Deployed Strategies
        self.tab_deployed = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_deployed, text="Deployed Strategies")
        self._init_deployed_tab()

        # Tab 2: My Strategies (Saved)
        self.tab_saved = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_saved, text="My Strategies")
        self._init_saved_tab()

        # Tab 3: Create New
        self.tab_create = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_create, text="Create New")
        self._init_create_tab()

        # Refresh Saved Strategies list on start
        self.refresh_saved_strategies()

    def _init_deployed_tab(self):
        f_top = ttk.Frame(self.tab_deployed)
        f_top.pack(fill=tk.X, pady=5)
        ttk.Button(f_top, text="Stop Selected", bootstyle="warning", command=self.stop_selected_deployed).pack(side=tk.LEFT, padx=5)
        ttk.Button(f_top, text="Square Off Selected", bootstyle="danger", command=self.sqoff_selected_deployed).pack(side=tk.LEFT, padx=5)

        canvas = tk.Canvas(self.tab_deployed, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_deployed, orient="vertical", command=canvas.yview)
        self.card_list = ttk.Frame(canvas)
        self.deployed_cards = []

        self.card_list.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.card_list, anchor="nw", width=1100)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _init_saved_tab(self):
        f_toolbar = ttk.Frame(self.tab_saved, padding=10)
        f_toolbar.pack(fill=tk.X)

        ttk.Button(f_toolbar, text="Refresh List", bootstyle="info-outline", command=self.refresh_saved_strategies).pack(side=tk.LEFT, padx=5)
        ttk.Button(f_toolbar, text="Delete Selected", bootstyle="danger", command=self.delete_selected_saved).pack(side=tk.RIGHT, padx=5)

        # Scrollable area for rows
        canvas = tk.Canvas(self.tab_saved, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_saved, orient="vertical", command=canvas.yview)
        self.saved_list_frame = ttk.Frame(canvas)
        self.saved_rows = []

        self.saved_list_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.saved_list_frame, anchor="nw", width=1100)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _init_create_tab(self):
        main_scroll = ttk.Frame(self.tab_create)
        main_scroll.pack(fill=tk.BOTH, expand=True)

        # --- Top: Symbol & Config ---
        f_top = ttk.Frame(main_scroll, padding=10)
        f_top.pack(fill=tk.X)

        ttk.Label(f_top, text="Strategy Name:").pack(side=tk.LEFT, padx=5)
        self.v_name = tk.StringVar(value="My Strategy")
        ttk.Entry(f_top, textvariable=self.v_name, width=20).pack(side=tk.LEFT, padx=5)

        ttk.Label(f_top, text="Underlying Symbol:").pack(side=tk.LEFT, padx=10)
        self.cb_sym = SearchableCombobox(f_top, all_values=instrument_manager.get_all_symbols(), width=30)
        self.cb_sym.pack(side=tk.LEFT, padx=5)
        if instrument_manager.get_all_symbols(): self.cb_sym.set_values(instrument_manager.get_all_symbols())

        # --- Entry Conditions Section ---
        f_cond = ttk.Labelframe(main_scroll, text="Entry Conditions (AND Logic)", padding=10)
        f_cond.pack(fill=tk.X, padx=10, pady=5)

        self.cond_frame = ttk.Frame(f_cond)
        self.cond_frame.pack(fill=tk.X)

        self.conditions_list = []

        ttk.Button(f_cond, text="+ Add Condition", command=self.add_condition_row, bootstyle="info-outline").pack(anchor="w", pady=5)
        self.add_condition_row() # Add one by default

        # --- Legs Section ---
        f_list = ttk.Labelframe(main_scroll, text="Leg Builder", padding=10)
        f_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        cols = ("type", "strike", "action", "qty", "tgt", "sl", "trail")
        self.tree_legs = ttk.Treeview(f_list, columns=cols, show="headings", height=5)

        for c in cols:
            self.tree_legs.heading(c, text=c.upper())
            self.tree_legs.column(c, width=80, anchor="center")
        self.tree_legs.pack(fill=tk.BOTH, expand=True)

        ttk.Button(f_list, text="Remove Selected", bootstyle="danger-outline",
                   command=lambda: [self.tree_legs.delete(x) for x in self.tree_legs.selection()]).pack(anchor="e", pady=5)

        # --- Add Leg Form ---
        f_add = ttk.Frame(main_scroll, padding=10)
        f_add.pack(fill=tk.X, padx=10)

        # Row 1
        r1 = ttk.Frame(f_add)
        r1.pack(fill=tk.X, pady=5)

        ttk.Label(r1, text="Type:").pack(side=tk.LEFT)
        self.v_type = tk.StringVar(value="CE")
        ttk.Combobox(r1, textvariable=self.v_type, values=["CE","PE","FUT"], width=5, state="readonly").pack(side=tk.LEFT, padx=5)

        ttk.Label(r1, text="Strike:").pack(side=tk.LEFT, padx=10)
        self.v_str = tk.StringVar(value="ATM")

        # Generate Strikes List
        strikes = []
        for i in range(400, 0, -50): strikes.append(f"ATM-{i}")
        strikes.append("ATM")
        for i in range(50, 450, 50): strikes.append(f"ATM+{i}")

        cb_str = ttk.Combobox(r1, textvariable=self.v_str, values=strikes, width=10, state="readonly")
        cb_str.pack(side=tk.LEFT, padx=5)

        ttk.Label(r1, text="Action:").pack(side=tk.LEFT, padx=10)
        self.v_act = tk.StringVar(value="BUY")
        ttk.Combobox(r1, textvariable=self.v_act, values=["BUY","SELL"], width=6, state="readonly").pack(side=tk.LEFT, padx=5)

        ttk.Label(r1, text="Qty:").pack(side=tk.LEFT, padx=10)
        self.v_qty = tk.StringVar(value="1")
        ttk.Entry(r1, textvariable=self.v_qty, width=5).pack(side=tk.LEFT, padx=5)

        # Row 2 (Risk)
        r2 = ttk.Frame(f_add)
        r2.pack(fill=tk.X, pady=5)

        def add_risk_field(label, val):
            ttk.Label(r2, text=label).pack(side=tk.LEFT, padx=5)
            v = tk.StringVar(value=val)
            ttk.Entry(r2, textvariable=v, width=5).pack(side=tk.LEFT)
            return v

        self.v_tgt = add_risk_field("Target(Pts):", "20")
        self.v_sl = add_risk_field("SL(Pts):", "10")
        self.v_trail = add_risk_field("Trail(Pts):", "0")

        ttk.Button(r2, text="ADD LEG", bootstyle="success", command=self.add_leg_to_tree).pack(side=tk.RIGHT, padx=20)

        # --- Action Buttons ---
        f_actions = ttk.Frame(main_scroll, padding=20)
        f_actions.pack(fill=tk.X)

        ttk.Button(f_actions, text="Save Strategy", bootstyle="info", command=self.save_strategy_to_disk).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10)
        ttk.Button(f_actions, text="DEPLOY LIVE", bootstyle="primary", command=self.deploy_live).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10)

    # --- Helper Methods for Creator ---

    def add_condition_row(self):
        row = ttk.Frame(self.cond_frame)
        row.pack(fill=tk.X, pady=2)

        i1 = ttk.Combobox(row, values=["LTP", "SMA", "EMA", "RSI", "VWAP", "SuperTrend", "Bollinger H", "Bollinger L"], width=12, state="readonly")
        i1.set("LTP")
        i1.pack(side=tk.LEFT, padx=2)

        comp = ttk.Combobox(row, values=[">", "<", ">=", "<=", "==", "Cross Above", "Cross Below"], width=10, state="readonly")
        comp.set(">")
        comp.pack(side=tk.LEFT, padx=2)

        i2 = ttk.Combobox(row, values=["Value", "LTP", "SMA", "EMA", "RSI", "VWAP"], width=12)
        i2.set("Value")
        i2.pack(side=tk.LEFT, padx=2)

        p1_val = tk.StringVar(value="14")
        ttk.Entry(row, textvariable=p1_val, width=5).pack(side=tk.LEFT, padx=2)

        entry_obj = {"row": row, "i1": i1, "comp": comp, "i2": i2, "p1": p1_val}

        btn_del = ttk.Button(row, text="X", bootstyle="danger-link", command=lambda: self.remove_condition_row(row, entry_obj))
        btn_del.pack(side=tk.LEFT, padx=5)

        self.conditions_list.append(entry_obj)

    def remove_condition_row(self, row, obj):
        row.destroy()
        if obj in self.conditions_list: self.conditions_list.remove(obj)

    def add_leg_to_tree(self):
        self.tree_legs.insert("", "end", values=(
            self.v_type.get(), self.v_str.get(), self.v_act.get(),
            self.v_qty.get(), self.v_tgt.get(), self.v_sl.get(), self.v_trail.get()
        ))

    def _get_config_from_ui(self):
        legs = []
        for item in self.tree_legs.get_children():
            vals = self.tree_legs.item(item)['values']
            leg = (vals[0], vals[1], vals[2], vals[3], vals[4], "Pts", vals[5], "Pts", vals[6], "Pts", "0", "Pts")
            legs.append(leg)

        parsed_conds = []
        for c in self.conditions_list:
            parsed_conds.append({
                "ind1": c["i1"].get(),
                "op": c["comp"].get(),
                "ind2": c["i2"].get(),
                "p1": {"period": c["p1"].get()},
                "p2": {"period": "14"}
            })

        return {
            "name": self.v_name.get(),
            "target_symbol": self.cb_sym.get(),
            "entry_conditions": parsed_conds,
            "legs": legs
        }

    # --- Strategy Management ---

    def save_strategy_to_disk(self):
        config = self._get_config_from_ui()
        if not config["name"]:
            messagebox.showerror("Error", "Strategy Name is required")
            return

        filename = f"{config['name']}.json".replace(" ", "_")
        path = os.path.join(STRATEGY_DIR, filename)

        try:
            with open(path, "w") as f:
                json.dump(config, f, indent=4)
            messagebox.showinfo("Success", f"Strategy saved to {path}")
            self.refresh_saved_strategies()
        except Exception as e:
            logger.error(f"Failed to save strategy: {e}")
            messagebox.showerror("Error", f"Failed to save: {e}")

    def refresh_saved_strategies(self):
        # Clear existing
        for w in self.saved_list_frame.winfo_children(): w.destroy()
        self.saved_rows = []

        files = glob.glob(os.path.join(STRATEGY_DIR, "*.json"))
        for f in files:
            try:
                with open(f, "r") as file:
                    config = json.load(file)

                row = SavedStrategyRow(self.saved_list_frame, config, f, self.deploy_from_config, self.load_for_edit)
                self.saved_rows.append(row)
            except Exception as e:
                logger.error(f"Error loading {f}: {e}")

    def delete_selected_saved(self):
        to_delete = [r for r in self.saved_rows if r.var_sel.get()]
        if not to_delete: return

        if messagebox.askyesno("Confirm", f"Delete {len(to_delete)} strategies?"):
            for r in to_delete:
                try: os.remove(r.filepath)
                except: pass
            self.refresh_saved_strategies()

    def deploy_from_config(self, config):
        broker = self.context.get('broker')
        strategy = BuilderStrategy(broker, config)
        strategy.set_symbol(config["target_symbol"])
        strategy.start()

        self.add_strategy_card(strategy)
        self.notebook.select(self.tab_deployed)

    def load_for_edit(self, path):
        try:
            with open(path, "r") as f:
                config = json.load(f)

            self.v_name.set(config.get("name", ""))
            self.cb_sym.set(config.get("target_symbol", ""))

            # Clear UI
            for c in self.conditions_list: c['row'].destroy()
            self.conditions_list = []
            self.tree_legs.delete(*self.tree_legs.get_children())

            # Restore Conditions
            for c in config.get("entry_conditions", []):
                self.add_condition_row()
                last_cond = self.conditions_list[-1]
                last_cond['i1'].set(c.get("ind1", "LTP"))
                last_cond['comp'].set(c.get("op", ">"))
                last_cond['i2'].set(c.get("ind2", "Value"))
                last_cond['p1'].set(c.get("p1", {}).get("period", "14"))

            # Restore Legs
            for leg in config.get("legs", []):
                if isinstance(leg, list) or isinstance(leg, tuple):
                    self.tree_legs.insert("", "end", values=(leg[0], leg[1], leg[2], leg[3], leg[4], leg[6], leg[8]))

            self.notebook.select(self.tab_create)

        except Exception as e:
            logger.error(f"Failed to load strategy: {e}")
            messagebox.showerror("Error", f"Failed to load: {e}")

    def deploy_live(self):
        config = self._get_config_from_ui()
        self.deploy_from_config(config)

    def add_strategy_card(self, strategy):
        if 'strategies' not in self.context: self.context['strategies'] = []
        self.context['strategies'].append(strategy)

        if self.context.get('data_engine'):
            self.context['data_engine'].register_strategy(strategy)
            self.context['data_engine'].subscribe([strategy.target_symbol])

        card = StrategyCard(self.card_list, strategy, lambda: None, self.square_off_strategy)
        self.deployed_cards.append(card)

    def square_off_strategy(self, strategy):
        pass

    def stop_selected_deployed(self):
        for card in self.deployed_cards:
            if card.var_sel.get():
                card.strategy.stop()
                card.lbl_status.config(text="STOPPED", bootstyle="secondary")

    def sqoff_selected_deployed(self):
        for card in self.deployed_cards:
            if card.var_sel.get():
                card.square_off()
