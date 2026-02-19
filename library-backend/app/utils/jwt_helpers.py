import jwt
import datetime
import os
from functools import wraps
from flask import request, jsonify, current_app
from app.models.user import User

def generate_tokens(user_id):
    """Generate access and refresh JWT tokens."""
    access_payload = {
        "sub": user_id,
        "type": "access",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(
            seconds=current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
        ),
        "iat": datetime.datetime.utcnow(),
    }
    refresh_payload = {
        "sub": user_id,
        "type": "refresh",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(
            seconds=current_app.config["JWT_REFRESH_TOKEN_EXPIRES"]
        ),
        "iat": datetime.datetime.utcnow(),
    }
    secret = current_app.config["JWT_SECRET_KEY"]
    access_token  = jwt.encode(access_payload,  secret, algorithm="HS256")
    refresh_token = jwt.encode(refresh_payload, secret, algorithm="HS256")
    return access_token, refresh_token


def decode_token(token):
    secret = current_app.config["JWT_SECRET_KEY"]
    return jwt.decode(token, secret, algorithms=["HS256"])


def jwt_required(f):
    """Decorator: require a valid access JWT in Authorization header."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or malformed token"}), 401
        token = auth_header.split(" ")[1]
        try:
            payload = decode_token(token)
            if payload.get("type") != "access":
                raise ValueError("Wrong token type")
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except Exception:
            return jsonify({"error": "Invalid token"}), 401

        user = User.query.get(payload["sub"])
        if not user or not user.is_active:
            return jsonify({"error": "User not found or inactive"}), 401

        request.current_user = user
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    """Decorator: require user to have one of the given roles."""
    def decorator(f):
        @wraps(f)
        @jwt_required
        def decorated(*args, **kwargs):
            if request.current_user.role not in roles:
                return jsonify({"error": "Insufficient permissions"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
