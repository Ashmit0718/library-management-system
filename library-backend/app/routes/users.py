from flask import Blueprint, request, jsonify
from app.extensions import db, bcrypt
from app.models.user import User
from app.utils.jwt_helpers import role_required

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


@users_bp.route("", methods=["GET"])
@role_required("admin")
def list_users():
    page     = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    search   = request.args.get("search", "")
    role     = request.args.get("role", "")

    query = User.query
    if search:
        like = f"%{search}%"
        query = query.filter((User.name.like(like)) | (User.email.like(like)))
    if role:
        query = query.filter_by(role=role)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "users":    [u.to_dict() for u in pagination.items],
        "total":    pagination.total,
        "page":     pagination.page,
        "pages":    pagination.pages,
    })


@users_bp.route("/<int:user_id>", methods=["GET"])
@role_required("admin")
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())


@users_bp.route("/<int:user_id>", methods=["PUT"])
@role_required("admin")
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    if "role" in data and data["role"] in ("member", "librarian", "admin"):
        user.role = data["role"]
    if "is_active" in data:
        user.is_active = bool(data["is_active"])
    if "name" in data:
        user.name = data["name"]

    db.session.commit()
    return jsonify(user.to_dict())
