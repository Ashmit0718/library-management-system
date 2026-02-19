from app.extensions import db
from datetime import datetime

class BorrowRecord(db.Model):
    __tablename__ = "borrow_records"

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    book_id     = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False, index=True)
    borrowed_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date    = db.Column(db.DateTime, nullable=False)
    returned_at = db.Column(db.DateTime)
    status      = db.Column(db.Enum("borrowed", "returned", "overdue"), default="borrowed", index=True)

    def to_dict(self):
        return {
            "id":          self.id,
            "user_id":     self.user_id,
            "book_id":     self.book_id,
            "borrowed_at": self.borrowed_at.isoformat(),
            "due_date":    self.due_date.isoformat(),
            "returned_at": self.returned_at.isoformat() if self.returned_at else None,
            "status":      self.status,
            "book":        self.book.to_dict() if self.book else None,
        }
