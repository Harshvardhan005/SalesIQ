"""
SalesIQ — Dashboard Blueprint
Returns aggregated stats for the dashboard overview.
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from database_service import DatabaseService

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api")


def api_response(success=True, data=None, message="", status_code=200):
    return jsonify({"success": success, "message": message, "data": data}), status_code


@dashboard_bp.route("/dashboard-stats", methods=["GET"])
@jwt_required()
def get_stats():
    try:
        stats = DatabaseService.get_dashboard_stats()
        return api_response(True, stats, "Dashboard stats retrieved successfully")
    except Exception as e:
        return api_response(False, None, f"Failed to fetch stats: {str(e)}", 500)
