import random
import os
import bcrypt
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from database import init_db
from database_service import DatabaseService
from groq_service import GroqService
from scrape_service import ScrapeService

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for cross-origin frontend communication
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize SQLite database schema
init_db()

# Custom Standard API Response Helper
def api_response(success=True, data=None, message="", status_code=200):
    return jsonify({
        "success": success,
        "message": message,
        "data": data
    }), status_code

# Error Handlers
@app.errorhandler(400)
def bad_request(e):
    return api_response(success=False, message=str(e.description or "Bad request"), status_code=400)

@app.errorhandler(404)
def not_found(e):
    return api_response(success=False, message="Resource or endpoint not found", status_code=404)

@app.errorhandler(500)
def server_error(e):
    return api_response(success=False, message="Internal server error occurred", status_code=500)

# Routes

@app.route("/", methods=["GET"])
def index():
    return api_response(success=True, message="SalesIQ Backend API Service is operational", data={"version": "1.0.0"})

@app.route("/api/dashboard-stats", methods=["GET"])
def get_stats():
    try:
        stats = DatabaseService.get_dashboard_stats()
        return api_response(success=True, data=stats, message="Dashboard stats retrieved successfully")
    except Exception as e:
        return api_response(success=False, message=f"Failed to fetch stats: {str(e)}", status_code=500)

@app.route("/api/analyze-company", methods=["POST"])
def analyze_company():
    payload = request.get_json() or {}

    # Inputs Validation
    company_name = payload.get("company_name", "").strip()
    website = payload.get("website", "").strip()
    industry = payload.get("industry", "").strip()
    product_offered = payload.get("product_offered", "").strip()
    target_customer = payload.get("target_customer", "").strip()
    notes = payload.get("notes", "").strip()
    manual_company_info = payload.get("manual_company_info", "").strip()

    if not company_name:
        return api_response(success=False, message="Company name is required", status_code=400)
    if not website:
        return api_response(success=False, message="Website URL is required", status_code=400)
    if not industry:
        return api_response(success=False, message="Industry is required", status_code=400)

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
                success=False, 
                message=f"Web scraping failed: {error_msg}. Please provide manual company information.", 
                status_code=422,
                data={"requires_manual_input": True, "error": error_msg}
            )

    try:
        # Call Groq AI Service
        report_data = GroqService.analyze_company(
            company_name=company_name,
            website=website,
            industry=industry,
            product_offered=product_offered,
            target_customer=target_customer,
            notes=notes,
            scraped_content=scraped_content,
            information_source=information_source
        )

        # Build fallback email and linkedin scripts based on sales strategy insights
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

        # Format complete payload for database insertion
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
            "information_source": information_source
        }

        report_id = DatabaseService.create_report(db_payload)

        # Also auto-create a saved lead account in CRM
        DatabaseService.create_lead({
            "company_name": company_name,
            "website": website,
            "industry": report_data.get("industry", industry),
            "lead_score": report_data.get("lead_score", 90),
            "status": "High Fit" if report_data.get("lead_score", 90) >= 90 else "Medium Fit",
            "notes": notes
        })

        db_payload["id"] = report_id
        return api_response(success=True, data=db_payload, message="Company analysis generated successfully", status_code=201)

    except ValueError as ve:
        # Invalid inputs or missing key errors
        return api_response(success=False, message=str(ve), status_code=400)
    except RuntimeError as re:
        # Rate limits, timeouts, connection/API errors
        return api_response(success=False, message=str(re), status_code=500)
    except Exception as e:
        return api_response(success=False, message=f"Failed to generate analysis: {str(e)}", status_code=500)

@app.route("/api/generate-content", methods=["POST"])
def generate_content():
    payload = request.get_json() or {}
    company_name = payload.get("company_name", "").strip()
    content_type = payload.get("content_type", "").strip()
    tone = payload.get("tone", "").strip()
    length = payload.get("length", "").strip()
    prompt = payload.get("prompt", "").strip()

    if not company_name:
        return api_response(success=False, message="Company name is required", status_code=400)
    if not content_type:
        return api_response(success=False, message="Content type is required", status_code=400)
    if not tone:
        return api_response(success=False, message="Tone is required", status_code=400)
    if not length:
        return api_response(success=False, message="Length is required", status_code=400)

    # Fetch company report from database
    try:
        company_info = DatabaseService.get_report_by_company_name(company_name)
        if not company_info:
            return api_response(success=False, message=f"No analyzed profile found for company '{company_name}'. Please run company research first.", status_code=404)
        
        # Call Groq AI to generate personalized content
        output_text = GroqService.generate_sales_content(
            company_info=company_info,
            content_type=content_type,
            tone=tone,
            length=length,
            custom_prompt=prompt
        )

        # Save to SQLite database
        content_id = DatabaseService.save_generated_content(company_name, content_type, prompt, output_text)

        return api_response(success=True, data={
            "id": content_id,
            "company_name": company_name,
            "content_type": content_type,
            "tone": tone,
            "length": length,
            "prompt": prompt,
            "output_text": output_text
        }, message="Content generated successfully", status_code=201)

    except ValueError as ve:
        return api_response(success=False, message=str(ve), status_code=400)
    except RuntimeError as re:
        return api_response(success=False, message=str(re), status_code=500)
    except Exception as e:
        return api_response(success=False, message=f"Failed to generate content: {str(e)}", status_code=500)

@app.route("/api/save-report", methods=["POST"])
def save_report():
    payload = request.get_json() or {}
    if not payload.get("company_name") or not payload.get("website"):
        return api_response(success=False, message="Missing company_name or website fields", status_code=400)

    try:
        report_id = DatabaseService.create_report(payload)
        return api_response(success=True, data={"id": report_id}, message="Report saved successfully", status_code=201)
    except Exception as e:
        return api_response(success=False, message=f"Database error: {str(e)}", status_code=500)

@app.route("/api/reports", methods=["GET"])
def get_reports():
    try:
        reports = DatabaseService.get_all_reports()
        return api_response(success=True, data=reports, message="Reports retrieved successfully")
    except Exception as e:
        return api_response(success=False, message=f"Failed to fetch reports: {str(e)}", status_code=500)

@app.route("/api/reports/<int:report_id>", methods=["DELETE"])
def delete_report(report_id):
    try:
        deleted = DatabaseService.delete_report(report_id)
        if deleted:
            return api_response(success=True, message=f"Report #{report_id} deleted successfully")
        return api_response(success=False, message=f"Report #{report_id} not found", status_code=404)
    except Exception as e:
        return api_response(success=False, message=f"Failed to delete report: {str(e)}", status_code=500)

@app.route("/api/save-lead", methods=["POST"])
def save_lead():
    payload = request.get_json() or {}
    company_name = payload.get("company_name", "").strip()
    website = payload.get("website", "").strip()

    if not company_name or not website:
        return api_response(success=False, message="Company name and website are required", status_code=400)

    try:
        lead_id = DatabaseService.create_lead(payload)
        return api_response(success=True, data={"id": lead_id}, message="Lead saved successfully", status_code=201)
    except Exception as e:
        return api_response(success=False, message=f"Database error: {str(e)}", status_code=500)

@app.route("/api/leads", methods=["GET"])
def get_leads():
    try:
        leads = DatabaseService.get_all_leads()
        return api_response(success=True, data=leads, message="Leads retrieved successfully")
    except Exception as e:
        return api_response(success=False, message=f"Failed to fetch leads: {str(e)}", status_code=500)

@app.route("/api/leads/<int:lead_id>", methods=["DELETE"])
def delete_lead(lead_id):
    try:
        deleted = DatabaseService.delete_lead(lead_id)
        if deleted:
            return api_response(success=True, message=f"Lead #{lead_id} deleted successfully")
        return api_response(success=False, message=f"Lead #{lead_id} not found", status_code=404)
    except Exception as e:
        return api_response(success=False, message=f"Failed to delete lead: {str(e)}", status_code=500)

@app.route("/api/auth/register", methods=["POST"])
def register():
    payload = request.get_json() or {}
    name = payload.get("name", "").strip()
    email = payload.get("email", "").strip().lower()
    password = payload.get("password", "").strip()

    if not name:
        return api_response(success=False, message="Name is required", status_code=400)
    if not email or "@" not in email:
        return api_response(success=False, message="A valid email is required", status_code=400)
    if len(password) < 8:
        return api_response(success=False, message="Password must be at least 8 characters", status_code=400)

    try:
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_id = DatabaseService.create_user(name, email, password_hash)
        return api_response(success=True, data={"id": user_id, "name": name, "email": email},
                            message="Account created successfully", status_code=201)
    except ValueError as ve:
        return api_response(success=False, message=str(ve), status_code=409)
    except Exception as e:
        return api_response(success=False, message=f"Registration failed: {str(e)}", status_code=500)


@app.route("/api/auth/login", methods=["POST"])
def login():
    payload = request.get_json() or {}
    email = payload.get("email", "").strip().lower()
    password = payload.get("password", "").strip()

    if not email or not password:
        return api_response(success=False, message="Email and password are required", status_code=400)

    try:
        user = DatabaseService.get_user_by_email(email)
        if not user:
            return api_response(success=False, message="No account found with this email", status_code=404)

        is_valid = bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8'))
        if not is_valid:
            return api_response(success=False, message="Incorrect password", status_code=401)

        return api_response(success=True, data={"id": user['id'], "name": user['name'], "email": user['email']},
                            message="Login successful")
    except Exception as e:
        return api_response(success=False, message=f"Login failed: {str(e)}", status_code=500)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)
