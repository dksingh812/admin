import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from src.config import save_config

class SettingsTab(ttk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.context = context
        self.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(self, text="Application Settings", font=("Helvetica", 14, "bold")).pack(pady=10)

        # --- Appearance ---
        frame_app = ttk.LabelFrame(self, text="Appearance", padding=15)
        frame_app.pack(fill=tk.X, pady=10)

        ttk.Label(frame_app, text="Theme:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.themes = tb.Style().theme_names()
        self.v_theme = tk.StringVar(value=self.context['config'].get('theme', 'flatly'))
        self.cb_theme = ttk.Combobox(frame_app, textvariable=self.v_theme, values=self.themes, state="readonly", width=20)
        self.cb_theme.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.cb_theme.bind("<<ComboboxSelected>>", self.change_theme)

        # --- Network & API ---
        frame_net = ttk.LabelFrame(self, text="Network & API", padding=15)
        frame_net.pack(fill=tk.X, pady=10)

        ttk.Label(frame_net, text="Redirect URI:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.entry_uri = ttk.Entry(frame_net, width=40)
        self.entry_uri.insert(0, self.context['config'].get('redirect_uri', 'http://127.0.0.1:5000/callback'))
        self.entry_uri.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # --- Save ---
        ttk.Button(self, text="Save Settings", bootstyle="success", command=self.save_settings).pack(pady=20)

    def change_theme(self, event):
        theme = self.v_theme.get()
        style = tb.Style()
        style.theme_use(theme)
        self.context['config']['theme'] = theme

    def save_settings(self):
        uri = self.entry_uri.get()
        theme = self.v_theme.get()

        self.context['config']['redirect_uri'] = uri
        self.context['config']['theme'] = theme

        save_config(self.context['config'])
        messagebox.showinfo("Success", "Settings saved successfully.")
