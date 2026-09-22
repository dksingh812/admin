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

        self.notebook.add(self.tab_invoice, text="Create Invoice")
        self.notebook.add(self.tab_clients, text="Manage Clients")

        self.setup_clients_tab()
        self.setup_invoice_tab()

    def setup_clients_tab(self):
        # Top Frame for Entry
        frame_top = ttk.LabelFrame(self.tab_clients, text="Client Details")
        frame_top.pack(fill='x', padx=10, pady=10)

        ttk.Label(frame_top, text="Client Name:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.entry_client_name = ttk.Entry(frame_top, width=40)
        self.entry_client_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_top, text="PAN:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.entry_client_pan = ttk.Entry(frame_top, width=20)
        self.entry_client_pan.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frame_top, text="GSTIN:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.entry_client_gst = ttk.Entry(frame_top, width=40)
        self.entry_client_gst.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame_top, text="Mobile:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.entry_client_mobile = ttk.Entry(frame_top, width=20)
        self.entry_client_mobile.grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(frame_top, text="Email:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.entry_client_email = ttk.Entry(frame_top, width=40)
        self.entry_client_email.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(frame_top, text="Address:").grid(row=2, column=2, padx=5, pady=5, sticky='w')
        self.entry_client_address = ttk.Entry(frame_top, width=40)
        self.entry_client_address.grid(row=2, column=3, padx=5, pady=5)

        ttk.Button(frame_top, text="Save Client", command=self.save_client).grid(row=3, column=0, columnspan=4, pady=10)

        # Bottom Frame for List
        frame_bottom = ttk.LabelFrame(self.tab_clients, text="Client List")
        frame_bottom.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ('ID', 'Name', 'PAN', 'Mobile', 'Email')
        self.tree_clients = ttk.Treeview(frame_bottom, columns=columns, show='headings')
        for col in columns:
            self.tree_clients.heading(col, text=col)
            self.tree_clients.column(col, width=150)
        self.tree_clients.column('ID', width=50)
        self.tree_clients.pack(fill='both', expand=True)

        self.refresh_clients_list()

    def save_client(self):
        name = self.entry_client_name.get().strip()
        pan = self.entry_client_pan.get().strip()

        if not name:
            messagebox.showerror("Error", "Client Name is required.")
            return

        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            INSERT INTO tblClients (ClientName, PAN, GSTIN, Mobile, Email, Address)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name,
            pan,
            self.entry_client_gst.get().strip(),
            self.entry_client_mobile.get().strip(),
            self.entry_client_email.get().strip(),
            self.entry_client_address.get().strip()
        ))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Client saved successfully.")
        self.refresh_clients_list()

        # Clear fields
        self.entry_client_name.delete(0, tk.END)
        self.entry_client_pan.delete(0, tk.END)
        self.entry_client_gst.delete(0, tk.END)
        self.entry_client_mobile.delete(0, tk.END)
        self.entry_client_email.delete(0, tk.END)
        self.entry_client_address.delete(0, tk.END)

        # Refresh client dropdown in invoice tab
        self.refresh_client_dropdown()

    def refresh_clients_list(self):
        for item in self.tree_clients.get_children():
            self.tree_clients.delete(item)

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT ClientID, ClientName, PAN, Mobile, Email FROM tblClients")
        for row in c.fetchall():
            self.tree_clients.insert('', tk.END, values=row)
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

        self.combo_client = ttk.Combobox(frame_client, state='readonly', width=50)
        self.combo_client.pack(side='left', padx=5, pady=5)
        self.refresh_client_dropdown()

        # Services Line Items
        frame_services = ttk.LabelFrame(self.tab_invoice, text="Services (Max 5)")
        frame_services.pack(fill='both', expand=True, padx=10, pady=5)

        self.service_rows = []

        headers = ["Service Description", "SAC Code", "Amount (Rs.)"]
        for col, h in enumerate(headers):
            ttk.Label(frame_services, text=h, font=('', 9, 'bold')).grid(row=0, column=col, padx=5, pady=5)

        for i in range(5):
            desc = ttk.Entry(frame_services, width=40)
            desc.grid(row=i+1, column=0, padx=5, pady=2)

            sac = ttk.Entry(frame_services, width=15)
            sac.grid(row=i+1, column=1, padx=5, pady=2)

            amt = ttk.Entry(frame_services, width=15)
            amt.grid(row=i+1, column=2, padx=5, pady=2)

            self.service_rows.append({'desc': desc, 'sac': sac, 'amt': amt})

        # Action buttons
        frame_actions = ttk.Frame(self.tab_invoice)
        frame_actions.pack(fill='x', padx=10, pady=10)

        ttk.Button(frame_actions, text="Generate Invoice", command=self.generate_invoice).pack(side='right', padx=5)

    def refresh_client_dropdown(self):
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT ClientID, ClientName FROM tblClients")
        self.client_map = {f"{row[1]} (ID: {row[0]})": row[0] for row in c.fetchall()}
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
        if not client_sel:
            messagebox.showerror("Error", "Please select a client.")
            return

        client_id = self.client_map[client_sel]
        inv_type = self.inv_type.get()

        items_data = []
        total_amount = 0
        total_taxable = 0

        for row in self.service_rows:
            desc = row['desc'].get().strip()
            amt_str = row['amt'].get().strip()
            sac = row['sac'].get().strip()

            if desc and amt_str:
                try:
                    amt = float(amt_str)
                except:
                    messagebox.showerror("Error", "Invalid amount entered.")
                    return

                total_taxable += amt

                item = {
                    'ServiceDescription': desc,
                    'SAC': sac,
                    'Amount': amt
                }

                if inv_type == 'GST':
                    # Assuming intra-state 18% for simple calculation as per rules
                    cgst = amt * 0.09
                    sgst = amt * 0.09
                    igst = 0

                    item['CGST'] = cgst
                    item['SGST'] = sgst
                    item['IGST'] = igst
                    item['TotalAmount'] = amt + cgst + sgst

                    total_amount += item['TotalAmount']
                else:
                    item['TotalAmount'] = amt
                    total_amount += amt

                items_data.append(item)

        if not items_data:
            messagebox.showerror("Error", "Please enter at least one service.")
            return

        conn = get_connection()
        c = conn.cursor()

        # Get Client Data
        c.execute("SELECT ClientName, PAN, GSTIN, Mobile, Email, Address FROM tblClients WHERE ClientID=?", (client_id,))
        client_row = c.fetchone()
        client_data = {
            'ClientName': client_row[0],
            'PAN': client_row[1],
            'GSTIN': client_row[2],
            'Mobile': client_row[3],
            'Email': client_row[4],
            'Address': client_row[5]
        }

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
                cgst_total = sum(i['CGST'] for i in items_data)
                sgst_total = sum(i['SGST'] for i in items_data)
                igst_total = sum(i['IGST'] for i in items_data)

                invoice_data['CGST'] = cgst_total
                invoice_data['SGST'] = sgst_total
                invoice_data['IGST'] = igst_total

                c.execute("""
                    INSERT INTO tblInvoices_GST (InvoiceNo, FinancialYear, InvoiceDate, DueDate, ClientID, TaxableValue, CGST, SGST, IGST, TotalAmount)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (inv_no, fy, date_str, date_str, client_id, total_taxable, cgst_total, sgst_total, igst_total, total_amount))

                inv_db_id = c.lastrowid
                for idx, i in enumerate(items_data):
                    c.execute("INSERT INTO tblInvoiceItems_GST (InvoiceID, SrNo, ServiceDescription, SAC, Amount, TaxableValue, GSTRate, CGST, SGST, TotalAmount) VALUES (?,?,?,?,?,?,?,?,?,?)",
                              (inv_db_id, idx+1, i['ServiceDescription'], i['SAC'], i['Amount'], i['Amount'], 18, i['CGST'], i['SGST'], i['TotalAmount']))

                pdf_path = generate_gst_invoice(invoice_data, client_data, items_data)
            else:
                c.execute("""
                    INSERT INTO tblInvoices_Normal (InvoiceNo, FinancialYear, InvoiceDate, DueDate, ClientID, CurrentBill, TotalAmount)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (inv_no, fy, date_str, date_str, client_id, total_taxable, total_amount))

                inv_db_id = c.lastrowid
                for idx, i in enumerate(items_data):
                    c.execute("INSERT INTO tblInvoiceItems_Normal (InvoiceID, SrNo, ServiceDescription, Amount, TotalAmount) VALUES (?,?,?,?,?)",
                              (inv_db_id, idx+1, i['ServiceDescription'], i['Amount'], i['TotalAmount']))

                pdf_path = generate_normal_invoice(invoice_data, client_data, items_data)

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

if __name__ == "__main__":
    app = InvoicingApp()
    app.mainloop()
