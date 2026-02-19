from app.extensions import db
from datetime import datetime

class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    action    = db.Column(db.String(100))   # 'borrow', 'return', 'login', 'add_book'
    entity    = db.Column(db.String(50))    # 'book', 'user'
    entity_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id":        self.id,
            "user_id":   self.user_id,
            "action":    self.action,
            "entity":    self.entity,
            "entity_id": self.entity_id,
            "timestamp": self.timestamp.isoformat(),
        }
