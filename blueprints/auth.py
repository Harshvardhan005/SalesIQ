"""
SalesIQ — Auth Blueprint
Handles user registration, login, logout, and token verification.
"""
import bcrypt
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from extensions import limiter
from database_service import DatabaseService
from schemas.schemas import AuthRegisterSchema, AuthLoginSchema, validate_schema

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def api_response(success=True, data=None, message="", status_code=200):
    return jsonify({"success": success, "message": message, "data": data}), status_code


@auth_bp.route("/register", methods=["POST"])
@limiter.limit("10 per minute")
def register():
    payload = request.get_json() or {}
    data, errors = validate_schema(AuthRegisterSchema, payload)
    if errors:
        return api_response(False, errors, "Validation failed", 400)

    name = data["name"].strip()
    email = data["email"].strip().lower()
    password = data["password"].strip()

    try:
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        user_id = DatabaseService.create_user(name, email, password_hash)

        access_token = create_access_token(identity=str(user_id))
        refresh_token = create_refresh_token(identity=str(user_id))

        return api_response(
            True,
            {
                "id": user_id, "name": name, "email": email,
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
            "Account created successfully",
            201,
        )
    except ValueError as ve:
        return api_response(False, None, str(ve), 409)
    except Exception as e:
        return api_response(False, None, f"Registration failed: {str(e)}", 500)


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    payload = request.get_json() or {}
    data, errors = validate_schema(AuthLoginSchema, payload)
    if errors:
        return api_response(False, errors, "Validation failed", 400)

    email = data["email"].strip().lower()
    password = data["password"].strip()

    try:
        user = DatabaseService.get_user_by_email(email)
        if not user:
            return api_response(False, None, "No account found with this email", 404)

        # get_user_by_email from to_dict() doesn't include password_hash, fetch directly
        session_obj = _get_user_with_hash(email)
        if not session_obj:
            return api_response(False, None, "No account found with this email", 404)

        is_valid = bcrypt.checkpw(password.encode("utf-8"), session_obj["password_hash"].encode("utf-8"))
        if not is_valid:
            return api_response(False, None, "Incorrect password", 401)

        access_token = create_access_token(identity=str(user["id"]))
        refresh_token = create_refresh_token(identity=str(user["id"]))

        return api_response(
            True,
            {
                "id": user["id"], "name": user["name"], "email": user["email"],
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
            "Login successful",
        )
    except Exception as e:
        return api_response(False, None, f"Login failed: {str(e)}", 500)


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """Return current user info from JWT identity."""
    user_id = int(get_jwt_identity())
    user = DatabaseService.get_user_by_id(user_id)
    if not user:
        return api_response(False, None, "User not found", 404)
    return api_response(True, user, "User info retrieved")


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """Logout is handled client-side (delete token).
    This endpoint exists for future token blocklist support."""
    return api_response(True, None, "Logged out successfully")


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Issue a new access token using a valid refresh token."""
    user_id = get_jwt_identity()
    new_token = create_access_token(identity=user_id)
    return api_response(True, {"access_token": new_token}, "Token refreshed")


# ── Internal helper ──────────────────────────────────────────────────────────

def _get_user_with_hash(email):
    """Fetch full user row including password_hash for bcrypt comparison."""
    from models import User, get_session
    session = get_session()
    try:
        row = session.query(User).filter_by(email=email).first()
        if not row:
            return None
        return {"id": row.id, "name": row.name, "email": row.email, "password_hash": row.password_hash}
    finally:
        session.close()
