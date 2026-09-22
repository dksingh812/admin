import re

with open('Invoicing/main.py', 'r') as f:
    content = f.read()

new_methods = """
    def setup_invoice_tab(self):
        # Invoice Type Selection
        frame_type = ttk.Frame(self.tab_invoice)
        frame_type.pack(fill='x', padx=10, pady=5)

        ttk.Label(frame_type, text="Invoice Type:").pack(side='left', padx=5)
        self.inv_type = tk.StringVar(value="GST")
        ttk.Radiobutton(frame_type, text="GST Invoice (Parigantavya)", variable=self.inv_type, value="GST", command=self.on_type_change).pack(side='left', padx=10)
        ttk.Radiobutton(frame_type, text="Normal Invoice (Berrify)", variable=self.inv_type, value="Normal", command=self.on_type_change).pack(side='left', padx=10)

        # Client Selection
        frame_client = ttk.LabelFrame(self.tab_invoice, text="Select Client")
        frame_client.pack(fill='x', padx=10, pady=5)

        self.combo_client = ttk.Combobox(frame_client, width=60) # Not readonly to allow searching
        self.combo_client.pack(side='left', padx=5, pady=5)
        self.combo_client.bind('<KeyRelease>', self.search_clients)

        self.refresh_client_dropdown()

        # Services Line Items
        frame_services = ttk.LabelFrame(self.tab_invoice, text="Services (Max 5)")
        frame_services.pack(fill='both', expand=True, padx=10, pady=5)

        self.service_rows = []

        # Fetch Services for Dropdown
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT SACCode, SACName FROM tblSACHSN")
        self.sac_list = [f"{row[1]} - {row[0]}" for row in c.fetchall()]
        conn.close()

        headers = ["Service Description (Select or Type)", "Period", "SAC Code", "Fee (Rs.)", "Cum-GST"]
        for col, h in enumerate(headers):
            ttk.Label(frame_services, text=h, font=('', 9, 'bold')).grid(row=0, column=col, padx=5, pady=5)

        for i in range(5):
            desc = ttk.Combobox(frame_services, values=self.sac_list, width=40)
            desc.grid(row=i+1, column=0, padx=5, pady=2)
            desc.bind('<<ComboboxSelected>>', lambda e, row_idx=i: self.on_service_selected(row_idx))

            period = ttk.Entry(frame_services, width=20)
            period.grid(row=i+1, column=1, padx=5, pady=2)

            sac = ttk.Entry(frame_services, width=10)
            sac.grid(row=i+1, column=2, padx=5, pady=2)

            amt = ttk.Entry(frame_services, width=15)
            amt.grid(row=i+1, column=3, padx=5, pady=2)

            cum_gst_var = tk.BooleanVar(value=True)
            cum_gst = ttk.Checkbutton(frame_services, variable=cum_gst_var)
            cum_gst.grid(row=i+1, column=4, padx=5, pady=2)

            self.service_rows.append({'desc': desc, 'period': period, 'sac': sac, 'amt': amt, 'cum_gst': cum_gst_var})

        # Action buttons
        frame_actions = ttk.Frame(self.tab_invoice)
        frame_actions.pack(fill='x', padx=10, pady=10)

        ttk.Button(frame_actions, text="Generate Invoice", command=self.generate_invoice).pack(side='right', padx=5)

    def search_clients(self, event):
        value = event.widget.get()
        if value == '':
            self.combo_client['values'] = list(self.client_map.keys())
        else:
            data = []
            for item in self.client_map.keys():
                if value.lower() in item.lower():
                    data.append(item)
            self.combo_client['values'] = data

    def on_service_selected(self, row_idx):
        row = self.service_rows[row_idx]
        selection = row['desc'].get()
        if " - " in selection:
            name, code = selection.rsplit(" - ", 1)
            row['desc'].set(name)
            row['sac'].delete(0, tk.END)
            row['sac'].insert(0, code)

    def refresh_client_dropdown(self):
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT ClientID, ClientName, PAN FROM tblClients")
        self.client_map = {f"{row[1]} - {row[2]}": row[0] for row in c.fetchall()}
        conn.close()

        self.combo_client['values'] = list(self.client_map.keys())

    def on_type_change(self):
        is_gst = self.inv_type.get() == "GST"
        for row in self.service_rows:
            if is_gst:
                row['sac'].config(state='normal')
            else:
                row['sac'].delete(0, tk.END)
                row['sac'].config(state='disabled')

    def generate_invoice(self):
        client_sel = self.combo_client.get()
        if client_sel not in self.client_map:
            messagebox.showerror("Error", "Please select a valid client from the dropdown list.")
            return

        client_id = self.client_map[client_sel]
        inv_type = self.inv_type.get()

        items_data = []
        total_amount = 0
        total_taxable = 0

        conn = get_connection()
        c = conn.cursor()

        # Get Client Data
        c.execute("SELECT ClientName, PAN, GSTIN, Mobile, Email, Address, State FROM tblClients WHERE ClientID=?", (client_id,))
        client_row = c.fetchone()
        client_data = {
            'ClientName': client_row[0],
            'PAN': client_row[1],
            'GSTIN': client_row[2],
            'Mobile': client_row[3],
            'Email': client_row[4],
            'Address': client_row[5],
            'State': client_row[6]
        }

        for row in self.service_rows:
            desc = row['desc'].get().strip()
            period = row['period'].get().strip()
            amt_str = row['amt'].get().strip()
            sac = row['sac'].get().strip()
            cum_gst = row['cum_gst'].get()

            if desc and amt_str:
                try:
                    fee = float(amt_str)
                except:
                    messagebox.showerror("Error", "Invalid fee amount entered.")
                    return

                item = {
                    'ServiceDescription': desc,
                    'Period': period,
                    'SAC': sac
                }

                if inv_type == 'GST':
                    client_state = client_data.get('State', '').upper()
                    is_intra_state = client_state == 'UTTAR PRADESH'

                    if cum_gst:
                        # Fee includes GST
                        taxable_value = fee / 1.18
                    else:
                        taxable_value = fee

                    total_taxable += taxable_value
                    item['Amount'] = taxable_value

                    if is_intra_state:
                        cgst = taxable_value * 0.09
                        sgst = taxable_value * 0.09
                        igst = 0
                    else:
                        cgst = 0
                        sgst = 0
                        igst = taxable_value * 0.18

                    item['CGST'] = cgst
                    item['SGST'] = sgst
                    item['IGST'] = igst

                    item_total = taxable_value + cgst + sgst + igst
                    item['TotalAmount'] = item_total
                    total_amount += item_total
                else:
                    item['Amount'] = fee
                    item['TotalAmount'] = fee
                    total_amount += fee

                items_data.append(item)

        if not items_data:
            messagebox.showerror("Error", "Please enter at least one service.")
            return

        # Generate DB Record
        now = datetime.now()
        inv_no = generate_invoice_number(conn, inv_type, now)
        fy = get_financial_year(now)
        date_str = now.strftime('%d-%m-%Y')

        invoice_data = {
            'InvoiceNo': inv_no,
            'InvoiceDate': date_str,
            'DueDate': date_str,
            'TotalAmount': total_amount,
            'PaymentMode': 'UPI / Bank Transfer / Cheque / Cash'
        }

        try:
            if inv_type == 'GST':
                cgst_total = sum(i.get('CGST', 0) for i in items_data)"""

content = re.sub(
    r'    def setup_invoice_tab\(self\):.*?if inv_type == \'GST\':\n                cgst_total = sum\(i\[\'CGST\'\] for i in items_data\)',
    new_methods,
    content,
    flags=re.DOTALL
)

with open('Invoicing/main.py', 'w') as f:
    f.write(content)
