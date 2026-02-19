from app.extensions import db
from app.models.activity import ActivityLog

def log_activity(user_id, action, entity=None, entity_id=None):
    """Write an activity log entry. Safe to call anywhere."""
    try:
        entry = ActivityLog(
            user_id=user_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
        )
        db.session.add(entry)
        db.session.commit()
    except Exception:
        db.session.rollback()
