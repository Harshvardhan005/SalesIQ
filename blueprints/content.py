"""
SalesIQ — Content Generation Blueprint
Handles AI-powered sales copy generation.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import limiter
from database_service import DatabaseService
from groq_service import GroqService
from schemas.schemas import ContentGenerationSchema, validate_schema

content_bp = Blueprint("content", __name__, url_prefix="/api")


def api_response(success=True, data=None, message="", status_code=200):
    return jsonify({"success": success, "message": message, "data": data}), status_code


@content_bp.route("/generate-content", methods=["POST"])
@jwt_required()
@limiter.limit("30 per hour")
def generate_content():
    payload = request.get_json() or {}
    data, errors = validate_schema(ContentGenerationSchema, payload)
    if errors:
        return api_response(False, errors, "Validation failed", 400)

    company_name = data["company_name"]
    content_type = data["content_type"]
    tone = data["tone"]
    length = data["length"]
    prompt = data.get("prompt", "")

    try:
        company_info = DatabaseService.get_report_by_company_name(company_name)
        if not company_info:
            return api_response(
                False, None,
                f"No analyzed profile found for company '{company_name}'. Please run company research first.",
                404,
            )

        output_text = GroqService.generate_sales_content(
            company_info=company_info,
            content_type=content_type,
            tone=tone,
            length=length,
            custom_prompt=prompt,
        )

        content_id = DatabaseService.save_generated_content(company_name, content_type, prompt, output_text)

        return api_response(
            True,
            {
                "id": content_id,
                "company_name": company_name,
                "content_type": content_type,
                "tone": tone,
                "length": length,
                "prompt": prompt,
                "output_text": output_text,
            },
            "Content generated successfully",
            201,
        )

    except ValueError as ve:
        return api_response(False, None, str(ve), 400)
    except RuntimeError as re:
        return api_response(False, None, str(re), 500)
    except Exception as e:
        return api_response(False, None, f"Failed to generate content: {str(e)}", 500)
