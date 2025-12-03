import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb

class SettingsTab(ttk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.context = context
        self.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(self, text="Application Settings", font=("Helvetica", 14, "bold")).pack(pady=10)

        # Redirect URI
        frame_net = ttk.LabelFrame(self, text="Network & API", padding=15)
        frame_net.pack(fill=tk.X, pady=10)

        ttk.Label(frame_net, text="Redirect URI:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.entry_uri = ttk.Entry(frame_net, width=40)
        self.entry_uri.insert(0, self.context['config'].get('redirect_uri', 'http://127.0.0.1:5000/callback'))
        self.entry_uri.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        ttk.Button(self, text="Save Settings", bootstyle="success", command=self.save_settings).pack(pady=20)

    def save_settings(self):
        uri = self.entry_uri.get()
        self.context['config']['redirect_uri'] = uri
        from src.config import save_config
        save_config(self.context['config'])
        tk.messagebox.showinfo("Success", "Settings saved. Restart application to apply changes.")
