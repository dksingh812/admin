import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb

class LogsTab(ttk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.context = context
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(self, text="Application Logs", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=5)

        self.txt_logs = tk.Text(self, font=("Consolas", 9), state="disabled")
        self.txt_logs.pack(fill=tk.BOTH, expand=True)

        # Initial Load
        self.load_logs()

        ttk.Button(self, text="Refresh Logs", command=self.load_logs).pack(pady=5)

    def load_logs(self):
        self.txt_logs.config(state="normal")
        self.txt_logs.delete("1.0", tk.END)

        # Read from latest log file
        # We need to find the latest log file in Logs/
        from src.config import LOGS_DIR
        try:
            log_files = sorted(LOGS_DIR.glob("*.log"), key=lambda f: f.stat().st_mtime, reverse=True)
            if log_files:
                latest = log_files[0]
                with open(latest, "r") as f:
                    content = f.read()
                    self.txt_logs.insert(tk.END, content)
            else:
                self.txt_logs.insert(tk.END, "No logs found.")
        except Exception as e:
            self.txt_logs.insert(tk.END, f"Error reading logs: {e}")

        self.txt_logs.see(tk.END)
        self.txt_logs.config(state="disabled")
