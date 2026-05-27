from app import db

class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    message = db.Column(db.Text)

    notification_date = db.Column(db.Date)

    status = db.Column(db.String(20), default="unread")

    created_at = db.Column(db.DateTime)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)