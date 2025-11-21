def generate_confirmation_pdf(payment):
    html = f"""
    <!DOCTYPE html>
    <html>
    <body>
      <h2>Booking Payment Confirmation</h2>
      <p>Payment Reference: {payment.payment_reference}</p>
      <p>Amount: {payment.amount} {payment.currency}</p>
      <p>Payment Method: {payment.payment_method}</p>
      <p>Status: {payment.status}</p>
    </body>
    </html>
    """
    return html
