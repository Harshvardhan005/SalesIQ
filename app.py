"""
SalesIQ — Application Factory
Wires together Flask extensions, blueprints, error handlers, and static file serving.
"""
import os
from dotenv import load_dotenv

# Load .env before anything else so Config can read env vars
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from flask import Flask, jsonify, send_from_directory
from config import Config
from extensions import jwt, limiter, cors
from database import init_db
from logger import configure_logging, register_request_logging


def create_app(config_class=Config):
    """Application factory — create and configure the Flask app."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ── Logging ──────────────────────────────────────────────────────────────
    configure_logging(debug=config_class.DEBUG)
    register_request_logging(app)

    # ── Extensions ───────────────────────────────────────────────────────────
    jwt.init_app(app)
    limiter.init_app(app)
    cors.init_app(
        app,
        resources={r"/*": {"origins": config_class.ALLOWED_ORIGINS}},
        supports_credentials=True,
    )

    # ── Database ─────────────────────────────────────────────────────────────
    with app.app_context():
        init_db()

    # ── Blueprints ───────────────────────────────────────────────────────────
    from blueprints.auth import auth_bp
    from blueprints.company import company_bp
    from blueprints.content import content_bp
    from blueprints.dashboard import dashboard_bp
    from blueprints.leads import leads_bp
    from blueprints.reports import reports_bp
    from blueprints.health import health_bp

    for bp in (auth_bp, company_bp, content_bp, dashboard_bp, leads_bp, reports_bp, health_bp):
        app.register_blueprint(bp)

    # ── Search-status helper (no auth required) ───────────────────────────────
    @app.route("/api/search-status", methods=["GET"])
    def search_status():
        providers = {
            "tavily":     bool(os.getenv("TAVILY_API_KEY", "").strip()),
            "serper":     bool(os.getenv("SERPER_API_KEY", "").strip()),
            "google_cse": bool(
                os.getenv("GOOGLE_CSE_API_KEY", "").strip()
                and os.getenv("GOOGLE_CSE_ID", "").strip()
            ),
            "bing": bool(os.getenv("BING_SEARCH_API_KEY", "").strip()),
        }
        return jsonify({
            "success": True,
            "message": "Search provider status",
            "data": {"providers": providers, "any_enabled": any(providers.values())},
        })

    # ── Static file serving ───────────────────────────────────────────────────
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    @app.route("/", methods=["GET"])
    def index():
        return send_from_directory(BASE_DIR, "login.html")

    @app.route("/login", methods=["GET"])
    def login_page():
        return send_from_directory(BASE_DIR, "login.html")

    @app.route("/dashboard", methods=["GET"])
    def dashboard_page():
        return send_from_directory(BASE_DIR, "index.html")

    @app.route("/<path:filename>", methods=["GET"])
    def static_files(filename):
        return send_from_directory(BASE_DIR, filename)

    # ── Security Headers ──────────────────────────────────────────────────────
    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response

    # ── JWT Error Handlers ────────────────────────────────────────────────────
    @jwt.unauthorized_loader
    def unauthorized_callback(reason):
        return jsonify({"success": False, "message": f"Unauthorized: {reason}", "data": None}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"success": False, "message": "Token has expired. Please log in again.", "data": None}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return jsonify({"success": False, "message": f"Invalid token: {reason}", "data": None}), 422

    # ── Generic Error Handlers ────────────────────────────────────────────────
    def api_response(success, message, status_code):
        return jsonify({"success": success, "message": message, "data": None}), status_code

    @app.errorhandler(400)
    def bad_request(e):
        return api_response(False, str(e.description or "Bad request"), 400)

    @app.errorhandler(404)
    def not_found(e):
        return api_response(False, "Resource or endpoint not found", 404)

    @app.errorhandler(413)
    def payload_too_large(e):
        return api_response(False, "Payload size exceeds maximum allowed limit (5 MB).", 413)

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return api_response(False, "Rate limit exceeded. Please slow down.", 429)

    @app.errorhandler(500)
    def server_error(e):
        return api_response(False, "Internal server error occurred", 500)

    return app


# ── Entry point ───────────────────────────────────────────────────────────────
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)
