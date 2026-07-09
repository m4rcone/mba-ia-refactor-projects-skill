import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///tasks.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))


class MailConfig:
    HOST = os.environ.get("MAIL_HOST", "smtp.gmail.com")
    PORT = int(os.environ.get("MAIL_PORT", "587"))
    USER = os.environ.get("MAIL_USER", "")
    PASSWORD = os.environ.get("MAIL_PASSWORD", "")
