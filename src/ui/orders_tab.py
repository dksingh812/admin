import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb

class OrdersTab(ttk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.context = context
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Columns
        columns = ("time", "symbol", "side", "qty", "price", "status", "id")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", bootstyle="info")

        self.tree.heading("time", text="Time")
        self.tree.heading("symbol", text="Symbol")
        self.tree.heading("side", text="Side")
        self.tree.heading("qty", text="Qty")
        self.tree.heading("price", text="Price")
        self.tree.heading("status", text="Status")
        self.tree.heading("id", text="Order ID")

        self.tree.column("time", width=100)
        self.tree.column("symbol", width=100)
        self.tree.column("side", width=50)
        self.tree.column("qty", width=50)
        self.tree.column("price", width=80)
        self.tree.column("status", width=80)
        self.tree.column("id", width=100)

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Refresh Button
        ttk.Button(self, text="Refresh Orders", command=self.refresh_orders, bootstyle="secondary").pack(pady=10)

    def refresh_orders(self):
        # Clear existing
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Fetch from broker
        # Ideally broker should have get_orders()
        # For now we just show placeholder or mock
        pass
