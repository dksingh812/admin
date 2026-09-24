import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from datetime import datetime

from database import get_connection, init_db
from business_logic import get_financial_year, generate_invoice_number, send_whatsapp_message
from pdf_generator import generate_gst_invoice, generate_normal_invoice

class InvoicingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Parigantavya Consultants - Invoicing System")
        self.geometry("1000x700")

        # Initialize Database
        init_db()

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)


        self.tab_invoice = ttk.Frame(self.notebook)
        self.tab_clients = ttk.Frame(self.notebook)
        self.tab_receipts = ttk.Frame(self.notebook)
        self.tab_cash_bank = ttk.Frame(self.notebook)
        self.tab_notes = ttk.Frame(self.notebook)
        self.tab_recycle = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_invoice, text="Create Invoice")
        self.notebook.add(self.tab_clients, text="Manage Clients")
        self.notebook.add(self.tab_receipts, text="Invoice Tracking & Receipts")
        self.notebook.add(self.tab_cash_bank, text="Cash Book & Bank Book")
        self.notebook.add(self.tab_notes, text="Credit/Debit Notes (GST)")
        self.notebook.add(self.tab_recycle, text="Recycle Bin")

        self.setup_clients_tab()
        self.setup_invoice_tab()
        self.setup_receipts_tab()
        self.setup_cash_bank_tab()
        self.setup_notes_tab()
        self.setup_recycle_tab()



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

        ttk.Label(frame_top, text="Opening Balance:").grid(row=3, column=2, padx=5, pady=5, sticky='w')
        self.entry_client_opening_bal = ttk.Entry(frame_top, width=20)
        self.entry_client_opening_bal.grid(row=3, column=3, padx=5, pady=5)

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
        self.tree_clients.column('PAN/ID', width=100, anchor='center')
        self.tree_clients.column('Account Balance', width=150, anchor='e')
        self.tree_clients.pack(fill='both', expand=True)
        self.tree_clients.bind('<<TreeviewSelect>>', self.on_client_select)

        self.refresh_clients_list()

    def clear_client_form(self):
        self.entry_client_name.delete(0, tk.END)
        self.entry_client_pan.delete(0, tk.END)
        self.entry_client_gst.delete(0, tk.END)
        self.entry_client_mobile.delete(0, tk.END)
        self.entry_client_email.delete(0, tk.END)
        self.entry_client_address.delete(0, tk.END)
        self.combo_client_state.set('')
        self.entry_client_opening_bal.delete(0, tk.END)

    def on_client_select(self, event):
        selected = self.tree_clients.selection()
        if not selected: return
        item = self.tree_clients.item(selected[0])
        pan = item['values'][0]

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT ClientName, PAN, GSTIN, Mobile, Email, Address, State, OpeningBalance FROM tblClients WHERE PAN=?", (pan,))
        row = c.fetchone()
        conn.close()

        if row:
            self.clear_client_form()
            self.entry_client_name.insert(0, row[0] or '')
            self.entry_client_pan.insert(0, row[1] or '')
            self.entry_client_gst.insert(0, row[2] or '')
            self.entry_client_mobile.insert(0, row[3] or '')
            self.entry_client_email.insert(0, row[4] or '')
            self.entry_client_address.insert(0, row[5] or '')
            self.combo_client_state.set(row[6] or '')
            self.entry_client_opening_bal.insert(0, str(row[7] or ''))

    def save_client(self):
        name = self.entry_client_name.get().strip()
        pan = self.entry_client_pan.get().strip()

        if not name or not pan:
            messagebox.showerror("Error", "Client Name and PAN are required.")
            return

        conn = get_connection()
        c = conn.cursor()
        try:
            ob_val = self.entry_client_opening_bal.get().strip()
            ob = float(ob_val) if ob_val else 0.0
            c.execute("""
                INSERT INTO tblClients (ClientName, PAN, GSTIN, Mobile, Email, Address, State, OpeningBalance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                pan,
                self.entry_client_gst.get().strip(),
                self.entry_client_mobile.get().strip(),
                self.entry_client_email.get().strip(),
                self.entry_client_address.get().strip(),
                self.combo_client_state.get().strip(),
                ob
            ))
            conn.commit()
            messagebox.showinfo("Success", "Client saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save client. Does PAN already exist?\n{str(e)}")
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
        c.execute("""
            UPDATE tblClients SET
                ClientName=?, GSTIN=?, Mobile=?, Email=?, Address=?, State=?
            WHERE PAN=?
        """, (
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
        c.execute("UPDATE tblClients SET IsDeleted=1, DeletedOn=CURRENT_TIMESTAMP WHERE PAN=?", (pan,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Client deleted successfully.")
        self.refresh_clients_list()
        self.clear_client_form()
        self.refresh_client_dropdown()

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
        conn.close()

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
        if event.keysym in ('Up', 'Down', 'Left', 'Right', 'Return'):
            return

        value = event.widget.get()
        if value == '':
            self.combo_client['values'] = list(self.client_map.keys())
        else:
            data = []
            for item in self.client_map.keys():
                if value.lower() in item.lower():
                    data.append(item)
            self.combo_client['values'] = data

        if hasattr(self, 'combo_client'):
            self.combo_client.event_generate('<Down>')

    def on_service_selected(self, row_idx):
        row = self.service_rows[row_idx]
        selection = row['desc'].get()
        if " - " in selection:
            name, code = selection.rsplit(" - ", 1)
            row['desc'].set(selection)
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
                cgst_total = sum(i.get('CGST', 0) for i in items_data)
                sgst_total = sum(i['SGST'] for i in items_data)
                igst_total = sum(i['IGST'] for i in items_data)

                invoice_data['CGST'] = cgst_total
                invoice_data['SGST'] = sgst_total
                invoice_data['IGST'] = igst_total

            from business_logic import calculate_account_balance
            previous_due = calculate_account_balance(conn, client_id)
            invoice_data['PreviousDue'] = previous_due

            if inv_type == "GST":
                pdf_path = generate_gst_invoice(invoice_data, client_data, items_data)
                c.execute("""
                    INSERT INTO tblInvoices_GST (InvoiceNo, FinancialYear, InvoiceDate, DueDate, ClientID, TaxableValue, CGST, SGST, IGST, TotalAmount, PDFPath, BalanceAmount)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (inv_no, fy, date_str, date_str, client_id, total_taxable, cgst_total, sgst_total, igst_total, total_amount, pdf_path, total_amount))

                inv_db_id = c.lastrowid
                for idx, i in enumerate(items_data):
                    c.execute("INSERT INTO tblInvoiceItems_GST (InvoiceID, SrNo, ServiceDescription, SAC, Amount, TaxableValue, GSTRate, CGST, SGST, TotalAmount) VALUES (?,?,?,?,?,?,?,?,?,?)",
                              (inv_db_id, idx+1, i['ServiceDescription'], i['SAC'], i['Amount'], i['Amount'], 18, i['CGST'], i['SGST'], i['TotalAmount']))
            else:
                pdf_path = generate_normal_invoice(invoice_data, client_data, items_data)
                c.execute("""
                    INSERT INTO tblInvoices_Normal (InvoiceNo, FinancialYear, InvoiceDate, DueDate, ClientID, CurrentBill, PreviousDue, TotalAmount, PDFPath, BalanceAmount)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (inv_no, fy, date_str, date_str, client_id, total_taxable, previous_due, total_amount, pdf_path, total_amount))

                inv_db_id = c.lastrowid
                for idx, i in enumerate(items_data):
                    c.execute("INSERT INTO tblInvoiceItems_Normal (InvoiceID, SrNo, ServiceDescription, Amount, TotalAmount) VALUES (?,?,?,?,?)",
                              (inv_db_id, idx+1, i['ServiceDescription'], i['Amount'], i['TotalAmount']))

            conn.commit()

            # Offer WhatsApp Msg
            ans = messagebox.askyesno("Success", f"Invoice {inv_no} generated and saved at:\n{pdf_path}\n\nDo you want to send a WhatsApp notification to the client?")
            if ans:
                send_whatsapp_message(client_data['Mobile'], client_data['ClientName'], inv_no, total_amount)

            # Clear UI
            for row in self.service_rows:
                row['desc'].delete(0, tk.END)
                row['sac'].delete(0, tk.END)
                row['amt'].delete(0, tk.END)
            self.combo_client.set('')

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to generate invoice:\n{str(e)}")
        finally:
            conn.close()



    def open_invoice_pdf(self, event):
        selected = self.tree_invoices.selection()
        if not selected: return
        item = self.tree_invoices.item(selected[0])
        inv_no = item['values'][1]
        inv_type = item['values'][2]

        conn = get_connection()
        c = conn.cursor()

        pdf_path = None
        if inv_type == 'Normal':
            c.execute("SELECT PDFPath FROM tblInvoices_Normal WHERE InvoiceNo=?", (inv_no,))
        else:
            c.execute("SELECT PDFPath FROM tblInvoices_GST WHERE InvoiceNo=?", (inv_no,))

        row = c.fetchone()
        conn.close()

        if row and row[0]:
            pdf_path = row[0]
            if os.path.exists(pdf_path):
                import platform
                import subprocess
                try:
                    if platform.system() == 'Darwin':       # macOS
                        subprocess.call(('open', pdf_path))
                    elif platform.system() == 'Windows':    # Windows
                        os.startfile(pdf_path)
                    else:                                   # linux variants
                        subprocess.call(('xdg-open', pdf_path))
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to open PDF.\n{str(e)}")
            else:
                messagebox.showerror("Error", f"PDF file not found at path:\n{pdf_path}")
        else:
            messagebox.showerror("Error", "No PDF path found in database for this invoice.")

    def setup_receipts_tab(self):
        # Frame for List
        frame_list = ttk.LabelFrame(self.tab_receipts, text="All Invoices")
        frame_list.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ('Date', 'Invoice No', 'Type', 'Client Name', 'Total Amount', 'Received', 'Balance')
        self.tree_invoices = ttk.Treeview(frame_list, columns=columns, show='headings')
        for col in columns:
            self.tree_invoices.heading(col, text=col)
            self.tree_invoices.column(col, width=120)

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(frame_list, orient="vertical", command=self.tree_invoices.yview)
        self.tree_invoices.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree_invoices.pack(fill='both', expand=True)
        self.tree_invoices.bind("<Double-1>", self.open_invoice_pdf)

        # Tags for coloring
        self.tree_invoices.tag_configure('unpaid', background='#ffcccc') # Light red for unpaid/balance
        self.tree_invoices.tag_configure('paid', background='#ccffcc')   # Light green for paid

        # Action Frame
        frame_action = ttk.LabelFrame(self.tab_receipts, text="Receive Payment")
        frame_action.pack(fill='x', padx=10, pady=5)

        ttk.Label(frame_action, text="Date (DD-MM-YYYY):").pack(side='left', padx=5, pady=5)
        self.entry_payment_date = ttk.Entry(frame_action, width=12)
        self.entry_payment_date.insert(0, datetime.now().strftime("%d-%m-%Y"))
        self.entry_payment_date.pack(side='left', padx=5, pady=5)

        ttk.Label(frame_action, text="Mode:").pack(side='left', padx=5, pady=5)
        self.combo_payment_mode = ttk.Combobox(frame_action, values=["Cash", "Online", "Cheque", "Other"], width=10, state="readonly")
        self.combo_payment_mode.current(1)
        self.combo_payment_mode.pack(side='left', padx=5, pady=5)

        ttk.Label(frame_action, text="Amount (Rs.):").pack(side='left', padx=5, pady=5)
        self.entry_payment_amt = ttk.Entry(frame_action, width=12)
        self.entry_payment_amt.pack(side='left', padx=5, pady=5)

        ttk.Button(frame_action, text="Record Payment & Receipt", command=self.record_payment).pack(side='left', padx=15, pady=5)
        ttk.Button(frame_action, text="Refresh List", command=self.refresh_invoices_list).pack(side='right', padx=5, pady=5)

        # Historical Receipts View
        frame_hist = ttk.LabelFrame(self.tab_receipts, text="Receipt History (Select an Invoice above)")
        frame_hist.pack(fill='both', expand=True, padx=10, pady=5)

        hist_columns = ('Receipt ID', 'Date', 'Amount', 'Mode')
        self.tree_receipts = ttk.Treeview(frame_hist, columns=hist_columns, show='headings', height=5)
        for col in hist_columns:
            self.tree_receipts.heading(col, text=col)
            self.tree_receipts.column(col, width=100)
        self.tree_receipts.pack(fill='both', expand=True)

        self.tree_invoices.bind('<<TreeviewSelect>>', self.on_invoice_select_for_history, add='+')

        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_change)

    def on_tab_change(self, event):
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")
        if tab_text == "Invoice Tracking & Receipts":
            self.refresh_invoices_list()
        elif tab_text == "Cash Book & Bank Book":
            self.refresh_book('Cash')
            self.refresh_book('Bank')
        elif tab_text == "Recycle Bin":
            self.refresh_recycle_list()

    def setup_cash_bank_tab(self):
        # Notebook for Cash vs Bank
        self.nb_cb = ttk.Notebook(self.tab_cash_bank)
        self.nb_cb.pack(fill='both', expand=True, padx=10, pady=10)

        self.tab_cash = ttk.Frame(self.nb_cb)
        self.tab_bank = ttk.Frame(self.nb_cb)

        self.nb_cb.add(self.tab_cash, text="Cash Book")
        self.nb_cb.add(self.tab_bank, text="Bank Book")

        # Setup Cash Book
        self.setup_book_ui(self.tab_cash, 'Cash')

        # Setup Bank Book
        self.setup_book_ui(self.tab_bank, 'Bank')

    def setup_book_ui(self, parent_frame, book_type):
        # Entry Frame
        frame_entry = ttk.LabelFrame(parent_frame, text=f"Add Manual Entry to {book_type} Book")
        frame_entry.pack(fill='x', padx=10, pady=5)

        ttk.Label(frame_entry, text="Date:").grid(row=0, column=0, padx=5, pady=5)
        ent_date = ttk.Entry(frame_entry, width=12)
        from datetime import datetime
        ent_date.insert(0, datetime.now().strftime('%d-%m-%Y'))
        ent_date.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_entry, text="Particulars:").grid(row=0, column=2, padx=5, pady=5)
        ent_part = ttk.Entry(frame_entry, width=40)
        ent_part.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frame_entry, text="Receipt (Rs.):").grid(row=0, column=4, padx=5, pady=5)
        ent_rec = ttk.Entry(frame_entry, width=10)
        ent_rec.grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(frame_entry, text="Payment (Rs.):").grid(row=0, column=6, padx=5, pady=5)
        ent_pay = ttk.Entry(frame_entry, width=10)
        ent_pay.grid(row=0, column=7, padx=5, pady=5)


        btn_f = ttk.Frame(frame_entry)
        btn_f.grid(row=0, column=8, padx=10, pady=5)
        ttk.Button(btn_f, text="Add", command=lambda: self.add_book_entry(book_type, ent_date, ent_part, ent_rec, ent_pay)).pack(side='left', padx=2)
        ttk.Button(btn_f, text="Modify", command=lambda: self.modify_book_entry(book_type, ent_date, ent_part, ent_rec, ent_pay)).pack(side='left', padx=2)
        ttk.Button(btn_f, text="Delete", command=lambda: self.delete_book_entry(book_type)).pack(side='left', padx=2)
        ttk.Button(frame_entry, text="Export Excel", command=lambda: self.export_book(book_type)).grid(row=0, column=9, padx=10, pady=5)

        # List Frame
        columns = ('ID', 'Date', 'Particulars', 'Receipt', 'Payment', 'Balance')
        tree = ttk.Treeview(parent_frame, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
            if col in ('Receipt', 'Payment', 'Balance'):
                tree.column(col, anchor='e', width=100)
            elif col == 'ID':
                tree.column(col, width=50, anchor='center')
            else:
                tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill='both', expand=True, padx=10, pady=5)

        tree.bind('<<TreeviewSelect>>', lambda e: self.on_book_select(book_type, ent_date, ent_part, ent_rec, ent_pay))

        if book_type == 'Cash':
            self.tree_cash = tree
        else:
            self.tree_bank = tree

    def on_book_select(self, book_type, ent_date, ent_part, ent_rec, ent_pay):
        tree = self.tree_cash if book_type == 'Cash' else self.tree_bank
        selected = tree.selection()
        if not selected: return
        item = tree.item(selected[0])

        ent_date.delete(0, tk.END)
        ent_date.insert(0, item['values'][1])

        ent_part.delete(0, tk.END)
        ent_part.insert(0, item['values'][2])

        ent_rec.delete(0, tk.END)
        ent_rec.insert(0, str(item['values'][3]).replace('Rs. ', '') if item['values'][3] != '-' else '')

        ent_pay.delete(0, tk.END)
        ent_pay.insert(0, str(item['values'][4]).replace('Rs. ', '') if item['values'][4] != '-' else '')

    def modify_book_entry(self, book_type, ent_date, ent_part, ent_rec, ent_pay):
        tree = self.tree_cash if book_type == 'Cash' else self.tree_bank
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a row to modify.")
            return

        item = tree.item(selected[0])
        record_id = item['values'][0]

        d = ent_date.get().strip()
        p = ent_part.get().strip()
        r = ent_rec.get().strip() or "0"
        pay = ent_pay.get().strip() or "0"

        try:
            r = float(r)
            pay = float(pay)
        except:
            messagebox.showerror("Error", "Invalid amounts.")
            return

        table = 'tblCashBook' if book_type == 'Cash' else 'tblBankBook'
        pk = 'CashID' if book_type == 'Cash' else 'BankID'

        conn = get_connection()
        c = conn.cursor()
        c.execute(f"UPDATE {table} SET Date=?, Particulars=?, ReceiptAmount=?, PaymentAmount=? WHERE {pk}=?", (d, p, r, pay, record_id))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Record modified.")
        self.refresh_book(book_type)

    def delete_book_entry(self, book_type):
        tree = self.tree_cash if book_type == 'Cash' else self.tree_bank
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a row to delete.")
            return

        item = tree.item(selected[0])
        record_id = item['values'][0]

        if not messagebox.askyesno("Confirm", "Delete this record?"): return

        table = 'tblCashBook' if book_type == 'Cash' else 'tblBankBook'
        pk = 'CashID' if book_type == 'Cash' else 'BankID'

        conn = get_connection()
        c = conn.cursor()
        c.execute(f"DELETE FROM {table} WHERE {pk}=?", (record_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Record deleted.")
        self.refresh_book(book_type)

    def on_book_select(self, book_type, ent_date, ent_part, ent_rec, ent_pay):
        tree = self.tree_cash if book_type == 'Cash' else self.tree_bank
        selected = tree.selection()
        if not selected: return
        item = tree.item(selected[0])

        ent_date.delete(0, tk.END)
        ent_date.insert(0, item['values'][1])

        ent_part.delete(0, tk.END)
        ent_part.insert(0, item['values'][2])

        ent_rec.delete(0, tk.END)
        ent_rec.insert(0, str(item['values'][3]).replace('Rs. ', '') if item['values'][3] != '-' else '')

        ent_pay.delete(0, tk.END)
        ent_pay.insert(0, str(item['values'][4]).replace('Rs. ', '') if item['values'][4] != '-' else '')

    def modify_book_entry(self, book_type, ent_date, ent_part, ent_rec, ent_pay):
        tree = self.tree_cash if book_type == 'Cash' else self.tree_bank
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a row to modify.")
            return

        item = tree.item(selected[0])
        record_id = item['values'][0]

        d = ent_date.get().strip()
        p = ent_part.get().strip()
        r = ent_rec.get().strip() or "0"
        pay = ent_pay.get().strip() or "0"

        try:
            r = float(r)
            pay = float(pay)
        except:
            messagebox.showerror("Error", "Invalid amounts.")
            return

        table = 'tblCashBook' if book_type == 'Cash' else 'tblBankBook'
        pk = 'CashID' if book_type == 'Cash' else 'BankID'

        conn = get_connection()
        c = conn.cursor()
        c.execute(f"UPDATE {table} SET Date=?, Particulars=?, ReceiptAmount=?, PaymentAmount=? WHERE {pk}=?", (d, p, r, pay, record_id))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Record modified.")
        self.refresh_book(book_type)

    def delete_book_entry(self, book_type):
        tree = self.tree_cash if book_type == 'Cash' else self.tree_bank
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a row to delete.")
            return

        item = tree.item(selected[0])
        record_id = item['values'][0]

        if not messagebox.askyesno("Confirm", "Delete this record?"): return

        table = 'tblCashBook' if book_type == 'Cash' else 'tblBankBook'
        pk = 'CashID' if book_type == 'Cash' else 'BankID'

        conn = get_connection()
        c = conn.cursor()
        c.execute(f"DELETE FROM {table} WHERE {pk}=?", (record_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Record deleted.")
        self.refresh_book(book_type)

    def add_book_entry(self, book_type, w_date, w_part, w_rec, w_pay):
        date_str = w_date.get().strip()
        part = w_part.get().strip()
        rec_str = w_rec.get().strip()
        pay_str = w_pay.get().strip()

        if not part:
            messagebox.showerror("Error", "Particulars cannot be empty.")
            return

        try:
            rec = float(rec_str) if rec_str else 0.0
            pay = float(pay_str) if pay_str else 0.0
        except:
            messagebox.showerror("Error", "Invalid numeric amounts.")
            return

        conn = get_connection()
        c = conn.cursor()
        table = 'tblCashBook' if book_type == 'Cash' else 'tblBankBook'
        c.execute(f"INSERT INTO {table} (TxnDate, Particulars, Receipt, Payment) VALUES (?, ?, ?, ?)", (date_str, part, rec, pay))
        conn.commit()
        conn.close()

        w_part.delete(0, tk.END)
        w_rec.delete(0, tk.END)
        w_pay.delete(0, tk.END)
        self.refresh_cash_bank_lists()

    def refresh_book(self, book_type):
        tree = self.tree_cash if book_type == 'Cash' else self.tree_bank
        table = 'tblCashBook' if book_type == 'Cash' else 'tblBankBook'
        pk = 'CashID' if book_type == 'Cash' else 'BankID'

        for item in tree.get_children():
            tree.delete(item)

        conn = get_connection()
        c = conn.cursor()
        c.execute(f"SELECT {pk}, Date, Particulars, ReceiptAmount, PaymentAmount FROM {table} ORDER BY {pk} ASC")
        rows = c.fetchall()
        conn.close()

        running_balance = 0.0
        for row in rows:
            tid, d, p, r, pay = row
            running_balance += r - pay
            tree.insert('', tk.END, values=(tid, d, p, f"{r:.2f}", f"{pay:.2f}", f"{running_balance:.2f}"))

    def export_book(self, book_type):
        try:
            import pandas as pd
        except ImportError:
            messagebox.showerror("Error", "pandas is required for Excel export.")
            return

        tree = self.tree_cash if book_type == 'Cash' else self.tree_bank
        data = []
        for child in tree.get_children():
            data.append(tree.item(child)['values'])

        if not data:
            messagebox.showinfo("Info", "No data to export.")
            return

        from tkinter import filedialog
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")], title=f"Save {book_type} Book")
        if path:
            df = pd.DataFrame(data, columns=['ID', 'Date', 'Particulars', 'Receipt', 'Payment', 'Balance'])
            df.to_excel(path, index=False)
            messagebox.showinfo("Success", f"{book_type} Book exported successfully.")

    def on_book_select(self, book_type, ent_date, ent_part, ent_rec, ent_pay):
        tree = self.tree_cash if book_type == 'Cash' else self.tree_bank
        selected = tree.selection()
        if not selected: return
        item = tree.item(selected[0])

        ent_date.delete(0, tk.END)
        ent_date.insert(0, item['values'][1])

        ent_part.delete(0, tk.END)
        ent_part.insert(0, item['values'][2])

        ent_rec.delete(0, tk.END)
        ent_rec.insert(0, str(item['values'][3]).replace('Rs. ', '') if item['values'][3] != '-' else '')

        ent_pay.delete(0, tk.END)
        ent_pay.insert(0, str(item['values'][4]).replace('Rs. ', '') if item['values'][4] != '-' else '')

    def modify_book_entry(self, book_type, ent_date, ent_part, ent_rec, ent_pay):
        tree = self.tree_cash if book_type == 'Cash' else self.tree_bank
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a row to modify.")
            return

        item = tree.item(selected[0])
        record_id = item['values'][0]

        d = ent_date.get().strip()
        p = ent_part.get().strip()
        r = ent_rec.get().strip() or "0"
        pay = ent_pay.get().strip() or "0"

        try:
            r = float(r)
            pay = float(pay)
        except:
            messagebox.showerror("Error", "Invalid amounts.")
            return

        table = 'tblCashBook' if book_type == 'Cash' else 'tblBankBook'
        pk = 'CashID' if book_type == 'Cash' else 'BankID'

        conn = get_connection()
        c = conn.cursor()
        c.execute(f"UPDATE {table} SET Date=?, Particulars=?, ReceiptAmount=?, PaymentAmount=? WHERE {pk}=?", (d, p, r, pay, record_id))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Record modified.")
        self.refresh_book(book_type)

    def delete_book_entry(self, book_type):
        tree = self.tree_cash if book_type == 'Cash' else self.tree_bank
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a row to delete.")
            return

        item = tree.item(selected[0])
        record_id = item['values'][0]

        if not messagebox.askyesno("Confirm", "Delete this record?"): return

        table = 'tblCashBook' if book_type == 'Cash' else 'tblBankBook'
        pk = 'CashID' if book_type == 'Cash' else 'BankID'

        conn = get_connection()
        c = conn.cursor()
        c.execute(f"DELETE FROM {table} WHERE {pk}=?", (record_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Record deleted.")
        self.refresh_book(book_type)

    def add_book_entry(self, book_type, ent_date, ent_part, ent_rec, ent_pay):
        d = ent_date.get().strip()
        p = ent_part.get().strip()
        r = ent_rec.get().strip() or "0"
        pay = ent_pay.get().strip() or "0"

        try:
            r = float(r)
            pay = float(pay)
        except:
            messagebox.showerror("Error", "Invalid amounts.")
            return

        table = 'tblCashBook' if book_type == 'Cash' else 'tblBankBook'

        conn = get_connection()
        c = conn.cursor()
        c.execute(f"INSERT INTO {table} (Date, Particulars, ReceiptAmount, PaymentAmount) VALUES (?, ?, ?, ?)", (d, p, r, pay))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Record added.")
        ent_part.delete(0, tk.END)
        ent_rec.delete(0, tk.END)
        ent_pay.delete(0, tk.END)
        self.refresh_book(book_type)

    def setup_notes_tab(self):
        frame_top = ttk.LabelFrame(self.tab_notes, text="Issue Credit/Debit Note")
        frame_top.pack(fill='x', padx=10, pady=10)

        ttk.Label(frame_top, text="Note Type:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_note_type = ttk.Combobox(frame_top, values=["Credit Note", "Debit Note"], width=15, state='readonly')
        self.combo_note_type.set("Credit Note")
        self.combo_note_type.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_top, text="Against GST Invoice No:").grid(row=0, column=2, padx=5, pady=5)

        inv_frame = ttk.Frame(frame_top)
        inv_frame.grid(row=0, column=3, padx=5, pady=5)
        self.entry_note_inv = ttk.Entry(inv_frame, width=15)
        self.entry_note_inv.pack(side='left')
        ttk.Button(inv_frame, text="Select", command=self.open_invoice_selector).pack(side='left', padx=2)

        ttk.Label(frame_top, text="Date:").grid(row=0, column=4, padx=5, pady=5)
        self.entry_note_date = ttk.Entry(frame_top, width=12)
        from datetime import datetime
        self.entry_note_date.insert(0, datetime.now().strftime('%d-%m-%Y'))
        self.entry_note_date.grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(frame_top, text="Amount (Rs.):").grid(row=1, column=0, padx=5, pady=5)
        self.entry_note_amt = ttk.Entry(frame_top, width=15)
        self.entry_note_amt.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame_top, text="Reason:").grid(row=1, column=2, padx=5, pady=5)
        self.entry_note_reason = ttk.Entry(frame_top, width=40)
        self.entry_note_reason.grid(row=1, column=3, columnspan=3, padx=5, pady=5, sticky='w')

        ttk.Button(frame_top, text="Generate Note", command=self.generate_note).grid(row=2, column=0, columnspan=6, pady=10)

    def open_invoice_selector(self):
        top = tk.Toplevel(self)
        top.title("Select GST Invoice")
        top.geometry("600x400")
        top.transient(self)
        top.grab_set()

        columns = ('Invoice No', 'Date', 'Client Name', 'Total Amount')
        tree = ttk.Treeview(top, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        tree.pack(fill='both', expand=True, padx=10, pady=10)

        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            SELECT i.InvoiceNo, i.InvoiceDate, c.ClientName, i.TotalAmount
            FROM tblInvoices_GST i
            JOIN tblClients c ON i.ClientID = c.ClientID
            WHERE i.IsDeleted=0
            ORDER BY i.InvoiceID DESC
        """)
        for row in c.fetchall():
            tree.insert('', tk.END, values=row)
        conn.close()

        def on_select():
            selected = tree.selection()
            if not selected:
                messagebox.showerror("Error", "Please select an invoice.")
                return
            item = tree.item(selected[0])
            self.entry_note_inv.delete(0, tk.END)
            self.entry_note_inv.insert(0, item['values'][0])
            top.destroy()

        ttk.Button(top, text="Select", command=on_select).pack(pady=10)

    def generate_note(self):
        note_type = self.combo_note_type.get()
        inv_no = self.entry_note_inv.get().strip()
        date_str = self.entry_note_date.get().strip()
        amt_str = self.entry_note_amt.get().strip()
        reason = self.entry_note_reason.get().strip()

        if not all([inv_no, date_str, amt_str, reason]):
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            amt = float(amt_str)
        except:
            messagebox.showerror("Error", "Invalid amount.")
            return

        conn = get_connection()
        c = conn.cursor()

        # Verify GST invoice exists
        c.execute("SELECT ClientID, TotalAmount FROM tblInvoices_GST WHERE InvoiceNo=?", (inv_no,))
        row = c.fetchone()
        if not row:
            conn.close()
            messagebox.showerror("Error", "GST Invoice not found.")
            return

        client_id = row[0]

        # Get Client Info
        c.execute("SELECT ClientName, Address, PAN, GSTIN, State FROM tblClients WHERE ClientID=?", (client_id,))
        c_row = c.fetchone()
        if not c_row:
            conn.close()
            return

        client_data = {
            'ClientName': c_row[0],
            'Address': c_row[1],
            'PAN': c_row[2],
            'GSTIN': c_row[3],
            'State': c_row[4]
        }

        # Generate Note No
        from business_logic import get_financial_year
        fy = get_financial_year()
        prefix = "CN" if note_type == "Credit Note" else "DN"
        c.execute(f"SELECT NoteNo FROM tblCreditDebitNotes WHERE NoteNo LIKE '{prefix}/{fy}/%' ORDER BY NoteID DESC LIMIT 1")
        last_note = c.fetchone()
        if last_note:
            try:
                seq = int(last_note[0].split('/')[-1]) + 1
            except:
                seq = 1
        else:
            seq = 1

        note_no = f"{prefix}/{fy}/{seq:03d}"

        c.execute('''
            INSERT INTO tblCreditDebitNotes (NoteNo, NoteType, InvoiceNo, NoteDate, ClientID, Amount, Reason)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (note_no, note_type, inv_no, date_str, client_id, amt, reason))

        # Adjust account balance implicitly via negative/positive payment if required?
        # Actually user asked for notes just to issue them.
        # We can record it as a pseudo-payment to adjust balance automatically.
        if note_type == 'Credit Note':
            # Credit note reduces client's due -> acts like a Receipt
            c.execute("INSERT INTO tblPayments (InvoiceType, InvoiceID, PaymentDate, Amount, PaymentMode, ReferenceNo) SELECT 'GST', InvoiceID, ?, ?, ?, ? FROM tblInvoices_GST WHERE InvoiceNo=?", (date_str, amt, 'Credit Note Adjustment', note_no, inv_no))
        else:
            # Debit note increases due -> acts like negative Receipt
            c.execute("INSERT INTO tblPayments (InvoiceType, InvoiceID, PaymentDate, Amount, PaymentMode, ReferenceNo) SELECT 'GST', InvoiceID, ?, ?, ?, ? FROM tblInvoices_GST WHERE InvoiceNo=?", (date_str, -amt, 'Debit Note Adjustment', note_no, inv_no))

        conn.commit()

        # Generate PDF
        note_data = {
            'NoteNo': note_no,
            'NoteType': note_type,
            'Date': date_str,
            'InvoiceNo': inv_no,
            'Amount': amt,
            'Reason': reason,
            'CGST': 0.0,
            'SGST': 0.0,
            'IGST': 0.0,
            'TotalAmount': amt
        }

        from pdf_generator import generate_note_pdf
        pdf_path = generate_note_pdf(note_data, client_data)

        conn.close()

        messagebox.showinfo("Success", f"{note_type} generated at:\n{pdf_path}")
        self.entry_note_amt.delete(0, tk.END)
        self.entry_note_reason.delete(0, tk.END)

    def setup_recycle_tab(self):
        frame = ttk.LabelFrame(self.tab_recycle, text="Soft Deleted Items (>7 Days will be purged automatically)")
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ('Type', 'ID/No', 'Name/Desc', 'Deleted On')
        self.tree_recycle = ttk.Treeview(frame, columns=columns, show='headings')
        for col in columns:
            self.tree_recycle.heading(col, text=col)
            self.tree_recycle.column(col, width=150)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree_recycle.yview)
        self.tree_recycle.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree_recycle.pack(fill='both', expand=True)

        btn_frame = ttk.Frame(self.tab_recycle)
        btn_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(btn_frame, text="Restore Selected", command=self.restore_recycled).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Permanent Delete Selected", command=self.purge_recycled).pack(side='left', padx=5)

    def refresh_recycle_list(self):
        for item in self.tree_recycle.get_children():
            self.tree_recycle.delete(item)

        conn = get_connection()
        c = conn.cursor()

        # Auto Purge > 7 days logic
        from datetime import datetime, timedelta
        limit_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")

        c.execute("DELETE FROM tblClients WHERE IsDeleted=1 AND DeletedOn < ?", (limit_date,))
        c.execute("DELETE FROM tblInvoices_Normal WHERE IsDeleted=1 AND DeletedOn < ?", (limit_date,))
        c.execute("DELETE FROM tblInvoices_GST WHERE IsDeleted=1 AND DeletedOn < ?", (limit_date,))
        conn.commit()

        # Load clients
        c.execute("SELECT 'Client', PAN, ClientName, DeletedOn FROM tblClients WHERE IsDeleted=1")
        for r in c.fetchall():
            self.tree_recycle.insert('', tk.END, values=r)

        # Load Invoices Normal
        c.execute("SELECT 'Invoice Normal', InvoiceNo, TotalAmount, DeletedOn FROM tblInvoices_Normal WHERE IsDeleted=1")
        for r in c.fetchall():
            self.tree_recycle.insert('', tk.END, values=r)

        # Load Invoices GST
        c.execute("SELECT 'Invoice GST', InvoiceNo, TotalAmount, DeletedOn FROM tblInvoices_GST WHERE IsDeleted=1")
        for r in c.fetchall():
            self.tree_recycle.insert('', tk.END, values=r)

        conn.close()

    def restore_recycled(self):
        sel = self.tree_recycle.selection()
        if not sel: return
        item = self.tree_recycle.item(sel[0])['values']
        item_type, item_id = item[0], item[1]

        conn = get_connection()
        c = conn.cursor()
        if item_type == 'Client':
            c.execute("UPDATE tblClients SET IsDeleted=0, DeletedOn=NULL WHERE PAN=?", (item_id,))
        elif item_type == 'Invoice Normal':
            c.execute("UPDATE tblInvoices_Normal SET IsDeleted=0, DeletedOn=NULL WHERE InvoiceNo=?", (item_id,))
        elif item_type == 'Invoice GST':
            c.execute("UPDATE tblInvoices_GST SET IsDeleted=0, DeletedOn=NULL WHERE InvoiceNo=?", (item_id,))

        conn.commit()
        conn.close()
        self.refresh_recycle_list()

    def purge_recycled(self):
        sel = self.tree_recycle.selection()
        if not sel: return
        item = self.tree_recycle.item(sel[0])['values']
        item_type, item_id = item[0], item[1]

        if not messagebox.askyesno("Confirm", "Are you sure? This cannot be undone."): return

        conn = get_connection()
        c = conn.cursor()
        if item_type == 'Client':
            c.execute("DELETE FROM tblClients WHERE PAN=?", (item_id,))
        elif item_type == 'Invoice Normal':
            c.execute("DELETE FROM tblInvoices_Normal WHERE InvoiceNo=?", (item_id,))
        elif item_type == 'Invoice GST':
            c.execute("DELETE FROM tblInvoices_GST WHERE InvoiceNo=?", (item_id,))

        conn.commit()
        conn.close()
        self.refresh_recycle_list()

    def refresh_invoices_list(self):
        for item in self.tree_invoices.get_children():
            self.tree_invoices.delete(item)

        conn = get_connection()
        c = conn.cursor()

        # Combine Normal and GST Invoices
        query = '''
            SELECT i.InvoiceDate, i.InvoiceNo, 'Normal' as Type, c.ClientName, i.TotalAmount, i.InvoiceID
            FROM tblInvoices_Normal i
            JOIN tblClients c ON i.ClientID = c.ClientID
            UNION ALL
            SELECT i.InvoiceDate, i.InvoiceNo, 'GST' as Type, c.ClientName, i.TotalAmount, i.InvoiceID
            FROM tblInvoices_GST i
            JOIN tblClients c ON i.ClientID = c.ClientID
            ORDER BY InvoiceDate DESC, InvoiceNo DESC
        '''
        c.execute(query)
        invoices = c.fetchall()

        for inv in invoices:
            inv_date, inv_no, inv_type, client_name, total, inv_id = inv

            # Get received amount for this specific invoice
            c.execute("SELECT SUM(Amount) FROM tblPayments WHERE InvoiceID=? AND InvoiceType=?", (inv_id, inv_type))
            received = c.fetchone()[0] or 0.0
            balance = total - received

            tag = 'paid' if balance <= 0 else 'unpaid'

            self.tree_invoices.insert('', tk.END, values=(
                inv_date, inv_no, inv_type, client_name, f"{total:.2f}", f"{received:.2f}", f"{balance:.2f}"
            ), tags=(tag,))

        conn.close()

    def on_invoice_select_for_history(self, event):
        selected = self.tree_invoices.selection()
        if not selected: return
        item = self.tree_invoices.item(selected[0])
        inv_no = item['values'][1]
        inv_type = item['values'][2]

        for i in self.tree_receipts.get_children():
            self.tree_receipts.delete(i)

        conn = get_connection()
        c = conn.cursor()

        table = 'tblInvoices_Normal' if inv_type == 'Normal' else 'tblInvoices_GST'
        c.execute(f"SELECT InvoiceID FROM {table} WHERE InvoiceNo=?", (inv_no,))
        row = c.fetchone()
        if row:
            inv_id = row[0]
            c.execute("SELECT PaymentID, PaymentDate, Amount, PaymentMode FROM tblPayments WHERE InvoiceID=? AND InvoiceType=? AND IsDeleted=0 ORDER BY PaymentID DESC", (inv_id, inv_type))
            for r in c.fetchall():
                self.tree_receipts.insert('', tk.END, values=(f"RCPT-{r[0]}", r[1], f"Rs. {r[2]:.2f}", r[3]))
        conn.close()

    def record_payment(self):
        selected = self.tree_invoices.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an invoice to record payment against.")
            return

        item = self.tree_invoices.item(selected[0])
        inv_no = item['values'][1]
        inv_type = item['values'][2]
        client_name = item['values'][3]
        balance_str = item['values'][6]

        try:
            balance = float(balance_str)
        except:
            balance = 0.0

        if balance <= 0:
            messagebox.showinfo("Info", "This invoice is already fully paid.")
            return

        amt_str = self.entry_payment_amt.get().strip()
        if not amt_str:
            messagebox.showerror("Error", "Please enter payment amount.")
            return

        try:
            amt = float(amt_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid payment amount.")
            return

        if amt > balance:
            if not messagebox.askyesno("Warning", f"Amount (Rs. {amt}) is greater than balance (Rs. {balance}). Continue?"):
                return

        payment_date = self.entry_payment_date.get().strip()
        payment_mode = self.combo_payment_mode.get().strip()

        if not payment_date:
            messagebox.showerror("Error", "Please enter a payment date.")
            return

        conn = get_connection()
        c = conn.cursor()

        # Get InvoiceID
        table = 'tblInvoices_Normal' if inv_type == 'Normal' else 'tblInvoices_GST'
        c.execute(f"SELECT InvoiceID FROM {table} WHERE InvoiceNo=?", (inv_no,))
        row = c.fetchone()
        if not row:
            conn.close()
            messagebox.showerror("Error", "Invoice not found in database.")
            return

        inv_id = row[0]

        from business_logic import generate_receipt_number
        receipt_no = generate_receipt_number(conn)

        c.execute('''
            INSERT INTO tblPayments (InvoiceType, InvoiceID, PaymentDate, Amount, ReferenceNo, PaymentMode)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (inv_type, inv_id, payment_date, amt, receipt_no, payment_mode))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"Payment of Rs. {amt} recorded successfully.\nReceipt No: {receipt_no}")

        # WhatsApp Receipt msg
        ans = messagebox.askyesno("WhatsApp", f"Do you want to send a WhatsApp receipt to {client_name}?")
        if ans:
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT Mobile FROM tblClients WHERE ClientName=?", (client_name,))
            r = c.fetchone()
            conn.close()
            if r and r[0]:
                from business_logic import send_whatsapp_receipt
                send_whatsapp_receipt(r[0], client_name, receipt_no, inv_no, amt, balance - amt)

        self.entry_payment_amt.delete(0, tk.END)
        self.refresh_invoices_list()

        # Refresh clients list to update Account Balances
        self.refresh_clients_list()

if __name__ == "__main__":
    app = InvoicingApp()
    app.mainloop()
