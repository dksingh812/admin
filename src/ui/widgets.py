import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb

class SearchableCombobox(ttk.Combobox):
    def __init__(self, master, all_values, **kwargs):
        super().__init__(master, **kwargs)
        self._all_values = all_values or []
        self._hits = self._all_values[:50]
        self['values'] = self._hits

        self.bind('<KeyRelease>', self._on_key_release)
        # self.bind('<FocusIn>', self._on_focus) # Optional: Open on click

    def _on_key_release(self, event):
        if event.keysym in ('Up', 'Down', 'Return', 'Enter', 'Tab', 'Left', 'Right'):
            return

        value = self.get()
        if value == '':
            self._hits = self._all_values[:50]
        else:
            search_term = value.lower()
            self._hits = []
            count = 0
            # Optimization:
            # 1. Check starts_with first (higher priority)
            # 2. Check contains

            # Fast filter for huge lists
            for item in self._all_values:
                if search_term in item.lower():
                    self._hits.append(item)
                    count += 1
                    if count >= 100: # Limit matches
                        break

        self['values'] = self._hits
        if self._hits:
            try:
                self.tk.call('ttk::combobox::Post', self._w)
            except: pass

    def set_values(self, values):
        self._all_values = values
        self._hits = values[:50] if values else []
        self['values'] = self._hits
