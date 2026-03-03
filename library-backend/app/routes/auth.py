import re
from flask import Blueprint, request, jsonify
from app.extensions import db, bcrypt
from app.models.user import User
from app.utils.jwt_helpers import generate_tokens, decode_token, jwt_required
from app.services.activity_service import log_activity
import jwt

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _check_password_strength(password):
    """Return an error string if password fails strength requirements, else None."""
    if len(password) < 8:
        return "Password must be at least 8 characters"
    if not re.search(r'[A-Z]', password):
        return "Password must contain at least one uppercase letter"
    if not re.search(r'[0-9]', password):
        return "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*(),.?\":{}|<>_\-]', password):
        return "Password must contain at least one special character (!@#$%^ etc.)"
    return None


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name     = data.get("name", "").strip()
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({"error": "name, email, and password are required"}), 400
    pw_error = _check_password_strength(password)
    if pw_error:
        return jsonify({"error": pw_error}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    hashed = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(name=name, email=email, password_hash=hashed)
    db.session.add(user)
    db.session.commit()
    log_activity(user.id, "register", "user", user.id)

    access, refresh = generate_tokens(user.id)
    return jsonify({
        "message": "Account created",
        "user": user.to_dict(),
        "access_token": access,
        "refresh_token": refresh,
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401
    if not user.is_active:
        return jsonify({"error": "Account is deactivated"}), 403

    log_activity(user.id, "login", "user", user.id)
    access, refresh = generate_tokens(user.id)
    return jsonify({
        "user": user.to_dict(),
        "access_token": access,
        "refresh_token": refresh,
    })


@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    data  = request.get_json()
    token = data.get("refresh_token", "")
    try:
        from flask import current_app
        payload = jwt.decode(token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
        if payload.get("type") != "refresh":
            raise ValueError("Not a refresh token")
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Refresh token expired, please log in again"}), 401
    except Exception:
        return jsonify({"error": "Invalid refresh token"}), 401

    user = User.query.get(payload["sub"])
    if not user or not user.is_active:
        return jsonify({"error": "User not found"}), 401

    access, new_refresh = generate_tokens(user.id)
    return jsonify({"access_token": access, "refresh_token": new_refresh})


@auth_bp.route("/me", methods=["GET"])
@jwt_required
def me():
    return jsonify({"user": request.current_user.to_dict()})
