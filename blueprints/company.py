"""
SalesIQ — Company Analysis Blueprint
Handles the main AI-powered company analysis endpoint.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import limiter
from database_service import DatabaseService
from groq_service import GroqService
from scrape_service import ScrapeService
from schemas.schemas import CompanyAnalysisSchema, validate_schema

company_bp = Blueprint("company", __name__, url_prefix="/api")


def api_response(success=True, data=None, message="", status_code=200):
    return jsonify({"success": success, "message": message, "data": data}), status_code


@company_bp.route("/analyze-company", methods=["POST"])
@jwt_required()
@limiter.limit("20 per hour")
def analyze_company():
    payload = request.get_json() or {}
    data, errors = validate_schema(CompanyAnalysisSchema, payload)
    if errors:
        return api_response(False, errors, "Validation failed", 400)

    company_name = data["company_name"]
    website = data["website"]
    industry = data["industry"]
    product_offered = data.get("product_offered", "")
    target_customer = data.get("target_customer", "")
    notes = data.get("notes", "")
    manual_company_info = data.get("manual_company_info", "")

    # Scraping Logic
    scraped_content = ""
    information_source = "Website"

    if manual_company_info:
        scraped_content = manual_company_info
        information_source = "User Input"
    else:
        scrape_result = ScrapeService.scrape_website(website)
        if scrape_result and scrape_result.get("success"):
            scraped_content = scrape_result.get("text", "")
            information_source = "Website"
        else:
            error_msg = scrape_result.get("error", "Unknown error") if scrape_result else "Invalid URL"
            return api_response(
                False,
                {"requires_manual_input": True, "error": error_msg},
                f"Web scraping failed: {error_msg}. Please provide manual company information.",
                422,
            )

    try:
        report_data = GroqService.analyze_company(
            company_name=company_name,
            website=website,
            industry=industry,
            product_offered=product_offered,
            target_customer=target_customer,
            notes=notes,
            scraped_content=scraped_content,
            information_source=information_source,
        )

        email_script = (
            f"Subject: Value Proposition outreach for {company_name}\n\n"
            f"Hi team,\n\n"
            f"Here is a personalized outbound outreach strategy for {company_name}:\n\n"
            f"{report_data.get('sales_strategy', '')}\n\n"
            f"Value Proposition Hook:\n"
            f"Focus on solving key pain point: {report_data.get('pain_points', ['Outbound efficiency'])[0]}\n\n"
            f"Best,\nSales Team"
        )
        linkedin_script = (
            f"Hi, saw your growth at {company_name}.\n\n"
            f"Let's connect regarding your business goals: {', '.join(report_data.get('business_goals', []))}.\n\n"
            f"Best regards!"
        )

        db_payload = {
            "company_name": company_name,
            "website": website,
            "industry": report_data.get("industry", industry),
            "product_offered": product_offered,
            "target_customer": target_customer,
            "notes": notes,
            "lead_score": report_data.get("lead_score", 90),
            "pain_points": report_data.get("pain_points", []),
            "company_overview": report_data.get("company_overview", ""),
            "products": report_data.get("products", []),
            "business_goals": report_data.get("business_goals", []),
            "growth_opportunities": report_data.get("growth_opportunities", []),
            "sales_strategy": report_data.get("sales_strategy", ""),
            "confidence": report_data.get("confidence", "High"),
            "email_script": email_script,
            "linkedin_script": linkedin_script,
            "information_source": information_source,
        }

        report_id = DatabaseService.create_report(db_payload)

        DatabaseService.create_lead({
            "company_name": company_name,
            "website": website,
            "industry": report_data.get("industry", industry),
            "lead_score": report_data.get("lead_score", 90),
            "status": "High Fit" if report_data.get("lead_score", 90) >= 90 else "Medium Fit",
            "notes": notes,
            "pipeline_stage": "New",
        })

        db_payload["id"] = report_id
        return api_response(True, db_payload, "Company analysis generated successfully", 201)

    except ValueError as ve:
        return api_response(False, None, str(ve), 400)
    except RuntimeError as re:
        return api_response(False, None, str(re), 500)
    except Exception as e:
        return api_response(False, None, f"Failed to generate analysis: {str(e)}", 500)
