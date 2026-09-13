"""
SalesIQ — Centralized Flask Extension Instances
All extensions are initialized here and registered in create_app() to avoid circular imports.
"""
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS

# JWT — stateless token-based authentication
jwt = JWTManager()

# Limiter — rate limiting (keyed by client IP)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per minute"],
    storage_uri="memory://",
)

# CORS — cross-origin resource sharing
cors = CORS()
