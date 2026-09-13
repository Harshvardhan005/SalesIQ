import os
from datetime import timedelta

class Config:
    # ── Core ──────────────────────────────────────────────────────────────────
    DEBUG = os.getenv("DEBUG", "False").lower() in ["true", "1", "t"]
    PORT = int(os.getenv("PORT", 5000))
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), os.getenv("DATABASE_URI", "salesiq.db"))
    SECRET_KEY = os.getenv("SECRET_KEY", "salesiq_prod_secure_secret_key_2026_change_me")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max payload

    # ── Session / Cookie Security ─────────────────────────────────────────────
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # ── JWT Configuration ─────────────────────────────────────────────────────
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "salesiq_jwt_secret_change_me"))
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    # ── CORS ──────────────────────────────────────────────────────────────────
    # Comma-separated list of allowed origins; defaults to wildcard for local dev
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

    # ── Rate Limiting ─────────────────────────────────────────────────────────
    RATELIMIT_DEFAULT = "200 per minute"
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URL", "memory://")
