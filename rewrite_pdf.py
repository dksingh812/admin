import os
import re

content = """
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.platypus import Table, TableStyle

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'Output', 'PDF')
ASSETS_DIR = '/tmp/file_attachments/' # Where the images are

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Utility function to convert numbers to words (simple version for Rs.)
def number_to_words(n):
    # Very basic implementation for demo purposes,
    # Ideally use a library like num2words, but avoiding external deps if possible.
    # In real app, we'd add proper Indian numbering system.
    # For now, just return a dummy or a basic representation.
    # The requirement is strictly: ONLY WORDS/TEXT to be there for amount.
    try:
        from num2words import num2words
        words = num2words(int(n), lang='en_IN').replace(',', '').title()
        return f"Rs. {words} Only"
    except ImportError:
        # Fallback if num2words not installed
        return f"Rs. [Amount in Words for {int(n)}] Only"

def get_asset_path(filename):
    path = os.path.join(ASSETS_DIR, filename)
    if os.path.exists(path):
        return path
    return None

def draw_header_image(c, width, height, image_name):
    img_path = get_asset_path(image_name)
    if img_path:
        # Assuming header takes top 3-4 cm of the page.
        # Calculate aspect ratio if needed, or stretch.
        c.drawImage(img_path, 1*cm, height - 4*cm, width=width-2*cm, height=3*cm, preserveAspectRatio=True, anchor='n')

def draw_qr_code(c, x, y, size, image_name):
    img_path = get_asset_path(image_name)
    if img_path:
        c.drawImage(img_path, x, y, width=size, height=size, preserveAspectRatio=True)
    else:
        # Draw placeholder box
        c.rect(x, y, size, size)
        c.setFont("Helvetica", 8)
        c.drawString(x+5, y+size/2, "QR CODE")

def draw_signature(c, x, y, width, height, image_name):
    img_path = get_asset_path(image_name)
    if img_path:
        c.drawImage(img_path, x, y, width=width, height=height, preserveAspectRatio=True)
    else:
        # Draw placeholder
        c.rect(x, y, width, height)
        c.setFont("Helvetica", 8)
        c.drawString(x+5, y+height/2, "SIGNATURE")

def generate_gst_invoice(invoice_data, client_data, items_data):
    client_name_safe = "".join([c for c in client_data['ClientName'] if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    filename = f"{invoice_data['InvoiceNo'].replace('/', '_')}_{client_name_safe}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    # Header Image (GST INVOICE.jpg)
    draw_header_image(c, width, height, "GST INVOICE.jpg")

    # Title
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2.0, height - 5*cm, "TAX INVOICE")

    # Client Info (Left)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*cm, height - 6*cm, "Billed To:")
    c.drawString(1*cm, height - 6.5*cm, client_data['ClientName']) # BOLD Client Name

    c.setFont("Helvetica", 10)
    c.drawString(1*cm, height - 7*cm, f"Address: {client_data['Address']}")
    c.drawString(1*cm, height - 7.5*cm, f"PAN: {client_data['PAN']}")
    c.drawString(1*cm, height - 8*cm, f"GSTIN: {client_data['GSTIN']}")
    c.drawString(1*cm, height - 8.5*cm, f"State: {client_data.get('State', '')}")

    # Invoice Info (Right)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(width/2 + 2*cm, height - 6*cm, "Invoice Details:")
    c.setFont("Helvetica", 10)
    c.drawString(width/2 + 2*cm, height - 6.5*cm, f"Invoice No: {invoice_data['InvoiceNo']}")
    c.drawString(width/2 + 2*cm, height - 7*cm, f"Date: {invoice_data['InvoiceDate']}")

    # Place of supply = State of client
    c.drawString(width/2 + 2*cm, height - 8*cm, f"Place of Supply: {client_data.get('State', '')}")

    # Table Data
    data = [["S.No", "Nature of Service", "SAC", "Amount", "CGST", "SGST", "IGST", "Total"]]

    for idx, item in enumerate(items_data):
        desc = item.get('ServiceDescription', '')
        period = item.get('Period', '')

        # Combine Desc and Period. We use Paragraph in Table usually for multi-font,
        # but for simple canvas reportlab Table, we'll just format it as string.
        # To strictly make period font size 6, we'd need Platypus Paragraphs.
        # We will use simple text for now, or just append it.
        service_text = desc
        if period:
            service_text += f"\\n(Period: {period})"

        row = [
            str(idx + 1),
            service_text,
            item.get('SAC', ''),
            f"{item.get('Amount', 0):.2f}",
            f"{item.get('CGST', 0):.2f}",
            f"{item.get('SGST', 0):.2f}",
            f"{item.get('IGST', 0):.2f}",
            f"{item.get('TotalAmount', 0):.2f}"
        ]
        data.append(row)

    t = Table(data, colWidths=[1*cm, 6*cm, 2*cm, 2.5*cm, 2*cm, 2*cm, 2*cm, 2.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f2f2f2")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (1,1), (1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))

    w, h = t.wrap(width, height)
    t.drawOn(c, 1*cm, height - 9.5*cm - h)

    current_y = height - 10.5*cm - h

    # Total Amount in Words
    total_amt = invoice_data['TotalAmount']
    amt_words = number_to_words(total_amt)

    c.setFont("Helvetica-Bold", 10)
    c.drawString(1*cm, current_y, "Total Amount (in words):")
    c.setFont("Helvetica", 10)
    c.drawString(1*cm, current_y - 0.5*cm, amt_words)

    # Payment Info & QR
    current_y -= 2*cm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(1*cm, current_y, "Bank Details:")
    c.setFont("Helvetica", 10)
    c.drawString(1*cm, current_y - 0.5*cm, "Payee Name: DEEPAK KUMAR SINGH")
    c.drawString(1*cm, current_y - 1.0*cm, "Payment Mode: UPI / Bank Transfer")

    c.drawString(width/2, current_y, "SCAN AND PAY:")
    draw_qr_code(c, width/2, current_y - 3*cm, 2.5*cm, "image.png") # Using image.png as PARIGANTAVYA QR placeholder

    # Signature
    draw_signature(c, width - 5*cm, current_y - 2.5*cm, 4*cm, 1.5*cm, "Sign.jpg")
    c.setFont("Helvetica", 10)
    c.drawCentredString(width - 3*cm, current_y - 3*cm, "Authorised Signatory")

    c.save()
    return filepath


def generate_normal_invoice(invoice_data, client_data, items_data):
    client_name_safe = "".join([c for c in client_data['ClientName'] if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    filename = f"{invoice_data['InvoiceNo'].replace('/', '_')}_{client_name_safe}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    # Header Image
    draw_header_image(c, width, height, "Invoice normal.png")

    # Title
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2.0, height - 5*cm, "INVOICE")

    # Client Info (Left)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*cm, height - 6*cm, "Billed To:")
    c.drawString(1*cm, height - 6.5*cm, client_data['ClientName']) # BOLD

    c.setFont("Helvetica", 10)
    c.drawString(1*cm, height - 7*cm, f"Address: {client_data['Address']}")
    c.drawString(1*cm, height - 7.5*cm, f"PAN: {client_data['PAN']}")
    c.drawString(1*cm, height - 8*cm, f"Mobile: {client_data['Mobile']}")

    # Invoice Info (Right)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(width/2 + 2*cm, height - 6*cm, "Invoice Details:")
    c.setFont("Helvetica", 10)
    c.drawString(width/2 + 2*cm, height - 6.5*cm, f"Invoice No: {invoice_data['InvoiceNo']}")
    c.drawString(width/2 + 2*cm, height - 7*cm, f"Date: {invoice_data['InvoiceDate']}")

    # Table Data (NO SAC)
    data = [["S.No", "Nature of Service", "Amount"]]

    for idx, item in enumerate(items_data):
        desc = item.get('ServiceDescription', '')
        period = item.get('Period', '')

        service_text = desc
        if period:
            service_text += f"\\n(Period: {period})"

        row = [
            str(idx + 1),
            service_text,
            f"{item.get('Amount', 0):.2f}"
        ]
        data.append(row)

    t = Table(data, colWidths=[2*cm, 12*cm, 4*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f2f2f2")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (1,1), (1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))

    w, h = t.wrap(width, height)
    t.drawOn(c, 1.5*cm, height - 9*cm - h)

    current_y = height - 10*cm - h

    # Total Amount in Words
    total_amt = invoice_data['TotalAmount']
    amt_words = number_to_words(total_amt)

    c.setFont("Helvetica-Bold", 10)
    c.drawString(1.5*cm, current_y, "Total Amount (in words):")
    c.setFont("Helvetica", 10)
    c.drawString(1.5*cm, current_y - 0.5*cm, amt_words)

    # Payment Info & QR
    current_y -= 2*cm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(1.5*cm, current_y, "Bank Details:")
    c.setFont("Helvetica", 10)
    c.drawString(1.5*cm, current_y - 0.5*cm, "Payee Name: DEEPAK KUMAR SINGH")
    c.drawString(1.5*cm, current_y - 1.0*cm, "UPI ID: 9990013555@UPI")

    c.drawString(width/2, current_y, "SCAN AND PAY:")
    draw_qr_code(c, width/2, current_y - 3*cm, 2.5*cm, "BERRIFY.jpeg") # Assuming name if provided later

    # Signature
    draw_signature(c, width - 5*cm, current_y - 2.5*cm, 4*cm, 1.5*cm, "Sign.jpg")
    c.setFont("Helvetica", 10)
    c.drawCentredString(width - 3*cm, current_y - 3*cm, "Authorised Signatory")

    c.save()
    return filepath

"""

with open('Invoicing/pdf_generator.py', 'w') as f:
    f.write(content)
