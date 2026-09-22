from datetime import datetime
import urllib.parse
import webbrowser

def get_financial_year(date_obj=None):
    if date_obj is None:
        date_obj = datetime.now()

    year = date_obj.year
    month = date_obj.month

    # Financial year in India starts from April 1st
    if month >= 4:
        start_year = year
        end_year = year + 1
    else:
        start_year = year - 1
        end_year = year

    # Format as 26-27
    return f"{str(start_year)[-2:]}-{str(end_year)[-2:]}"

def generate_invoice_number(db_conn, invoice_type, date_obj=None):
    fy = get_financial_year(date_obj)

    cursor = db_conn.cursor()

    if invoice_type == 'GST':
        prefix = f"PAR/{fy}/"
        cursor.execute("SELECT InvoiceNo FROM tblInvoices_GST WHERE FinancialYear=? ORDER BY InvoiceID DESC LIMIT 1", (fy,))
    else:
        prefix = f"ITR/{fy}/"
        cursor.execute("SELECT InvoiceNo FROM tblInvoices_Normal WHERE FinancialYear=? ORDER BY InvoiceID DESC LIMIT 1", (fy,))

    row = cursor.fetchone()
    if row:
        last_no = row[0]
        try:
            seq = int(last_no.split('/')[-1]) + 1
        except:
            seq = 1
    else:
        seq = 1

    return f"{prefix}{seq:03d}"

def send_whatsapp_message(mobile_number, client_name, invoice_no, total_amount):
    """
    Formats the message and opens WhatsApp Web/Desktop to send to the client.
    """
    if not mobile_number:
        return False

    # Standardize number (assuming Indian +91 if length is 10)
    mobile_number = str(mobile_number).strip().replace(' ', '').replace('+', '')
    if len(mobile_number) == 10:
        mobile_number = f"91{mobile_number}"

    message = (
        f"Dear {client_name},\n\n"
        f"Your invoice ({invoice_no}) for the amount of Rs. {total_amount:.2f} has been generated.\n"
        f"Please find the attached invoice for your reference.\n\n"
        f"Thank you for your business.\n"
        f"Parigantavya Consultants"
    )

    encoded_message = urllib.parse.quote(message)
    url = f"whatsapp://send?phone={mobile_number}&text={encoded_message}"

    # Try to open via desktop app protocol, fallback to web
    try:
        webbrowser.open(url)
    except Exception:
        webbrowser.open(f"https://web.whatsapp.com/send?phone={mobile_number}&text={encoded_message}")

    return True
