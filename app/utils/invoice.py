import os
import datetime
import random
from reportlab.pdfgen import canvas

INVOICE_DIR = os.path.join(os.getcwd(), "invoices")
os.makedirs(INVOICE_DIR, exist_ok=True)


def generate_booking_reference() -> str:
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    random_str = str(random.randint(1000, 9999))
    return f"BK-{date_str}-{random_str}"


def generate_invoice(file_path: str, booking_ref: str, amount: float, user_name: str):
    c = canvas.Canvas(file_path)
    c.drawString(100, 750, f"Invoice for Booking: {booking_ref}")
    c.drawString(100, 730, f"Name: {user_name}")
    c.drawString(100, 710, f"Amount Paid: ₹{amount}")
    c.save()
    return file_path


def send_email_simulation(to_email: str, booking_ref: str, amount: float):
    # Simulated email send (replace with real integration later)
    print(f"[EMAIL] Sent to {to_email}: Booking {booking_ref}, Amount ₹{amount}")


def send_sms_simulation(phone: str, booking_ref: str, amount: float):
    # Simulated SMS send (replace with real integration later)
    print(f"[SMS] Sent to {phone}: Booking {booking_ref}, Amount ₹{amount}")
