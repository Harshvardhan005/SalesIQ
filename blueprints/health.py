"""
SalesIQ — Health Check Blueprint
Returns system status: DB connectivity, Groq key presence, timestamp.
"""
import os
from datetime import datetime, timezone
from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__, url_prefix="/api")


@health_bp.route("/health", methods=["GET"])
def health():
    """Public health-check endpoint — no auth required."""
    # Verify DB is reachable
    db_ok = False
    try:
        from database_service import DatabaseService
        DatabaseService.get_dashboard_stats()
        db_ok = True
    except Exception:
        db_ok = False

    groq_key_present = bool(os.getenv("GROQ_API_KEY", "").strip())

    status = "ok" if (db_ok and groq_key_present) else "degraded"

    return jsonify({
        "success": True,
        "message": f"SalesIQ is {status}",
        "data": {
            "status": status,
            "db": db_ok,
            "groq_key": groq_key_present,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }), 200
