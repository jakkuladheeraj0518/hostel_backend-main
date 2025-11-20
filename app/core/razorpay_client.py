import razorpay
from app.config import settings


print("🔍 Loaded Razorpay Key ID:", settings.RAZORPAY_KEY_ID)
print("🔍 Loaded Razorpay Secret:", settings.RAZORPAY_KEY_SECRET)

# Initialize Razorpay client using Pydantic Settings
razorpay_client = razorpay.Client(auth=(
    settings.RAZORPAY_KEY_ID,
    settings.RAZORPAY_KEY_SECRET
))
