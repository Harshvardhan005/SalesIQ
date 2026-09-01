import sqlite3
import os
import json
from config import Config

def get_db_connection():
    """Establish connection to SQLite database with dictionary row factory."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create SQLite database tables if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Migration Check: Drop reports table if company_overview column is missing
    try:
        cursor.execute("PRAGMA table_info(reports)")
        cols = [row[1] for row in cursor.fetchall()]
        if cols and "company_overview" not in cols:
            cursor.execute("DROP TABLE IF EXISTS reports")
        elif cols and "information_source" not in cols:
            cursor.execute("ALTER TABLE reports ADD COLUMN information_source TEXT DEFAULT 'AI Estimate'")
    except Exception:
        pass

    # Table 1: Reports (Expanded to support structured AI signals)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            website TEXT NOT NULL,
            industry TEXT NOT NULL,
            product_offered TEXT,
            target_customer TEXT,
            notes TEXT,
            lead_score INTEGER NOT NULL,
            pain_points TEXT NOT NULL,
            company_overview TEXT,
            products TEXT,
            business_goals TEXT,
            growth_opportunities TEXT,
            sales_strategy TEXT,
            confidence TEXT,
            email_script TEXT,
            linkedin_script TEXT,
            information_source TEXT DEFAULT 'AI Estimate',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table 2: Generated Content
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS generated_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            content_type TEXT NOT NULL,
            prompt TEXT,
            output_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table 3: Saved Leads
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            website TEXT NOT NULL,
            industry TEXT NOT NULL,
            lead_score INTEGER NOT NULL,
            status TEXT DEFAULT 'High Fit',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Insert default seed data if database is empty
    cursor.execute("SELECT COUNT(*) as count FROM reports")
    if cursor.fetchone()['count'] == 0:
        seed_database(cursor)

    conn.commit()
    conn.close()

def seed_database(cursor):
    """Seed initial sample data for demonstration."""
    sample_reports = [
        (
            "Stripe", "https://stripe.com", "Fintech & Banking", 
            "AI Sales Intelligence Engine", "Head of Sales", "Expanding sales team", 96, 
            json.dumps(["Manual merchant verification bottlenecks", "Multi-currency reconciliation overhead"]),
            "Stripe is a global technology company that builds economic infrastructure for the internet, enabling payments and business operations of all sizes.",
            json.dumps(["Stripe Payments", "Stripe Connect", "Stripe Billing"]),
            json.dumps(["Expand international merchant base", "Launch automated compliance systems"]),
            json.dumps(["Provide real-time merchant auditing tools", "Integrate instant local currency payouts"]),
            "Pitch our automated compliance tracking and risk auditing workflows. Position SalesIQ as the key engine to save merchant operations team 15+ hours per week.",
            "High",
            "Subject: Streamlining outbound pipeline for Stripe\n\nHi [FirstName],\n\nNoticed Stripe is expanding enterprise sales...", 
            "Hi [FirstName], impressive growth at Stripe! Would love to connect regarding AI research automation."
        ),
        (
            "Vercel", "https://vercel.com", "B2B SaaS / Software", 
            "DevSecOps Scanner", "CTO & VP Eng", "Hiring enterprise SDRs", 92, 
            json.dumps(["Security compliance documentation overhead", "Lead triage taking engineering cycles"]),
            "Vercel provides developer tools and cloud hosting infrastructure that enables teams to deploy fast, secure frontends and websites.",
            json.dumps(["Next.js Hosting", "Vercel v0", "Vercel Analytics"]),
            json.dumps(["Accelerate website load speeds globally", "Enforce security standards across projects"]),
            json.dumps(["Provide continuous frontend vulnerability scanning", "Integrate automated security linting at build-time"]),
            "Highlight our automated DevSecOps scanning that acts as a guardrail at build-time, preventing vulnerabilities from reaching the production edge.",
            "High",
            "Subject: Accelerating security compliance at Vercel\n\nHi [FirstName],\n\nCongrats on the platform updates...", 
            "Hi [FirstName], great work on Vercel's recent launch. Let's connect!"
        ),
        (
            "Linear", "https://linear.app", "B2B SaaS / Software", 
            "AI Sales Platform", "VP of Revenue Ops", "Migrating enterprise customers", 89, 
            json.dumps(["Outbound SDR team needs tech stack signal monitoring", "Long sales cycle for workspace migrations"]),
            "Linear is an issue tracker and project management platform designed for high-performance software engineering teams.",
            json.dumps(["Linear Issue Tracker", "Linear Cycles", "Linear Roadmaps"]),
            json.dumps(["Increase enterprise sales penetration", "Shorten client project onboarding cycle"]),
            json.dumps(["Sync workspace tickets with enterprise CRM systems", "Track team velocity metrics automatically"]),
            "Emphasize our direct integrations and CRM sync capabilities, showing how we can reduce administrative tasks for outbound teams by 25%.",
            "Medium",
            "Subject: Outbound signal monitoring for Linear\n\nHi [FirstName],\n\nNoticed your workspace migrations...", 
            "Hi [FirstName], loving Linear! Let's connect regarding outbound intelligence."
        )
    ]

    for r in sample_reports:
        r_list = list(r)
        r_list.append("AI Estimate") # for information_source
        cursor.execute('''
            INSERT INTO reports (
                company_name, website, industry, product_offered, target_customer, notes, lead_score, pain_points,
                company_overview, products, business_goals, growth_opportunities, sales_strategy, confidence,
                email_script, linkedin_script, information_source
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', tuple(r_list))

    sample_leads = [
        ("Stripe", "https://stripe.com", "Fintech & Banking", 96, "High Fit", "Expanding enterprise team"),
        ("Vercel", "https://vercel.com", "B2B SaaS / Software", 92, "High Fit", "DevOps pipeline lead"),
        ("Linear", "https://linear.app", "B2B SaaS / Software", 89, "Medium Fit", "Migrating users"),
        ("Figma", "https://figma.com", "B2B SaaS / Software", 94, "High Fit", "Design team scaling"),
        ("Notion", "https://notion.so", "B2B SaaS / Software", 91, "High Fit", "Workspace security compliance")
    ]

    for l in sample_leads:
        cursor.execute('''
            INSERT INTO saved_leads (company_name, website, industry, lead_score, status, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', l)

