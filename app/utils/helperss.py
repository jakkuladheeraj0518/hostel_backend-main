import hmac, hashlib, uuid
from datetime import datetime
from app.config import settings

def generate_order_id():
    return f"ORD_{datetime.utcnow().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8].upper()}"

def verify_razorpay_signature(order_id: str, payment_id: str, signature: str) -> bool:
    message = f"{order_id}|{payment_id}"
    generated_signature = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(generated_signature, signature)

def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    expected = hmac.new(
        settings.RAZORPAY_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
