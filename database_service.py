"""
SalesIQ — Database Service Layer
All database operations use SQLAlchemy ORM with soft-delete support.
"""
import json
from datetime import datetime, timezone

from models import Report, Lead, GeneratedContent, User, get_session


class DatabaseService:

    # ── Reports ───────────────────────────────────────────────────────────────

    @staticmethod
    def get_all_reports():
        session = get_session()
        try:
            rows = (
                session.query(Report)
                .filter_by(is_deleted=False)
                .order_by(Report.created_at.desc())
                .all()
            )
            return [r.to_dict() for r in rows]
        finally:
            session.close()

    @staticmethod
    def get_report_by_id(report_id):
        session = get_session()
        try:
            row = session.query(Report).filter_by(id=report_id, is_deleted=False).first()
            return row.to_dict() if row else None
        finally:
            session.close()

    @staticmethod
    def get_report_by_company_name(company_name):
        session = get_session()
        try:
            row = (
                session.query(Report)
                .filter_by(company_name=company_name, is_deleted=False)
                .order_by(Report.created_at.desc())
                .first()
            )
            return row.to_dict() if row else None
        finally:
            session.close()

    @staticmethod
    def create_report(report_data):
        session = get_session()
        try:
            def _j(val):
                if isinstance(val, list):
                    return json.dumps(val)
                if isinstance(val, str):
                    return val  # already serialized
                return json.dumps([])

            report = Report(
                company_name=report_data["company_name"],
                website=report_data["website"],
                industry=report_data["industry"],
                product_offered=report_data.get("product_offered", ""),
                target_customer=report_data.get("target_customer", ""),
                notes=report_data.get("notes", ""),
                lead_score=report_data["lead_score"],
                pain_points=_j(report_data.get("pain_points", [])),
                company_overview=report_data.get("company_overview", ""),
                products=_j(report_data.get("products", [])),
                business_goals=_j(report_data.get("business_goals", [])),
                growth_opportunities=_j(report_data.get("growth_opportunities", [])),
                sales_strategy=report_data.get("sales_strategy", ""),
                confidence=report_data.get("confidence", "High"),
                email_script=report_data.get("email_script", ""),
                linkedin_script=report_data.get("linkedin_script", ""),
                information_source=report_data.get("information_source", "AI Estimate"),
            )
            session.add(report)
            session.commit()
            return report.id
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def delete_report(report_id):
        """Soft-delete a report by ID. Returns True if found and deleted."""
        session = get_session()
        try:
            row = session.query(Report).filter_by(id=report_id, is_deleted=False).first()
            if not row:
                return False
            row.soft_delete()
            session.commit()
            return True
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ── Generated Content ─────────────────────────────────────────────────────

    @staticmethod
    def save_generated_content(company_name, content_type, prompt, output_text):
        session = get_session()
        try:
            content = GeneratedContent(
                company_name=company_name,
                content_type=content_type,
                prompt=prompt or "",
                output_text=output_text,
            )
            session.add(content)
            session.commit()
            return content.id
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ── Leads ─────────────────────────────────────────────────────────────────

    @staticmethod
    def get_all_leads():
        session = get_session()
        try:
            rows = (
                session.query(Lead)
                .filter_by(is_deleted=False)
                .order_by(Lead.created_at.desc())
                .all()
            )
            return [r.to_dict() for r in rows]
        finally:
            session.close()

    @staticmethod
    def get_lead_by_id(lead_id):
        session = get_session()
        try:
            row = session.query(Lead).filter_by(id=lead_id, is_deleted=False).first()
            return row.to_dict() if row else None
        finally:
            session.close()

    @staticmethod
    def create_lead(lead_data):
        session = get_session()
        try:
            lead = Lead(
                company_name=lead_data["company_name"],
                website=lead_data["website"],
                industry=lead_data["industry"],
                lead_score=lead_data["lead_score"],
                status=lead_data.get("status", "High Fit"),
                notes=lead_data.get("notes", ""),
                pipeline_stage=lead_data.get("pipeline_stage", "New"),
            )
            session.add(lead)
            session.commit()
            return lead.id
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def delete_lead(lead_id):
        """Soft-delete a lead by ID. Returns True if found and deleted."""
        session = get_session()
        try:
            row = session.query(Lead).filter_by(id=lead_id, is_deleted=False).first()
            if not row:
                return False
            row.soft_delete()
            session.commit()
            return True
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def update_lead_stage(lead_id, stage):
        """Update the pipeline stage for a lead."""
        valid_stages = {"New", "Contacted", "Demo", "Closed"}
        if stage not in valid_stages:
            raise ValueError(f"Invalid stage '{stage}'. Must be one of {valid_stages}")
        session = get_session()
        try:
            row = session.query(Lead).filter_by(id=lead_id, is_deleted=False).first()
            if not row:
                return None
            row.pipeline_stage = stage
            session.commit()
            return row.to_dict()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ── Dashboard Stats ───────────────────────────────────────────────────────

    @staticmethod
    def get_dashboard_stats():
        session = get_session()
        try:
            from sqlalchemy import func
            total_companies = session.query(func.count(Report.id)).filter_by(is_deleted=False).scalar() or 0
            total_leads = session.query(func.count(Lead.id)).filter_by(is_deleted=False).scalar() or 0
            avg_score_raw = session.query(func.avg(Report.lead_score)).filter_by(is_deleted=False).scalar()
            avg_lead_score = round(float(avg_score_raw), 1) if avg_score_raw else 90.0

            # Industry breakdown for analytics
            industry_rows = (
                session.query(Report.industry, func.count(Report.id).label("count"))
                .filter_by(is_deleted=False)
                .group_by(Report.industry)
                .all()
            )
            industry_breakdown = {row.industry: row.count for row in industry_rows}

            # Pipeline stage distribution
            stage_rows = (
                session.query(Lead.pipeline_stage, func.count(Lead.id).label("count"))
                .filter_by(is_deleted=False)
                .group_by(Lead.pipeline_stage)
                .all()
            )
            pipeline_distribution = {row.pipeline_stage: row.count for row in stage_rows}

            return {
                "total_companies": total_companies,
                "total_leads": total_leads,
                "avg_lead_score": avg_lead_score,
                "recent_reports": total_companies,
                "industry_breakdown": industry_breakdown,
                "pipeline_distribution": pipeline_distribution,
            }
        finally:
            session.close()

    # ── Users ─────────────────────────────────────────────────────────────────

    @staticmethod
    def create_user(name, email, password_hash):
        """Create a new user. Raises ValueError on duplicate email."""
        session = get_session()
        try:
            user = User(name=name, email=email, password_hash=password_hash)
            session.add(user)
            session.commit()
            return user.id
        except Exception as e:
            session.rollback()
            raise ValueError(f"Email already registered: {str(e)}")
        finally:
            session.close()

    @staticmethod
    def get_user_by_email(email):
        """Fetch user dict by email, or None if not found."""
        session = get_session()
        try:
            row = session.query(User).filter_by(email=email).first()
            return row.to_dict() if row else None
        finally:
            session.close()

    @staticmethod
    def get_user_by_id(user_id):
        """Fetch user dict by id, or None if not found."""
        session = get_session()
        try:
            row = session.query(User).filter_by(id=user_id).first()
            return row.to_dict() if row else None
        finally:
            session.close()
