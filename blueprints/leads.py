"""
SalesIQ — Leads Blueprint
Handles CRUD and pipeline stage operations for saved leads.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from database_service import DatabaseService
from schemas.schemas import LeadSchema, PipelineStageSchema, validate_schema

leads_bp = Blueprint("leads", __name__, url_prefix="/api")


def api_response(success=True, data=None, message="", status_code=200):
    return jsonify({"success": success, "message": message, "data": data}), status_code


@leads_bp.route("/leads", methods=["GET"])
@jwt_required()
def get_leads():
    try:
        leads = DatabaseService.get_all_leads()
        return api_response(True, leads, "Leads retrieved successfully")
    except Exception as e:
        return api_response(False, None, f"Failed to fetch leads: {str(e)}", 500)


@leads_bp.route("/save-lead", methods=["POST"])
@jwt_required()
def save_lead():
    payload = request.get_json() or {}
    data, errors = validate_schema(LeadSchema, payload)
    if errors:
        return api_response(False, errors, "Validation failed", 400)
    try:
        lead_id = DatabaseService.create_lead(data)
        return api_response(True, {"id": lead_id}, "Lead saved successfully", 201)
    except Exception as e:
        return api_response(False, None, f"Database error: {str(e)}", 500)


@leads_bp.route("/leads/<int:lead_id>", methods=["DELETE"])
@jwt_required()
def delete_lead(lead_id):
    try:
        deleted = DatabaseService.delete_lead(lead_id)
        if deleted:
            return api_response(True, None, f"Lead #{lead_id} deleted successfully")
        return api_response(False, None, f"Lead #{lead_id} not found", 404)
    except Exception as e:
        return api_response(False, None, f"Failed to delete lead: {str(e)}", 500)


@leads_bp.route("/leads/<int:lead_id>/stage", methods=["PATCH"])
@jwt_required()
def update_lead_stage(lead_id):
    """Update the Kanban pipeline stage for a lead."""
    payload = request.get_json() or {}
    data, errors = validate_schema(PipelineStageSchema, payload)
    if errors:
        return api_response(False, errors, "Validation failed", 400)
    try:
        updated = DatabaseService.update_lead_stage(lead_id, data["stage"])
        if not updated:
            return api_response(False, None, f"Lead #{lead_id} not found", 404)
        return api_response(True, updated, "Pipeline stage updated successfully")
    except ValueError as ve:
        return api_response(False, None, str(ve), 400)
    except Exception as e:
        return api_response(False, None, f"Failed to update stage: {str(e)}", 500)
