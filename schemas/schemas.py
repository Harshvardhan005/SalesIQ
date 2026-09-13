"""
SalesIQ — Marshmallow Validation Schemas
Provides input validation for all API endpoints.
"""
from marshmallow import Schema, fields, validate, ValidationError, pre_load
import re


class AuthRegisterSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=200))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8, max=128))

    @staticmethod
    def validate_password_strength(password):
        """Ensure password has at least one uppercase, one digit, one special char."""
        if not re.search(r"[A-Z]", password):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r"\d", password):
            raise ValidationError("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-]", password):
            raise ValidationError("Password must contain at least one special character.")


class AuthLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=1))


class CompanyAnalysisSchema(Schema):
    company_name = fields.Str(required=True, validate=validate.Length(min=1, max=300))
    website = fields.Str(required=True, validate=validate.Length(min=3, max=500))
    industry = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    product_offered = fields.Str(load_default="")
    target_customer = fields.Str(load_default="")
    notes = fields.Str(load_default="")
    manual_company_info = fields.Str(load_default="")


class ContentGenerationSchema(Schema):
    company_name = fields.Str(required=True, validate=validate.Length(min=1, max=300))
    content_type = fields.Str(
        required=True,
        validate=validate.OneOf([
            "Cold Email", "Follow-up Email", "LinkedIn Connection Request",
            "LinkedIn InMail", "Sales Call Script", "Product Demo Pitch"
        ])
    )
    tone = fields.Str(
        required=True,
        validate=validate.OneOf(["Professional", "Friendly", "Consultative", "Persuasive"])
    )
    length = fields.Str(
        required=True,
        validate=validate.OneOf(["Short", "Medium", "Long"])
    )
    prompt = fields.Str(load_default="")


class LeadSchema(Schema):
    company_name = fields.Str(required=True, validate=validate.Length(min=1, max=300))
    website = fields.Str(required=True, validate=validate.Length(min=3, max=500))
    industry = fields.Str(load_default="Unknown")
    lead_score = fields.Int(load_default=80, validate=validate.Range(min=0, max=100))
    status = fields.Str(load_default="High Fit")
    notes = fields.Str(load_default="")
    pipeline_stage = fields.Str(
        load_default="New",
        validate=validate.OneOf(["New", "Contacted", "Demo", "Closed"])
    )


class PipelineStageSchema(Schema):
    stage = fields.Str(
        required=True,
        validate=validate.OneOf(["New", "Contacted", "Demo", "Closed"])
    )


def validate_schema(schema_cls, data):
    """
    Validate a dict against a Marshmallow schema.
    Returns (cleaned_data, errors_dict). errors_dict is empty on success.
    """
    schema = schema_cls()
    try:
        cleaned = schema.load(data)
        return cleaned, {}
    except ValidationError as err:
        return None, err.messages
