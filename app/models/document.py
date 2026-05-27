from app import db

class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    document_type = db.Column(db.String(50))
    file_name = db.Column(db.String(255))
    file_path = db.Column(db.String(255))

    uploaded_at = db.Column(db.DateTime)

    verification_status = db.Column(db.String(20), default="pending")
    verified_at = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)