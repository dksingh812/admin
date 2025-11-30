import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb

class MainApp(tb.Window):
    def __init__(self, context):
        super().__init__(themename="darkly")
        self.title("AlgoTech Trading Engine")
        self.geometry("1000x700")
        self.context = context

        # Create Notebook (Tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Initialize Tabs
        from src.ui.home_tab import HomeTab
        from src.ui.login_tab import LoginTab
        from src.ui.strategy_tab import StrategyTab

        # Tab 1: Home
        self.tab_home = HomeTab(self.notebook, context)
        self.notebook.add(self.tab_home, text="Home")

        # Tab 2: Login
        self.tab_login = LoginTab(self.notebook, context)
        self.notebook.add(self.tab_login, text="Login")

        # Tab 3: Strategy
        self.tab_strategy = StrategyTab(self.notebook, context)
        self.notebook.add(self.tab_strategy, text="Strategy")

        # Tab 4: Orders (Placeholder)
        self.tab_orders = ttk.Frame(self.notebook)
        ttk.Label(self.tab_orders, text="Orders Table Here").pack(pady=20)
        self.notebook.add(self.tab_orders, text="Orders")

        # Start UI Loop
        self.tab_home.update_ui()
