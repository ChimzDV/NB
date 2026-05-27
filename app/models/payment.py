from app import db

class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)

    loan_id = db.Column(db.Integer, db.ForeignKey("loans.id"))

    amount_paid = db.Column(db.Numeric(10, 2), nullable=False)

    payment_date = db.Column(db.DateTime)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)