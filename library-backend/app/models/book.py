from app.extensions import db
from datetime import datetime

class Book(db.Model):
    __tablename__ = "books"

    id               = db.Column(db.Integer, primary_key=True)
    title            = db.Column(db.String(300), nullable=False)
    author           = db.Column(db.String(200))
    isbn             = db.Column(db.String(20), unique=True, index=True)
    genre            = db.Column(db.String(100), index=True)
    description      = db.Column(db.Text)
    total_copies     = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    borrows = db.relationship("BorrowRecord", backref="book", lazy="dynamic")

    def to_dict(self):
        return {
            "id":               self.id,
            "title":            self.title,
            "author":           self.author,
            "isbn":             self.isbn,
            "genre":            self.genre,
            "description":      self.description,
            "total_copies":     self.total_copies,
            "available_copies": self.available_copies,
            "created_at":       self.created_at.isoformat(),
        }
