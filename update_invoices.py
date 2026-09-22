import sqlite3
import os

DB_PATH = os.path.join('Invoicing', 'invoicing.db')

def update_invoices_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Ensure there's a Period field in tblInvoiceItems_GST and tblInvoiceItems_Normal

    try:
        cursor.execute("ALTER TABLE tblInvoiceItems_Normal ADD COLUMN Period TEXT;")
    except:
        pass

    try:
        cursor.execute("ALTER TABLE tblInvoiceItems_GST ADD COLUMN Period TEXT;")
    except:
        pass

    conn.commit()
    conn.close()

if __name__ == '__main__':
    update_invoices_table()
