from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.book import Book
from app.utils.jwt_helpers import jwt_required, role_required
from app.services.activity_service import log_activity

books_bp = Blueprint("books", __name__, url_prefix="/api/books")


@books_bp.route("", methods=["GET"])
@jwt_required
def list_books():
    page    = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 12, type=int)
    search  = request.args.get("search", "")
    genre   = request.args.get("genre", "")

    query = Book.query
    if search:
        like = f"%{search}%"
        query = query.filter(
            (Book.title.like(like)) | (Book.author.like(like)) | (Book.isbn.like(like))
        )
    if genre:
        query = query.filter_by(genre=genre)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "books":    [b.to_dict() for b in pagination.items],
        "total":    pagination.total,
        "page":     pagination.page,
        "pages":    pagination.pages,
        "per_page": pagination.per_page,
    })


@books_bp.route("/<int:book_id>", methods=["GET"])
@jwt_required
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify(book.to_dict())


@books_bp.route("", methods=["POST"])
@role_required("librarian", "admin")
def add_book():
    data = request.get_json()
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400

    copies = data.get("total_copies", 1)
    book = Book(
        title            = title,
        author           = data.get("author"),
        isbn             = data.get("isbn"),
        genre            = data.get("genre"),
        description      = data.get("description"),
        total_copies     = copies,
        available_copies = copies,
    )
    db.session.add(book)
    db.session.commit()
    log_activity(request.current_user.id, "add_book", "book", book.id)
    return jsonify(book.to_dict()), 201


@books_bp.route("/<int:book_id>", methods=["PUT"])
@role_required("librarian", "admin")
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.get_json()

    for field in ("title", "author", "isbn", "genre", "description"):
        if field in data:
            setattr(book, field, data[field])

    if "total_copies" in data:
        diff = data["total_copies"] - book.total_copies
        book.total_copies     = data["total_copies"]
        book.available_copies = max(0, book.available_copies + diff)

    db.session.commit()
    log_activity(request.current_user.id, "update_book", "book", book.id)
    return jsonify(book.to_dict())


@books_bp.route("/<int:book_id>", methods=["DELETE"])
@role_required("admin")
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    log_activity(request.current_user.id, "delete_book", "book", book_id)
    return jsonify({"message": "Book deleted"})
