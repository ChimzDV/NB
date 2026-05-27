from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import os

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

def create_app():

    app = Flask(__name__)

    app.config.from_object("app.config.Config")

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from app.routes.main_routes import main
    app.register_blueprint(main)

    from app.models.user import User
    from app.models.loan import Loan
    from app.models.document import Document
    from app.models.payment import Payment
    from app.models.notification import Notification
    from app.routes.auth_routes import auth
    app.register_blueprint(auth)
    
    from app.routes.admin_routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix="/admin")
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Background Scheduler setup
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        from apscheduler.schedulers.background import BackgroundScheduler
        from app.services.reminder_service import check_and_send_reminders
        
        scheduler = BackgroundScheduler()
        # Schedule the scan to run daily
        scheduler.add_job(func=check_and_send_reminders, trigger="interval", days=1, id="reminder_job")
        scheduler.start()
        print("APScheduler reminder background job started successfully.")

    return app