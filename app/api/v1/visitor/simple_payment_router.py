from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
import os
from datetime import datetime
from typing import Dict, List

from app.utils.invoice import (
    INVOICE_DIR,
    generate_booking_reference,
    generate_invoice,
    send_email_simulation,
    send_sms_simulation,
)

router = APIRouter()

# In-memory store for quick testing (not persistent, not thread-safe)
bookings_db: Dict[str, List[Dict]] = {}


@router.post("/confirm")
async def confirm_payment(user_email: str, phone: str, amount: float, background_tasks: BackgroundTasks):
    booking_ref = generate_booking_reference()
    invoice_path = os.path.join(INVOICE_DIR, f"{booking_ref}.pdf")

    # Generate invoice PDF
    generate_invoice(invoice_path, booking_ref, amount, user_email)

    # Schedule simulated email and SMS
    background_tasks.add_task(send_email_simulation, user_email, booking_ref, amount)
    background_tasks.add_task(send_sms_simulation, phone, booking_ref, amount)

    # Store booking in-memory
    booking_data = {
        "booking_ref": booking_ref,
        "user_email": user_email,
        "phone": phone,
        "amount": amount,
        "status": "confirmed",
        "invoice_path": invoice_path,
        "timestamp": datetime.utcnow(),
    }
    bookings_db.setdefault(user_email, []).append(booking_data)

    return {
        "booking_reference": booking_ref,
        "amount": amount,
        "status": "confirmed",
        "invoice_path": invoice_path,
    }


@router.get("/history/{user_email}")
async def get_booking_history(user_email: str):
    history = bookings_db.get(user_email)
    if not history:
        raise HTTPException(status_code=404, detail="No bookings found for this user")
    return [
        {
            "booking_ref": b["booking_ref"],
            "amount": b["amount"],
            "status": b["status"],
            "timestamp": b["timestamp"].strftime("%Y-%m-%d %H:%M"),
        }
        for b in history
    ]


@router.get("/transactions/{booking_ref}")
async def get_transaction(booking_ref: str):
    for user_bookings in bookings_db.values():
        for b in user_bookings:
            if b["booking_ref"] == booking_ref:
                return b
    raise HTTPException(status_code=404, detail="Transaction not found")


@router.get("/invoice/{booking_ref}")
async def download_invoice(booking_ref: str):
    # Find invoice path in in-memory store
    for user_bookings in bookings_db.values():
        for b in user_bookings:
            if b["booking_ref"] == booking_ref:
                invoice_path = b["invoice_path"]
                if not os.path.isfile(invoice_path):
                    raise HTTPException(status_code=404, detail="Invoice not found")
                return FileResponse(invoice_path, media_type="application/pdf", filename=f"{booking_ref}.pdf")
    raise HTTPException(status_code=404, detail="Invoice not found")
