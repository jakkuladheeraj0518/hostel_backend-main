# app/utils/receipt_generator.py
import io, os, json
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from datetime import datetime

def generate_qr_code(data: str) -> io.BytesIO:
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

def generate_receipt_pdf(receipt, invoice, transaction) -> str:
    os.makedirs("receipts", exist_ok=True)
    filename = f"receipts/receipt_{receipt.receipt_number}.pdf"
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=18)
    elements.append(Paragraph("PAYMENT RECEIPT", title_style))
    elements.append(Spacer(1, 12))

    # Basic info table
    info = [
        ["Receipt No:", receipt.receipt_number],
        ["Date:", receipt.generated_at.strftime("%Y-%m-%d %H:%M:%S")],
        ["Invoice No:", invoice.invoice_number],
        ["Transaction ID:", transaction.transaction_id],
    ]
    table = Table(info, colWidths=[120, 360])
    table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Items (if any)
    items = []
    try:
        items = json.loads(invoice.items) if invoice.items else []
    except Exception:
        items = []

    if items:
        rows = [["Description", "Qty", "Unit", "Amount"]]
        for it in items:
            rows.append([it.get("description",""), str(it.get("quantity",1)), f"₹{it.get('unit_price',0):.2f}", f"₹{it.get('amount',0):.2f}"])
        rows.append(["", "", "Total:", f"₹{invoice.total_amount:.2f}"])
        rows.append(["", "", "Paid:", f"₹{receipt.amount:.2f}"])
        rows.append(["", "", "Remaining:", f"₹{invoice.due_amount:.2f}"])
        t = Table(rows, colWidths=[260, 60, 80, 80])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a73e8')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (2,1), (-1,-1), 'RIGHT'),
            ('GRID', (0,0), (-1,-1), 0.3, colors.grey),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 12))

    # QR
    qr_buf = generate_qr_code(receipt.qr_code_data or f"R:{receipt.receipt_number}|A:{receipt.amount}")
    img = Image(qr_buf, width=1.5*inch, height=1.5*inch)
    img.hAlign = 'CENTER'
    elements.append(img)
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("Scan QR code to verify", styles['Normal']))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("This is a computer-generated receipt.", styles['Normal']))

    doc.build(elements)

    with open(filename, "wb") as f:
        f.write(buffer.getvalue())

    return filename
