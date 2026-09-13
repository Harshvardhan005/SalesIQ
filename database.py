"""
SalesIQ — Database Initialization
Uses SQLAlchemy to create all tables and seed default data.
Legacy get_db_connection() kept for backwards-compatibility during migration.
"""
import json
import os
import bcrypt

from models import Base, User, Report, Lead, GeneratedContent, get_engine, get_session
from config import Config


def init_db():
    """Create all SQLAlchemy tables and seed initial data if empty."""
    engine = get_engine()

    # Create all tables (safe; won't overwrite existing ones)
    Base.metadata.create_all(bind=engine)

    session = get_session()
    try:
        _seed_reports_if_empty(session)
        _seed_users_if_empty(session)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# ── Seeding ───────────────────────────────────────────────────────────────────

def _seed_reports_if_empty(session):
    if session.query(Report).count() > 0:
        return

    sample_reports = [
        Report(
            company_name="Stripe", website="https://stripe.com",
            industry="Fintech & Banking",
            product_offered="AI Sales Intelligence Engine",
            target_customer="Head of Sales", notes="Expanding sales team",
            lead_score=96,
            pain_points=json.dumps(["Manual merchant verification bottlenecks", "Multi-currency reconciliation overhead"]),
            company_overview="Stripe is a global technology company that builds economic infrastructure for the internet, enabling payments and business operations of all sizes.",
            products=json.dumps(["Stripe Payments", "Stripe Connect", "Stripe Billing"]),
            business_goals=json.dumps(["Expand international merchant base", "Launch automated compliance systems"]),
            growth_opportunities=json.dumps(["Provide real-time merchant auditing tools", "Integrate instant local currency payouts"]),
            sales_strategy="Pitch our automated compliance tracking and risk auditing workflows. Position SalesIQ as the key engine to save merchant operations team 15+ hours per week.",
            confidence="High",
            email_script="Subject: Streamlining outbound pipeline for Stripe\n\nHi [FirstName],\n\nNoticed Stripe is expanding enterprise sales...",
            linkedin_script="Hi [FirstName], impressive growth at Stripe! Would love to connect regarding AI research automation.",
            information_source="AI Estimate",
        ),
        Report(
            company_name="Vercel", website="https://vercel.com",
            industry="B2B SaaS / Software",
            product_offered="DevSecOps Scanner",
            target_customer="CTO & VP Eng", notes="Hiring enterprise SDRs",
            lead_score=92,
            pain_points=json.dumps(["Security compliance documentation overhead", "Lead triage taking engineering cycles"]),
            company_overview="Vercel provides developer tools and cloud hosting infrastructure that enables teams to deploy fast, secure frontends and websites.",
            products=json.dumps(["Next.js Hosting", "Vercel v0", "Vercel Analytics"]),
            business_goals=json.dumps(["Accelerate website load speeds globally", "Enforce security standards across projects"]),
            growth_opportunities=json.dumps(["Provide continuous frontend vulnerability scanning", "Integrate automated security linting at build-time"]),
            sales_strategy="Highlight our automated DevSecOps scanning that acts as a guardrail at build-time, preventing vulnerabilities from reaching the production edge.",
            confidence="High",
            email_script="Subject: Accelerating security compliance at Vercel\n\nHi [FirstName],\n\nCongrats on the platform updates...",
            linkedin_script="Hi [FirstName], great work on Vercel's recent launch. Let's connect!",
            information_source="AI Estimate",
        ),
        Report(
            company_name="Linear", website="https://linear.app",
            industry="B2B SaaS / Software",
            product_offered="AI Sales Platform",
            target_customer="VP of Revenue Ops", notes="Migrating enterprise customers",
            lead_score=89,
            pain_points=json.dumps(["Outbound SDR team needs tech stack signal monitoring", "Long sales cycle for workspace migrations"]),
            company_overview="Linear is an issue tracker and project management platform designed for high-performance software engineering teams.",
            products=json.dumps(["Linear Issue Tracker", "Linear Cycles", "Linear Roadmaps"]),
            business_goals=json.dumps(["Increase enterprise sales penetration", "Shorten client project onboarding cycle"]),
            growth_opportunities=json.dumps(["Sync workspace tickets with enterprise CRM systems", "Track team velocity metrics automatically"]),
            sales_strategy="Emphasize our direct integrations and CRM sync capabilities, showing how we can reduce administrative tasks for outbound teams by 25%.",
            confidence="Medium",
            email_script="Subject: Outbound signal monitoring for Linear\n\nHi [FirstName],\n\nNoticed your workspace migrations...",
            linkedin_script="Hi [FirstName], loving Linear! Let's connect regarding outbound intelligence.",
            information_source="AI Estimate",
        ),
    ]
    session.add_all(sample_reports)

    sample_leads = [
        Lead(company_name="Stripe", website="https://stripe.com", industry="Fintech & Banking", lead_score=96, status="High Fit", notes="Expanding enterprise team", pipeline_stage="Contacted"),
        Lead(company_name="Vercel", website="https://vercel.com", industry="B2B SaaS / Software", lead_score=92, status="High Fit", notes="DevOps pipeline lead", pipeline_stage="Demo"),
        Lead(company_name="Linear", website="https://linear.app", industry="B2B SaaS / Software", lead_score=89, status="Medium Fit", notes="Migrating users", pipeline_stage="New"),
        Lead(company_name="Figma", website="https://figma.com", industry="B2B SaaS / Software", lead_score=94, status="High Fit", notes="Design team scaling", pipeline_stage="New"),
        Lead(company_name="Notion", website="https://notion.so", industry="B2B SaaS / Software", lead_score=91, status="High Fit", notes="Workspace security compliance", pipeline_stage="Closed"),
    ]
    session.add_all(sample_leads)


def _seed_users_if_empty(session):
    if session.query(User).count() > 0:
        return

    default_users = [
        User(
            name="Harshvardhan Kumar",
            email="hv14835@gmail.com",
            password_hash="$2b$12$SO8aeNoA52d.wzgefTxRc.ITz86O12S933pLN1cZ7nKtErBNb1CBm",
        ),
        User(
            name="Demo User",
            email="demo@salesiq.ai",
            password_hash="$2b$12$Yo9g8FGNByX3QBQyfGXVqOGM9Kc6sZ3aAZetwvC/s8rx1QDm0Hdmq",
        ),
    ]
    session.add_all(default_users)


# ── Legacy compatibility shim ─────────────────────────────────────────────────
# Kept so any remaining direct imports of get_db_connection() don't break.

def get_db_connection():
    """
    DEPRECATED: Use models.get_session() instead.
    Returns a raw sqlite3 connection for backwards-compatibility only.
    """
    import sqlite3
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn
