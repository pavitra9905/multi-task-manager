import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


def _db_url():
    url = os.getenv("DATABASE_URL", "")
    # Some hosts give "postgres://", SQLAlchemy needs "postgresql://"
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    SQLALCHEMY_DATABASE_URI = _db_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Neon sleeps when idle and drops old connections; this checks before use
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    FRONTEND_ORIGINS = [
        o.strip()
        for o in os.getenv("FRONTEND_ORIGINS", "http://localhost:5173").split(",")
        if o.strip()
    ]

    # Rate limits (can be changed with environment variables)
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
    LOGIN_RATE_LIMIT = os.getenv("LOGIN_RATE_LIMIT", "5 per minute")
    LOGIN_EMAIL_RATE_LIMIT = os.getenv("LOGIN_EMAIL_RATE_LIMIT", "10 per 15 minutes")
    REGISTER_RATE_LIMIT = os.getenv("REGISTER_RATE_LIMIT", "10 per hour")