"""
SalesIQ — SQLAlchemy ORM Models
Defines all database tables as Python classes with soft-delete support.
"""
import json
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float,
    DateTime, create_engine, Index
)
from sqlalchemy.orm import DeclarativeBase, Session
from config import Config


class Base(DeclarativeBase):
    pass


# ── Helper mixin ──────────────────────────────────────────────────────────────

class TimestampMixin:
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class SoftDeleteMixin:
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)


# ── Models ────────────────────────────────────────────────────────────────────

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)

    __table_args__ = (
        Index("ix_users_email", "email"),
    )

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email,
                "created_at": str(self.created_at)}


class Report(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(300), nullable=False)
    website = Column(String(500), nullable=False)
    industry = Column(String(200), nullable=False)
    product_offered = Column(Text, default="")
    target_customer = Column(Text, default="")
    notes = Column(Text, default="")
    lead_score = Column(Integer, nullable=False)
    pain_points = Column(Text, default="[]")       # JSON array
    company_overview = Column(Text, default="")
    products = Column(Text, default="[]")          # JSON array
    business_goals = Column(Text, default="[]")    # JSON array
    growth_opportunities = Column(Text, default="[]")  # JSON array
    sales_strategy = Column(Text, default="")
    confidence = Column(String(20), default="High")
    email_script = Column(Text, default="")
    linkedin_script = Column(Text, default="")
    information_source = Column(String(100), default="AI Estimate")

    __table_args__ = (
        Index("ix_reports_company_name", "company_name"),
        Index("ix_reports_created_at", "created_at"),
        Index("ix_reports_is_deleted", "is_deleted"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "company_name": self.company_name,
            "website": self.website,
            "industry": self.industry,
            "product_offered": self.product_offered or "",
            "target_customer": self.target_customer or "",
            "notes": self.notes or "",
            "lead_score": self.lead_score,
            "pain_points": self._parse_json(self.pain_points),
            "company_overview": self.company_overview or "",
            "products": self._parse_json(self.products),
            "business_goals": self._parse_json(self.business_goals),
            "growth_opportunities": self._parse_json(self.growth_opportunities),
            "sales_strategy": self.sales_strategy or "",
            "confidence": self.confidence or "High",
            "email_script": self.email_script or "",
            "linkedin_script": self.linkedin_script or "",
            "information_source": self.information_source or "AI Estimate",
            "created_at": str(self.created_at),
        }

    @staticmethod
    def _parse_json(val):
        if not val:
            return []
        try:
            return json.loads(val)
        except Exception:
            return [val] if val else []


class Lead(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "saved_leads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(300), nullable=False)
    website = Column(String(500), nullable=False)
    industry = Column(String(200), nullable=False)
    lead_score = Column(Integer, nullable=False)
    status = Column(String(50), default="High Fit")
    notes = Column(Text, default="")
    pipeline_stage = Column(String(50), default="New")  # New | Contacted | Demo | Closed

    __table_args__ = (
        Index("ix_leads_company_name", "company_name"),
        Index("ix_leads_is_deleted", "is_deleted"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "company_name": self.company_name,
            "website": self.website,
            "industry": self.industry,
            "lead_score": self.lead_score,
            "status": self.status,
            "notes": self.notes or "",
            "pipeline_stage": self.pipeline_stage or "New",
            "created_at": str(self.created_at),
        }


class GeneratedContent(Base, TimestampMixin):
    __tablename__ = "generated_content"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(300), nullable=False)
    content_type = Column(String(100), nullable=False)
    prompt = Column(Text, default="")
    output_text = Column(Text, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "company_name": self.company_name,
            "content_type": self.content_type,
            "prompt": self.prompt or "",
            "output_text": self.output_text,
            "created_at": str(self.created_at),
        }


# ── Engine & session factory ──────────────────────────────────────────────────

def get_engine():
    db_path = Config.DATABASE_PATH
    return create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        echo=False,
    )


def get_session():
    """Return a new SQLAlchemy Session. Caller is responsible for closing."""
    from sqlalchemy.orm import sessionmaker
    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()
