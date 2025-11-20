from app.models.subscription import Payment
from app.models.payment_models import Customer
from app.models.hostel import Hostel

class RazorpayRepository:

    @staticmethod
    def get_user_by_id(db, user_id: int):
        return db.query(Customer).filter(Customer.id == user_id).first()

    @staticmethod
    def get_hostel_by_id(db, hostel_id: int):
        return db.query(Hostel).filter(Hostel.id == hostel_id).first()

    @staticmethod
    def save_payment(db, payment: Payment):
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment
