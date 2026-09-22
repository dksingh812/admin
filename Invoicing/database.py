import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'invoicing.db')

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Create tables based on the user's requirements
    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS tblClients (
        ClientID INTEGER PRIMARY KEY AUTOINCREMENT,
        ClientCode TEXT,
        ClientName TEXT,
        BusinessName TEXT,
        PAN TEXT,
        GSTIN TEXT,
        ClientType TEXT,
        GroupName TEXT,
        Status TEXT,
        ResidentialStatus TEXT,
        Aadhaar TEXT,
        FatherHusbandName TEXT,
        DOB_DOI TEXT,
        Gender TEXT,
        Address TEXT,
        Mobile TEXT,
        Email TEXT,
        State TEXT,
        Notes TEXT,
        Active INTEGER DEFAULT 1,
        CreatedOn TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UpdatedOn TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS tblInvoices_Normal (
        InvoiceID INTEGER PRIMARY KEY AUTOINCREMENT,
        InvoiceNo TEXT UNIQUE,
        FinancialYear TEXT,
        InvoiceDate TEXT,
        DueDate TEXT,
        ClientID INTEGER,
        Description TEXT,
        CurrentBill REAL,
        PreviousDue REAL,
        TotalAmount REAL,
        ReceivedAmount REAL DEFAULT 0,
        BalanceAmount REAL,
        PaymentStatus TEXT,
        VerifiedStatus TEXT,
        PaymentMode TEXT,
        ReferenceNo TEXT,
        DocPath TEXT,
        PDFPath TEXT,
        CreatedOn TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(ClientID) REFERENCES tblClients(ClientID)
    );

    CREATE TABLE IF NOT EXISTS tblInvoices_GST (
        InvoiceID INTEGER PRIMARY KEY AUTOINCREMENT,
        InvoiceNo TEXT UNIQUE,
        FinancialYear TEXT,
        InvoiceDate TEXT,
        DueDate TEXT,
        ClientID INTEGER,
        PlaceOfSupply TEXT,
        SupplyType TEXT,
        ReverseCharge TEXT,
        NatureOfService TEXT,
        ReferenceNo TEXT,
        TaxableValue REAL,
        Discount REAL,
        IGST REAL,
        CGST REAL,
        SGST REAL,
        TotalAmount REAL,
        ReceivedAmount REAL DEFAULT 0,
        BalanceAmount REAL,
        PaymentStatus TEXT,
        VerifiedStatus TEXT,
        PaymentMode TEXT,
        DocPath TEXT,
        PDFPath TEXT,
        CreatedOn TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(ClientID) REFERENCES tblClients(ClientID)
    );

    CREATE TABLE IF NOT EXISTS tblInvoiceItems_Normal (
        ItemID INTEGER PRIMARY KEY AUTOINCREMENT,
        InvoiceID INTEGER,
        SrNo INTEGER,
        ServiceDescription TEXT,
        SAC TEXT,
        YearAY TEXT,
        Amount REAL,
        Discount REAL,
        TotalAmount REAL,
        Period TEXT,
        FOREIGN KEY(InvoiceID) REFERENCES tblInvoices_Normal(InvoiceID)
    );

    CREATE TABLE IF NOT EXISTS tblInvoiceItems_GST (
        ItemID INTEGER PRIMARY KEY AUTOINCREMENT,
        InvoiceID INTEGER,
        SrNo INTEGER,
        ServiceDescription TEXT,
        SAC TEXT,
        YearAY TEXT,
        Amount REAL,
        Discount REAL,
        TaxableValue REAL,
        GSTRate REAL,
        IGST REAL,
        CGST REAL,
        SGST REAL,
        TotalAmount REAL,
        Period TEXT,
        FOREIGN KEY(InvoiceID) REFERENCES tblInvoices_GST(InvoiceID)
    );

    CREATE TABLE IF NOT EXISTS tblSACHSN (
        SACCode TEXT PRIMARY KEY,
        SACName TEXT,
        GSTRate REAL,
        Active INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS tblPayments (
        PaymentID INTEGER PRIMARY KEY AUTOINCREMENT,
        InvoiceType TEXT,
        InvoiceID INTEGER,
        PaymentDate TEXT,
        Amount REAL,
        PaymentMode TEXT,
        ReferenceNo TEXT,
        Notes TEXT,
        CreatedOn TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    conn.commit()
    conn.close()

def seed_sac_codes():
    sac_data = [
        ('998211', 'Legal advisory', 18),
        ('998212', 'Legal advisory', 18),
        ('998213', 'Legal documentation and certification', 18),
        ('998214', 'Legal documentation and certification', 18),
        ('998215', 'Arbitration and conciliation services', 18),
        ('998216', 'Other legal services n.e.c.', 18),
        ('998221', 'Financial auditing services', 18),
        ('998222', 'Accounting and bookkeeping services', 18),
        ('998223', 'Payroll services', 18),
        ('998224', 'Other similar services n.e.c', 18),
        ('998231', 'Corporate tax consulting and preparation services', 18),
        ('998232', 'Individual tax preparation and planning services', 18),
        ('998311', 'Management consulting management services', 18),
        ('998312', 'Business consulting services', 18),
        ('998313', 'Information technology (IT)', 18),
        ('998314', 'Information technology (IT)', 18),
        ('998315', 'Hosting and information technology infrastructure provisioning services', 18),
        ('998316', 'IT infrastructure and network management services', 18),
        ('998319', 'Other information technology services n.e.c', 18),
        ('998387', 'Other Photography & Videography and their processing services n.e.c.', 18),
        ('998396', 'Trademarks and franchises', 18),
        ('998399', 'Other professional, technical and business services n.e.c.', 18),
        ('997156', 'Financial consultancy services', 18)
    ]

    conn = get_connection()
    cursor = conn.cursor()

    for code, name, rate in sac_data:
        cursor.execute('''
            INSERT OR IGNORE INTO tblSACHSN (SACCode, SACName, GSTRate, Active)
            VALUES (?, ?, ?, 1)
        ''', (code, name, rate))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    seed_sac_codes()
    print("Database initialized and seeded.")
