import re

with open('Invoicing/main.py', 'r') as f:
    content = f.read()

# Replace setup_clients_tab and related methods
new_methods = """
    def validate_name(self, action, value_if_allowed):
        if action != '1': return True
        if any(char.isdigit() for char in value_if_allowed): return False
        return True

    def validate_mobile(self, action, value_if_allowed):
        if action != '1': return True
        if not value_if_allowed.isdigit(): return False
        return True

    def validate_uppercase(self, event):
        widget = event.widget
        current_text = widget.get()
        if current_text != current_text.upper():
            cursor_pos = widget.index(tk.INSERT)
            widget.delete(0, tk.END)
            widget.insert(0, current_text.upper())
            widget.icursor(cursor_pos)

    def setup_clients_tab(self):
        # Top Frame for Entry
        frame_top = ttk.LabelFrame(self.tab_clients, text="Client Details")
        frame_top.pack(fill='x', padx=10, pady=10)

        vcmd_name = (self.register(self.validate_name), '%d', '%P')
        vcmd_mobile = (self.register(self.validate_mobile), '%d', '%P')

        ttk.Label(frame_top, text="Client Name:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.entry_client_name = ttk.Entry(frame_top, width=40, validate='key', validatecommand=vcmd_name)
        self.entry_client_name.grid(row=0, column=1, padx=5, pady=5)
        self.entry_client_name.bind('<KeyRelease>', self.validate_uppercase)

        ttk.Label(frame_top, text="PAN:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.entry_client_pan = ttk.Entry(frame_top, width=20)
        self.entry_client_pan.grid(row=0, column=3, padx=5, pady=5)
        self.entry_client_pan.bind('<KeyRelease>', self.validate_uppercase)

        ttk.Label(frame_top, text="GSTIN:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.entry_client_gst = ttk.Entry(frame_top, width=40)
        self.entry_client_gst.grid(row=1, column=1, padx=5, pady=5)
        self.entry_client_gst.bind('<KeyRelease>', self.validate_uppercase)

        ttk.Label(frame_top, text="Mobile:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.entry_client_mobile = ttk.Entry(frame_top, width=20, validate='key', validatecommand=vcmd_mobile)
        self.entry_client_mobile.grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(frame_top, text="Email:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.entry_client_email = ttk.Entry(frame_top, width=40)
        self.entry_client_email.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(frame_top, text="Address:").grid(row=2, column=2, padx=5, pady=5, sticky='w')
        self.entry_client_address = ttk.Entry(frame_top, width=40)
        self.entry_client_address.grid(row=2, column=3, padx=5, pady=5)
        self.entry_client_address.bind('<KeyRelease>', self.validate_uppercase)

        ttk.Label(frame_top, text="State:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        states = ["ANDAMAN AND NICOBAR ISLANDS", "ANDHRA PRADESH", "ARUNACHAL PRADESH", "ASSAM", "BIHAR", "CHANDIGARH", "CHHATTISGARH", "DADRA AND NAGAR HAVELI AND DAMAN AND DIU", "DELHI", "GOA", "GUJARAT", "HARYANA", "HIMACHAL PRADESH", "JAMMU AND KASHMIR", "JHARKHAND", "KARNATAKA", "KERALA", "LADAKH", "LAKSHADWEEP", "MADHYA PRADESH", "MAHARASHTRA", "MANIPUR", "MEGHALAYA", "MIZORAM", "NAGALAND", "ODISHA", "PUDUCHERRY", "PUNJAB", "RAJASTHAN", "SIKKIM", "TAMIL NADU", "TELANGANA", "TRIPURA", "UTTAR PRADESH", "UTTARAKHAND", "WEST BENGAL"]
        self.combo_client_state = ttk.Combobox(frame_top, values=states, width=38)
        self.combo_client_state.grid(row=3, column=1, padx=5, pady=5)

        btn_frame = ttk.Frame(frame_top)
        btn_frame.grid(row=4, column=0, columnspan=4, pady=10)
        ttk.Button(btn_frame, text="Add/Save Client", command=self.save_client).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Modify Selected", command=self.modify_client).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_client).pack(side='left', padx=5)

        # Bottom Frame for List
        frame_bottom = ttk.LabelFrame(self.tab_clients, text="Client List")
        frame_bottom.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ('PAN/ID', 'Name', 'Mobile', 'State', 'Account Balance')
        self.tree_clients = ttk.Treeview(frame_bottom, columns=columns, show='headings')
        for col in columns:
            self.tree_clients.heading(col, text=col)
            self.tree_clients.column(col, width=150)
        self.tree_clients.column('PAN/ID', width=100)
        self.tree_clients.pack(fill='both', expand=True)
        self.tree_clients.bind('<<TreeviewSelect>>', self.on_client_select)

        self.refresh_clients_list()

    def on_client_select(self, event):
        selected = self.tree_clients.selection()
        if not selected: return
        item = self.tree_clients.item(selected[0])
        pan = item['values'][0]

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT ClientName, PAN, GSTIN, Mobile, Email, Address, State FROM tblClients WHERE PAN=?", (pan,))
        row = c.fetchone()
        conn.close()

        if row:
            self.entry_client_name.delete(0, tk.END)
            self.entry_client_name.insert(0, row[0] or '')
            self.entry_client_pan.delete(0, tk.END)
            self.entry_client_pan.insert(0, row[1] or '')
            self.entry_client_gst.delete(0, tk.END)
            self.entry_client_gst.insert(0, row[2] or '')
            self.entry_client_mobile.delete(0, tk.END)
            self.entry_client_mobile.insert(0, row[3] or '')
            self.entry_client_email.delete(0, tk.END)
            self.entry_client_email.insert(0, row[4] or '')
            self.entry_client_address.delete(0, tk.END)
            self.entry_client_address.insert(0, row[5] or '')
            self.combo_client_state.set(row[6] or '')

    def save_client(self):
        name = self.entry_client_name.get().strip()
        pan = self.entry_client_pan.get().strip()

        if not name or not pan:
            messagebox.showerror("Error", "Client Name and PAN are required.")
            return

        conn = get_connection()
        c = conn.cursor()
        try:
            c.execute(\"""
                INSERT INTO tblClients (ClientName, PAN, GSTIN, Mobile, Email, Address, State)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            \""", (
                name,
                pan,
                self.entry_client_gst.get().strip(),
                self.entry_client_mobile.get().strip(),
                self.entry_client_email.get().strip(),
                self.entry_client_address.get().strip(),
                self.combo_client_state.get().strip()
            ))
            conn.commit()
            messagebox.showinfo("Success", "Client saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save client. Does PAN already exist?\\n{str(e)}")
        finally:
            conn.close()

        self.refresh_clients_list()
        self.clear_client_form()
        self.refresh_client_dropdown()

    def modify_client(self):
        pan = self.entry_client_pan.get().strip()
        if not pan:
            messagebox.showerror("Error", "Please select a client or enter PAN to modify.")
            return

        conn = get_connection()
        c = conn.cursor()
        c.execute(\"""
            UPDATE tblClients SET
                ClientName=?, GSTIN=?, Mobile=?, Email=?, Address=?, State=?
            WHERE PAN=?
        \""", (
            self.entry_client_name.get().strip(),
            self.entry_client_gst.get().strip(),
            self.entry_client_mobile.get().strip(),
            self.entry_client_email.get().strip(),
            self.entry_client_address.get().strip(),
            self.combo_client_state.get().strip(),
            pan
        ))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Client updated successfully.")
        self.refresh_clients_list()
        self.clear_client_form()
        self.refresh_client_dropdown()

    def delete_client(self):
        pan = self.entry_client_pan.get().strip()
        if not pan:
            messagebox.showerror("Error", "Please select a client to delete.")
            return

        if not messagebox.askyesno("Confirm", f"Are you sure you want to delete client with PAN: {pan}?"):
            return

        conn = get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM tblClients WHERE PAN=?", (pan,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Client deleted successfully.")
        self.refresh_clients_list()
        self.clear_client_form()
        self.refresh_client_dropdown()

    def clear_client_form(self):
        self.entry_client_name.delete(0, tk.END)
        self.entry_client_pan.delete(0, tk.END)
        self.entry_client_gst.delete(0, tk.END)
        self.entry_client_mobile.delete(0, tk.END)
        self.entry_client_email.delete(0, tk.END)
        self.entry_client_address.delete(0, tk.END)
        self.combo_client_state.set('')

    def refresh_clients_list(self):
        for item in self.tree_clients.get_children():
            self.tree_clients.delete(item)

        from business_logic import calculate_account_balance
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT ClientID, PAN, ClientName, Mobile, State FROM tblClients")
        for row in c.fetchall():
            client_id = row[0]
            balance = calculate_account_balance(conn, client_id)
            self.tree_clients.insert('', tk.END, values=(row[1], row[2], row[3], row[4], f"Rs. {balance:.2f}"))
        conn.close()"""

content = re.sub(
    r'    def setup_clients_tab\(self\):.*?def setup_invoice_tab\(self\):',
    new_methods + '\n    def setup_invoice_tab(self):',
    content,
    flags=re.DOTALL
)

with open('Invoicing/main.py', 'w') as f:
    f.write(content)
