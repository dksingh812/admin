import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.platypus import Table, TableStyle

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'Output', 'PDF')
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def generate_gst_invoice(invoice_data, client_data, items_data):
    """
    Generate GST Invoice PDF according to Parigantavya Consultants design.
    """
    # Safe filename
    client_name_safe = "".join([c for c in client_data['ClientName'] if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    filename = f"{invoice_data['InvoiceNo'].replace('/', '_')}_{client_name_safe}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    # 1. Header Area
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.HexColor("#3b5998")) # Approximate Blue from template
    c.drawString(1*cm, height - 2*cm, "Parigantavya Consultants")

    c.setFont("Helvetica", 9)
    c.setFillColor(colors.gray)
    c.drawString(1*cm, height - 2.5*cm, "Growing Your Expectations")

    c.setFont("Helvetica", 8)
    c.setFillColor(colors.black)
    c.drawRightString(width - 1*cm, height - 1.5*cm, "Laxmanpuram Colony, Baraudha")
    c.drawRightString(width - 1*cm, height - 1.9*cm, "Mirzapur, Uttar Pradesh-231001")
    c.drawRightString(width - 1*cm, height - 2.3*cm, "+91-5442316600, +91-9990013555")
    c.drawRightString(width - 1*cm, height - 2.7*cm, "parigantavya@outlook.com")

    # Horizontal line
    c.setStrokeColor(colors.lightblue)
    c.setLineWidth(2)
    c.line(1*cm, height - 3*cm, width - 1*cm, height - 3*cm)

    # Title
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.black)
    c.drawCentredString(width/2.0, height - 4*cm, "TAX INVOICE")

    # 2. Client & Invoice Info (Two Columns)
    y_start = height - 4.5*cm
    c.setStrokeColor(colors.lightblue)
    c.setLineWidth(1)

    # Box around details
    c.rect(1*cm, height - 9.5*cm, width - 2*cm, 5*cm)
    c.line(width/2.0, height - 9.5*cm, width/2.0, height - 4.5*cm) # center divider

    c.setFont("Helvetica-Bold", 10)
    c.drawString(1.2*cm, y_start - 0.5*cm, "Bill To / Client's Name:")
    c.drawString(width/2.0 + 0.2*cm, y_start - 0.5*cm, "Invoice Details:")

    c.setFont("Helvetica", 9)
    # Left Column (Client)
    c.drawString(1.2*cm, y_start - 1.5*cm, f"Client Name : {client_data.get('ClientName', '')}")
    c.drawString(1.2*cm, y_start - 2.0*cm, f"PAN : {client_data.get('PAN', '')}")
    c.drawString(1.2*cm, y_start - 2.5*cm, f"GSTIN : {client_data.get('GSTIN', '')}")
    c.drawString(1.2*cm, y_start - 3.0*cm, f"Contact No. : {client_data.get('Mobile', '')}")
    c.drawString(1.2*cm, y_start - 3.5*cm, f"Email : {client_data.get('Email', '')}")
    c.drawString(1.2*cm, y_start - 4.0*cm, f"Billing Address : {client_data.get('Address', '')}")

    # Right Column (Invoice)
    c.drawString(width/2.0 + 0.2*cm, y_start - 1.5*cm, f"Invoice No. : {invoice_data.get('InvoiceNo', '')}")
    c.drawString(width/2.0 + 0.2*cm, y_start - 2.0*cm, f"Invoice Date : {invoice_data.get('InvoiceDate', '')}")
    c.drawString(width/2.0 + 0.2*cm, y_start - 2.5*cm, f"Due Date : {invoice_data.get('DueDate', '')}")
    c.drawString(width/2.0 + 0.2*cm, y_start - 3.0*cm, f"Place of Supply : {invoice_data.get('PlaceOfSupply', '')}")
    c.drawString(width/2.0 + 0.2*cm, y_start - 3.5*cm, f"Reverse Charge : {invoice_data.get('ReverseCharge', 'No')}")
    c.drawString(width/2.0 + 0.2*cm, y_start - 4.0*cm, f"Nature of Service : {invoice_data.get('NatureOfService', '')}")
    c.drawString(width/2.0 + 0.2*cm, y_start - 4.5*cm, f"Reference No. : {invoice_data.get('ReferenceNo', '')}")

    # 3. Items Table
    table_data = [["Sr. No.", "Description of Service", "SAC/HSN", "Amount\n(Rs)", "GST\n(Rs)", "Total Amount\n(Rs)"]]
    for i, item in enumerate(items_data):
        row = [
            str(i+1),
            item.get('ServiceDescription', ''),
            item.get('SAC', ''),
            f"{item.get('Amount', 0):.2f}",
            f"{(item.get('CGST', 0) + item.get('SGST', 0) + item.get('IGST', 0)):.2f}",
            f"{item.get('TotalAmount', 0):.2f}"
        ]
        table_data.append(row)

    # Fill remaining empty rows to maintain minimum height (e.g. 5 rows)
    while len(table_data) <= 5:
        table_data.append(["", "", "", "", "", ""])

    # Total Row
    total_val = invoice_data.get('TotalAmount', 0)
    table_data.append(["", "", "", "", "TOTAL AMOUNT", f"Rs {total_val:.2f}"])

    t = Table(table_data, colWidths=[1.5*cm, 7*cm, 2.5*cm, 2.5*cm, 2.5*cm, 3*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (1,1), (1,-2), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('GRID', (0,0), (-1,-1), 1, colors.lightblue),
        ('FONTNAME', (-2,-1), (-1,-1), 'Helvetica-Bold')
    ]))

    t.wrapOn(c, width, height)
    t.drawOn(c, 1*cm, height - 16.5*cm) # Adjust Y appropriately based on row count

    # 4. In Words & GST Breakdown
    y_words = height - 17.5*cm
    c.rect(1*cm, y_words, width - 2*cm, 1.5*cm)
    c.line(1*cm, y_words + 0.75*cm, width - 1*cm, y_words + 0.75*cm) # horizontal middle divider

    c.setFont("Helvetica-Bold", 9)
    c.drawString(1.2*cm, y_words + 0.95*cm, "Total Invoice Value (In Words)   :")
    c.setFont("Helvetica", 9)
    # Very basic number to words logic should be imported or implemented, defaulting to placeholder
    c.drawString(6*cm, y_words + 0.95*cm, f"Rupees {total_val} Only (Amount in words TBD)")

    c.setFont("Helvetica-Bold", 9)
    c.drawString(1.2*cm, y_words + 0.2*cm, "GST Details                                :")
    c.setFont("Helvetica", 9)
    igst = invoice_data.get('IGST', 0)
    cgst = invoice_data.get('CGST', 0)
    sgst = invoice_data.get('SGST', 0)
    c.drawString(6*cm, y_words + 0.2*cm, f"IGST @18%   Rs {igst:.2f}")
    c.drawString(10*cm, y_words + 0.2*cm, f"CGST @9%   Rs {cgst:.2f}")
    c.drawString(14*cm, y_words + 0.2*cm, f"SGST @9%   Rs {sgst:.2f}")

    # 5. Payment Details & Footer
    y_footer = height - 23*cm
    c.rect(1*cm, y_footer, width - 2*cm, 5*cm)
    c.line(14*cm, y_footer, 14*cm, y_footer + 5*cm) # vertical split for QR

    c.setFont("Helvetica-Bold", 10)
    c.drawString(1.2*cm, y_footer + 4.5*cm, "Payment Details:")
    c.setFont("Helvetica", 9)
    c.drawString(1.2*cm, y_footer + 3.8*cm, "In favour of : DEEPAK KUMAR SINGH")
    c.drawString(1.2*cm, y_footer + 3.3*cm, "Bank & Branch : STATE BANK OF INDIA")
    c.drawString(1.2*cm, y_footer + 2.8*cm, "Account No. : 030919594941")
    c.drawString(1.2*cm, y_footer + 2.3*cm, "IFSC Code : SBIN0003879")
    c.drawString(1.2*cm, y_footer + 1.8*cm, f"Payment Mode : {invoice_data.get('PaymentMode', 'UPI / Bank Transfer / Cheque / Cash')}")

    # QR Code placeholder
    c.drawCentredString(17*cm, y_footer + 4.5*cm, "SCAN & PAY")
    c.drawCentredString(17*cm, y_footer + 1.2*cm, "UPI ID : parigantavya@sbi")

    # Footer Notes
    y_notes = y_footer - 2.5*cm
    c.rect(1*cm, y_notes, width - 2*cm, 2*cm)
    c.line(14*cm, y_notes, 14*cm, y_notes + 2*cm)

    c.setFont("Helvetica-Bold", 9)
    c.drawString(1.2*cm, y_notes + 1.5*cm, "Note:")
    c.setFont("Helvetica", 8)
    c.drawString(1.2*cm, y_notes + 1.0*cm, "● THANK YOU FOR YOUR BUSINESS.")
    c.drawString(1.2*cm, y_notes + 0.5*cm, "● SUBJECT TO MIRZAPUR JURISDICTION ONLY")

    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(17*cm, y_notes + 1.5*cm, "For Parigantavya Consultants")
    c.line(14.5*cm, y_notes + 0.5*cm, 19.5*cm, y_notes + 0.5*cm)
    c.setFont("Helvetica", 8)
    c.drawCentredString(17*cm, y_notes + 0.2*cm, "(Authorised Signatory)")

    c.save()
    return filepath

def generate_normal_invoice(invoice_data, client_data, items_data):
    """
    Generate Normal Invoice PDF according to Berrify & Associates design.
    """
    client_name_safe = "".join([c for c in client_data['ClientName'] if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    filename = f"{invoice_data['InvoiceNo'].replace('/', '_')}_{client_name_safe}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    # 1. Header Area
    c.setFillColor(colors.HexColor("#1c2e4a")) # Dark Blue
    c.rect(0, height - 3*cm, width, 3*cm, fill=1, stroke=0)

    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(colors.white)
    c.drawString(1*cm, height - 1.5*cm, "BERRIFY & ASSOCIATES")

    c.setFont("Helvetica", 10)
    c.drawString(1*cm, height - 2.2*cm, "Chamber No. 119, New Building, High Court Allahabad")

    # Yellow triangle accent (approximate from image)
    c.setFillColor(colors.orange)
    p = c.beginPath()
    p.moveTo(width/2.0, height)
    p.lineTo(width, height)
    p.lineTo(width, height - 3*cm)
    c.drawPath(p, fill=1, stroke=0)

    c.setFillColor(colors.black)
    c.setFont("Helvetica", 9)
    c.drawRightString(width - 1*cm, height - 1*cm, "+91 - 990013555")
    c.drawRightString(width - 1*cm, height - 1.5*cm, "berrify@outlook.com")
    c.drawRightString(width - 1*cm, height - 2*cm, "ca_deepak@outlook.com")

    # Title
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.black)
    c.drawCentredString(width/2.0, height - 4*cm, "INVOICE")

    # 2. Client & Invoice Info
    y_start = height - 4.5*cm
    c.setStrokeColor(colors.lightblue)
    c.rect(1*cm, height - 9.5*cm, width - 2*cm, 5*cm)
    c.line(width/2.0, height - 9.5*cm, width/2.0, height - 4.5*cm)

    c.setFont("Helvetica-Bold", 10)
    c.drawString(1.2*cm, y_start - 0.5*cm, "Bill To / Client's Name:")
    c.drawString(width/2.0 + 0.2*cm, y_start - 0.5*cm, "Invoice Details:")

    c.setFont("Helvetica", 9)
    c.drawString(1.2*cm, y_start - 1.5*cm, f"Client Name : {client_data.get('ClientName', '')}")
    c.drawString(1.2*cm, y_start - 2.0*cm, f"PAN : {client_data.get('PAN', '')}")
    c.drawString(1.2*cm, y_start - 2.5*cm, f"Contact No. : {client_data.get('Mobile', '')}")
    c.drawString(1.2*cm, y_start - 3.0*cm, f"Email : {client_data.get('Email', '')}")
    c.drawString(1.2*cm, y_start - 3.5*cm, f"Billing Address : {client_data.get('Address', '')}")

    c.drawString(width/2.0 + 0.2*cm, y_start - 1.5*cm, f"Invoice No. : {invoice_data.get('InvoiceNo', '')}")
    c.drawString(width/2.0 + 0.2*cm, y_start - 2.0*cm, f"Invoice Date : {invoice_data.get('InvoiceDate', '')}")
    c.drawString(width/2.0 + 0.2*cm, y_start - 2.5*cm, f"Due Date : {invoice_data.get('DueDate', '')}")
    c.drawString(width/2.0 + 0.2*cm, y_start - 3.0*cm, f"Nature of Service : {invoice_data.get('Description', '')}")
    c.drawString(width/2.0 + 0.2*cm, y_start - 3.5*cm, f"Reference No. : {invoice_data.get('ReferenceNo', '')}")

    # 3. Items Table
    table_data = [["S.No.", "Particulars", "Amount (Rs.)"]]
    for i, item in enumerate(items_data):
        row = [
            str(i+1),
            item.get('ServiceDescription', ''),
            f"{item.get('Amount', 0):.2f}"
        ]
        table_data.append(row)

    while len(table_data) <= 5:
        table_data.append(["", "", ""])

    total_val = invoice_data.get('TotalAmount', 0)
    table_data.append(["", "Total", f"Rs {total_val:.2f}"])

    t = Table(table_data, colWidths=[2*cm, 12*cm, 5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (1,1), (1,-2), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('GRID', (0,0), (-1,-1), 1, colors.lightblue),
        ('FONTNAME', (-2,-1), (-1,-1), 'Helvetica-Bold')
    ]))

    t.wrapOn(c, width, height)
    t.drawOn(c, 1*cm, height - 16.5*cm)

    # 4. In Words
    y_words = height - 18.5*cm
    c.rect(1*cm, y_words, width - 2*cm, 1.5*cm)
    c.line(1*cm, y_words + 0.75*cm, width - 1*cm, y_words + 0.75*cm)
    c.line(6.5*cm, y_words, 6.5*cm, y_words + 1.5*cm)

    c.setFont("Helvetica-Bold", 9)
    c.drawString(1.2*cm, y_words + 0.95*cm, "Total Invoice Value (In Figures)")
    c.drawString(1.2*cm, y_words + 0.2*cm, "Total Invoice Value (In Words)")
    c.setFont("Helvetica", 9)
    c.drawString(7*cm, y_words + 0.95*cm, f"Rs {total_val:.2f}")
    c.drawString(7*cm, y_words + 0.2*cm, f"Rupees {total_val} Only")

    # 5. Payment Details
    y_footer = height - 24*cm
    c.rect(1*cm, y_footer, width - 2*cm, 5*cm)
    c.line(14*cm, y_footer, 14*cm, y_footer + 5*cm)

    c.setFont("Helvetica-Bold", 10)
    c.drawString(1.2*cm, y_footer + 4.5*cm, "Payment Details:")
    c.setFont("Helvetica", 9)
    c.drawString(1.2*cm, y_footer + 3.8*cm, "In favour of : DEEPAK KUMAR SINGH")
    c.drawString(1.2*cm, y_footer + 3.3*cm, "Bank : STATE BANK OF INDIA")
    c.drawString(1.2*cm, y_footer + 2.8*cm, "Branch : HIGH COURT ALLAHABAD")
    c.drawString(1.2*cm, y_footer + 2.3*cm, "Account No. : 030919594941")
    c.drawString(1.2*cm, y_footer + 1.8*cm, "IFSC Code : SBIN0003879")
    c.drawString(1.2*cm, y_footer + 1.3*cm, f"Payment Mode : {invoice_data.get('PaymentMode', 'UPI / Bank Transfer / Cheque / Cash')}")

    c.drawCentredString(17*cm, y_footer + 4.5*cm, "SCAN & PAY")
    c.drawCentredString(17*cm, y_footer + 1.2*cm, "UPI ID : parigantavya@sbi")

    # 6. Footer Notes
    y_notes = y_footer - 2.5*cm
    c.rect(1*cm, y_notes, width - 2*cm, 2*cm)
    c.line(14*cm, y_notes, 14*cm, y_notes + 2*cm)

    c.setFont("Helvetica-Bold", 9)
    c.drawString(1.2*cm, y_notes + 1.5*cm, "Note:")
    c.setFont("Helvetica", 8)
    c.drawString(1.2*cm, y_notes + 1.0*cm, "● THANK YOU FOR YOUR BUSINESS.")
    c.drawString(1.2*cm, y_notes + 0.5*cm, "● SUBJECT TO PRAYAGRAJ JURISDICTION ONLY")

    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(17*cm, y_notes + 1.5*cm, "For Berrify & Associates")
    c.line(14.5*cm, y_notes + 0.5*cm, 19.5*cm, y_notes + 0.5*cm)
    c.setFont("Helvetica", 8)
    c.drawCentredString(17*cm, y_notes + 0.2*cm, "(Authorized Signatory)")

    c.save()
    return filepath

if __name__ == '__main__':
    # Test Generation
    test_client = {"ClientName": "Rajesh Kumar", "PAN": "ABCDE1234F", "GSTIN": "27ABCDE1234F1Z5", "Mobile": "9876543210", "Email": "test@test.com", "Address": "Mumbai"}
    test_inv = {"InvoiceNo": "PAR/26-27/001", "InvoiceDate": "01-04-2026", "DueDate": "15-04-2026", "TotalAmount": 11800, "IGST": 1800, "CGST": 0, "SGST": 0}
    test_items = [{"ServiceDescription": "Legal Advisory", "SAC": "998211", "Amount": 10000, "TotalAmount": 11800}]

    print("Generated GST PDF:", generate_gst_invoice(test_inv, test_client, test_items))

    test_inv_norm = {"InvoiceNo": "ITR/26-27/001", "InvoiceDate": "01-04-2026", "DueDate": "15-04-2026", "TotalAmount": 5000}
    print("Generated Normal PDF:", generate_normal_invoice(test_inv_norm, test_client, test_items))
