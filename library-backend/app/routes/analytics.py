from flask import Blueprint, jsonify
from app.extensions import db
from app.models.user import User
from app.models.book import Book
from app.models.borrow import BorrowRecord
from app.utils.jwt_helpers import jwt_required, role_required
from sqlalchemy import text

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")


@analytics_bp.route("/dashboard", methods=["GET"])
@jwt_required
def dashboard():
    total_books   = Book.query.count()
    total_users   = User.query.filter_by(role="member").count()
    total_borrows = BorrowRecord.query.count()
    active_borrows = BorrowRecord.query.filter_by(status="borrowed").count()
    overdue_count  = db.session.execute(
        text("SELECT COUNT(*) FROM borrow_records WHERE status='borrowed' AND due_date < NOW()")
    ).scalar()
    available_books = Book.query.filter(Book.available_copies > 0).count()

    return jsonify({
        "total_books":    total_books,
        "total_members":  total_users,
        "total_borrows":  total_borrows,
        "active_borrows": active_borrows,
        "overdue_count":  overdue_count,
        "available_books": available_books,
    })


@analytics_bp.route("/trending", methods=["GET"])
@jwt_required
def trending():
    sql = text("""
        SELECT b.id, b.title, b.author, b.genre,
               COUNT(br.id) AS borrow_count
        FROM books b
        JOIN borrow_records br ON br.book_id = b.id
        WHERE br.borrowed_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        GROUP BY b.id
        ORDER BY borrow_count DESC
        LIMIT 10
    """)
    rows = db.session.execute(sql).mappings().all()
    return jsonify([dict(r) for r in rows])


@analytics_bp.route("/leaderboard", methods=["GET"])
@jwt_required
def leaderboard():
    sql = text("""
        SELECT u.id, u.name,
               COUNT(br.id)                        AS total_borrows,
               SUM(br.status = 'returned')         AS returned,
               SUM(br.status = 'overdue')          AS overdue,
               RANK() OVER (ORDER BY COUNT(br.id) DESC) AS rank_pos
        FROM users u
        LEFT JOIN borrow_records br ON br.user_id = u.id
        WHERE u.role = 'member' AND u.is_active = 1
        GROUP BY u.id
        ORDER BY rank_pos
        LIMIT 20
    """)
    rows = db.session.execute(sql).mappings().all()
    return jsonify([dict(r) for r in rows])


@analytics_bp.route("/overdue", methods=["GET"])
@role_required("librarian", "admin")
def overdue():
    sql = text("""
        SELECT br.id, u.name AS user_name, u.email,
               b.title AS book_title,
               br.borrowed_at, br.due_date,
               DATEDIFF(NOW(), br.due_date) AS days_overdue
        FROM borrow_records br
        JOIN users u ON u.id = br.user_id
        JOIN books b ON b.id = br.book_id
        WHERE br.status = 'borrowed' AND br.due_date < NOW()
        ORDER BY days_overdue DESC
    """)
    rows = db.session.execute(sql).mappings().all()
    result = []
    for r in rows:
        row = dict(r)
        # Convert datetime objects to ISO strings
        for k, v in row.items():
            if hasattr(v, "isoformat"):
                row[k] = v.isoformat()
        result.append(row)
    return jsonify(result)


@analytics_bp.route("/genre-stats", methods=["GET"])
@jwt_required
def genre_stats():
    sql = text("""
        SELECT b.genre, COUNT(br.id) AS borrow_count
        FROM books b
        LEFT JOIN borrow_records br ON br.book_id = b.id
        WHERE b.genre IS NOT NULL
        GROUP BY b.genre
        ORDER BY borrow_count DESC
    """)
    rows = db.session.execute(sql).mappings().all()
    return jsonify([dict(r) for r in rows])
