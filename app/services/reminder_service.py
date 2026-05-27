from app.models.notification import Notification
from app.models.loan import Loan
from app.models.user import User
from app import db
import datetime
from app.services.email_service import send_loan_due_tomorrow_email, send_loan_overdue_email

def check_and_send_reminders():
    """Daily background job to detect due-tomorrow and overdue loans."""
    # Build a separate app context since this runs in a background thread
    from app import create_app
    app = create_app()
    with app.app_context():
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        
        print(f"[Reminder Service] Starting scanning run. Today: {today}, Tomorrow: {tomorrow}")
        
        # 1. Process due tomorrow
        due_tomorrow_loans = Loan.query.filter(Loan.due_date == tomorrow, Loan.status == "approved").all()
        for loan in due_tomorrow_loans:
            user = User.query.get(loan.user_id)
            if not user:
                continue
            
            msg = f"Your loan payment for loan #{loan.id} is due tomorrow."
            # Prevent duplicate creation
            existing = Notification.query.filter_by(user_id=user.id, message=msg).first()
            if not existing:
                notification = Notification(
                    user_id=user.id,
                    message=msg,
                    notification_date=today,
                    status="unread"
                )
                db.session.add(notification)
                send_loan_due_tomorrow_email(user, loan)
                print(f"[Reminder Service] Created due-tomorrow notification for User #{user.id}")
        
        # 2. Process overdue accounts
        # Checks approved loans that have passed their due date
        overdue_loans = Loan.query.filter(Loan.due_date < today, Loan.status == "approved").all()
        for loan in overdue_loans:
            user = User.query.get(loan.user_id)
            if not user:
                continue
            
            loan.status = "overdue"
            msg = f"Your loan #{loan.id} is overdue."
            notification = Notification(
                user_id=user.id,
                message=msg,
                notification_date=today,
                status="unread"
            )
            db.session.add(notification)
            send_loan_overdue_email(user, loan)
            print(f"[Reminder Service] Flagged Loan #{loan.id} as overdue for User #{user.id}")
            
        db.session.commit()
        print("[Reminder Service] Scanning run completed.")
