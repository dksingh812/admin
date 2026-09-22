import re

with open('Invoicing/main.py', 'r') as f:
    content = f.read()

init_tabs = """
        self.tab_invoice = ttk.Frame(self.notebook)
        self.tab_clients = ttk.Frame(self.notebook)
        self.tab_receipts = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_invoice, text="Create Invoice")
        self.notebook.add(self.tab_clients, text="Manage Clients")
        self.notebook.add(self.tab_receipts, text="Invoice Tracking & Receipts")

        self.setup_clients_tab()
        self.setup_invoice_tab()
        self.setup_receipts_tab()
"""

content = re.sub(
    r'        self\.tab_invoice = ttk\.Frame\(self\.notebook\).*?self\.setup_invoice_tab\(\)',
    init_tabs,
    content,
    flags=re.DOTALL
)

receipt_methods = """
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

        # Tags for coloring
        self.tree_invoices.tag_configure('unpaid', background='#ffcccc') # Light red for unpaid/balance
        self.tree_invoices.tag_configure('paid', background='#ccffcc')   # Light green for paid

        # Action Frame
        frame_action = ttk.LabelFrame(self.tab_receipts, text="Receive Payment")
        frame_action.pack(fill='x', padx=10, pady=10)

        ttk.Label(frame_action, text="Amount Received (Rs.):").pack(side='left', padx=5, pady=5)
        self.entry_payment_amt = ttk.Entry(frame_action, width=15)
        self.entry_payment_amt.pack(side='left', padx=5, pady=5)

        ttk.Button(frame_action, text="Record Payment & Generate Receipt", command=self.record_payment).pack(side='left', padx=15, pady=5)
        ttk.Button(frame_action, text="Refresh List", command=self.refresh_invoices_list).pack(side='right', padx=5, pady=5)

        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_change)

    def on_tab_change(self, event):
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")
        if tab_text == "Invoice Tracking & Receipts":
            self.refresh_invoices_list()

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
            INSERT INTO tblPayments (InvoiceType, InvoiceID, PaymentDate, Amount, ReferenceNo)
            VALUES (?, ?, date('now'), ?, ?)
        ''', (inv_type, inv_id, amt, receipt_no))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"Payment of Rs. {amt} recorded successfully.\\nReceipt No: {receipt_no}")
        self.entry_payment_amt.delete(0, tk.END)
        self.refresh_invoices_list()

        # Refresh clients list to update Account Balances
        self.refresh_clients_list()
"""

# Append receipt_methods to the class
content = re.sub(
    r'(?s)(class InvoicingApp\(tk\.Tk\):.*)(if __name__ == "__main__":)',
    r'\1' + '\n' + receipt_methods + '\n' + r'\2',
    content
)

with open('Invoicing/main.py', 'w') as f:
    f.write(content)
