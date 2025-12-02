import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb

class MainApp(tb.Window):
    def __init__(self, context):
        super().__init__(themename="darkly")
        self.title("AlgoTech Trading Engine")
        self.geometry("1200x800")
        self.context = context

        # Create Notebook (Tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Initialize Tabs
        from src.ui.home_tab import HomeTab
        from src.ui.login_tab import LoginTab
        from src.ui.strategy_tab import StrategyTab
        from src.ui.orders_tab import OrdersTab
        from src.ui.logs_tab import LogsTab
        from src.ui.risk_tab import RiskTab
        from src.ui.settings_tab import SettingsTab

        # Tab 1: Home
        self.tab_home = HomeTab(self.notebook, context)
        self.notebook.add(self.tab_home, text="Home")

        # Tab 2: Login
        self.tab_login = LoginTab(self.notebook, context)
        self.notebook.add(self.tab_login, text="Login")

        # Tab 3: Strategy
        self.tab_strategy = StrategyTab(self.notebook, context)
        self.notebook.add(self.tab_strategy, text="Strategy")

        # Tab 4: Orders
        self.tab_orders = OrdersTab(self.notebook, context)
        self.notebook.add(self.tab_orders, text="Orders")

        # Tab 5: Logs
        self.tab_logs = LogsTab(self.notebook, context)
        self.notebook.add(self.tab_logs, text="Logs")

        # Tab 6: Risk
        self.tab_risk = RiskTab(self.notebook, context)
        self.notebook.add(self.tab_risk, text="Risk")

        # Tab 7: Settings
        self.tab_settings = SettingsTab(self.notebook, context)
        self.notebook.add(self.tab_settings, text="Settings")

        # Start UI Loop
        self.tab_home.update_ui()
