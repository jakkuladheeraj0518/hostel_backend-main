from datetime import datetime


class RefundService:

    @staticmethod
    def calculate_refund(check_in: datetime, amount_paid: float) -> float:
        """
        Refund rules:
        - >7 days before check-in → 100%
        - 3–7 days → 50%
        - 0–2 days → 0%
        - After check-in → 0%
        """
        now = datetime.utcnow()
        days_left = (check_in - now).days

        if days_left > 7:
            return amount_paid
        elif 3 <= days_left <= 7:
            return amount_paid * 0.5
        elif 0 <= days_left <= 2:
            return 0.0
        else:
            return 0.0
