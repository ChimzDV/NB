import os

class Config:
    SECRET_KEY = "novabridge_secret_key"

    SQLALCHEMY_DATABASE_URI = (
    "mysql+pymysql://root:chimwemwe%402026@localhost/novabridge_db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = "app/static/uploads"

    # Flask-Mail Configurations
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "True").lower() in ["true", "on", "1"]
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "notifications@novabridge.com")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "mock_password")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", ("NovaBridge Notifications", "notifications@novabridge.com"))