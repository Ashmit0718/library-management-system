from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from app.extensions import db
from app.models.borrow import BorrowRecord
from app.models.book import Book
from app.utils.jwt_helpers import jwt_required, role_required
from app.services.activity_service import log_activity

borrows_bp = Blueprint("borrows", __name__, url_prefix="/api/borrows")

BORROW_DAYS = 14  # default loan period


@borrows_bp.route("", methods=["POST"])
@jwt_required
def borrow_book():
    data    = request.get_json()
    book_id = data.get("book_id")
    user    = request.current_user

    if not book_id:
        return jsonify({"error": "book_id is required"}), 400

    book = Book.query.get_or_404(book_id)
    if book.available_copies < 1:
        return jsonify({"error": "No copies available"}), 409

    # Check if user already has this book borrowed
    existing = BorrowRecord.query.filter_by(
        user_id=user.id, book_id=book_id, status="borrowed"
    ).first()
    if existing:
        return jsonify({"error": "You already have this book borrowed"}), 409

    due = datetime.utcnow() + timedelta(days=BORROW_DAYS)
    record = BorrowRecord(user_id=user.id, book_id=book_id, due_date=due)
    book.available_copies -= 1

    db.session.add(record)
    db.session.commit()
    log_activity(user.id, "borrow", "book", book_id)
    return jsonify(record.to_dict()), 201


@borrows_bp.route("/<int:record_id>/return", methods=["PUT"])
@jwt_required
def return_book(record_id):
    user   = request.current_user
    record = BorrowRecord.query.get_or_404(record_id)

    # Members can only return their own records; librarian/admin can return any
    if user.role == "member" and record.user_id != user.id:
        return jsonify({"error": "Not your borrow record"}), 403
    if record.status == "returned":
        return jsonify({"error": "Already returned"}), 409

    record.returned_at = datetime.utcnow()
    record.status      = "returned"
    record.book.available_copies += 1

    db.session.commit()
    log_activity(user.id, "return", "book", record.book_id)
    return jsonify(record.to_dict())


@borrows_bp.route("", methods=["GET"])
@jwt_required
def list_borrows():
    user     = request.current_user
    page     = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    status   = request.args.get("status")

    if user.role == "member":
        query = BorrowRecord.query.filter_by(user_id=user.id)
    else:
        query = BorrowRecord.query

    if status:
        query = query.filter_by(status=status)

    query = query.order_by(BorrowRecord.borrowed_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "borrows":  [r.to_dict() for r in pagination.items],
        "total":    pagination.total,
        "page":     pagination.page,
        "pages":    pagination.pages,
    })
