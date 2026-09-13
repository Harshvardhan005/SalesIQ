"""
SalesIQ — Reports Blueprint
Handles CRUD operations for company analysis reports.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import limiter
from database_service import DatabaseService

reports_bp = Blueprint("reports", __name__, url_prefix="/api")


def api_response(success=True, data=None, message="", status_code=200):
    return jsonify({"success": success, "message": message, "data": data}), status_code


@reports_bp.route("/reports", methods=["GET"])
@jwt_required()
def get_reports():
    try:
        reports = DatabaseService.get_all_reports()
        return api_response(True, reports, "Reports retrieved successfully")
    except Exception as e:
        return api_response(False, None, f"Failed to fetch reports: {str(e)}", 500)


@reports_bp.route("/reports/<int:report_id>", methods=["GET"])
@jwt_required()
def get_report(report_id):
    try:
        report = DatabaseService.get_report_by_id(report_id)
        if not report:
            return api_response(False, None, f"Report #{report_id} not found", 404)
        return api_response(True, report, "Report retrieved successfully")
    except Exception as e:
        return api_response(False, None, f"Failed to fetch report: {str(e)}", 500)


@reports_bp.route("/save-report", methods=["POST"])
@jwt_required()
def save_report():
    payload = request.get_json() or {}
    if not payload.get("company_name") or not payload.get("website"):
        return api_response(False, None, "Missing company_name or website fields", 400)
    try:
        report_id = DatabaseService.create_report(payload)
        return api_response(True, {"id": report_id}, "Report saved successfully", 201)
    except Exception as e:
        return api_response(False, None, f"Database error: {str(e)}", 500)


@reports_bp.route("/reports/<int:report_id>", methods=["DELETE"])
@jwt_required()
def delete_report(report_id):
    try:
        deleted = DatabaseService.delete_report(report_id)
        if deleted:
            return api_response(True, None, f"Report #{report_id} deleted successfully")
        return api_response(False, None, f"Report #{report_id} not found", 404)
    except Exception as e:
        return api_response(False, None, f"Failed to delete report: {str(e)}", 500)
