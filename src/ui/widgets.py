import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb

class SearchableCombobox(ttk.Combobox):
    def __init__(self, master, all_values, **kwargs):
        super().__init__(master, **kwargs)
        self._all_values = all_values
        self._hits = all_values[:50] # Show first 50 by default
        self['values'] = self._hits

        self.bind('<KeyRelease>', self._on_key_release)
        self.bind('<<ComboboxSelected>>', self._on_select)

    def _on_key_release(self, event):
        # If special key (up/down/enter), ignore filtering
        if event.keysym in ('Up', 'Down', 'Return', 'Enter', 'Tab'):
            return

        value = self.get()
        if value == '':
            self._hits = self._all_values[:50]
        else:
            # Simple case-insensitive filter
            # Optimization: If list is huge (50k), simple loop is slow.
            # But for now, we try simple list comprehension limited to first 50 matches for speed
            search_term = value.lower()
            self._hits = []
            count = 0
            for item in self._all_values:
                if search_term in item.lower():
                    self._hits.append(item)
                    count += 1
                    if count >= 50: # Limit dropdown size
                        break

        self['values'] = self._hits

        # Keep the dropdown open or re-open it
        if self._hits:
            self.event_generate('<Down>')

    def _on_select(self, event):
        # Optional: trigger callback
        pass

    def set_values(self, values):
        self._all_values = values
        self._hits = values[:50]
        self['values'] = self._hits
