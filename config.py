import os

class Config:
    DEBUG = os.getenv("DEBUG", "True").lower() in ["true", "1", "t"]
    PORT = int(os.getenv("PORT", 5000))
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), os.getenv("DATABASE_URI", "salesiq.db"))
    SECRET_KEY = os.getenv("SECRET_KEY", "salesiq_default_secret_key_2026")
