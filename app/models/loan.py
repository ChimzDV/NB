from app import db

class Loan(db.Model):
    __tablename__ = "loans"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    loan_amount = db.Column(db.Numeric(10, 2), nullable=False)
    purpose = db.Column(db.String(255))
    interest_rate = db.Column(db.Numeric(5, 2), default=0)

    total_amount = db.Column(db.Numeric(10, 2))
    remaining_balance = db.Column(db.Numeric(10, 2))

    status = db.Column(db.String(20), default="pending")

    start_date = db.Column(db.Date)
    due_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)