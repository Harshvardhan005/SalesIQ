import os

class Config:
    DEBUG = os.getenv("DEBUG", "False").lower() in ["true", "1", "t"]
    PORT = int(os.getenv("PORT", 5000))
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), os.getenv("DATABASE_URI", "salesiq.db"))
    SECRET_KEY = os.getenv("SECRET_KEY", "salesiq_prod_secure_secret_key_2026")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max payload limit
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
