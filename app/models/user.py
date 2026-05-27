from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))

    password = db.Column(db.String(255), nullable=False)

    national_id = db.Column(db.String(50))

    account_status = db.Column(db.String(20), default="active")

    created_at = db.Column(db.DateTime)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @property
    def kyc_status(self):
        from app.models.document import Document
        docs = Document.query.filter_by(user_id=self.id).all()
        national_id_approved = any(d.document_type == "National ID" and d.verification_status == "approved" for d in docs)
        payslip_approved = any(d.document_type == "Payslip" and d.verification_status == "approved" for d in docs)
        any_rejected = any(d.verification_status == "rejected" for d in docs)
        
        if national_id_approved and payslip_approved:
            return "Verified"
        elif any_rejected:
            return "Rejected Documents"
        else:
            return "Pending Verification"