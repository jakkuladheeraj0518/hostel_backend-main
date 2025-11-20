# app/core/razorpay_client.py
import razorpay
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(
    os.getenv("RAZORPAY_KEY_ID"),
    os.getenv("RAZORPAY_KEY_SECRET")
))
