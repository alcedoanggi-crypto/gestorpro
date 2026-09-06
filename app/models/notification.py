from datetime import datetime

from ..extensions import db


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    message = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(255))
    category = db.Column(db.String(30), default="info")  # info | warning | danger | success
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    dedup_key = db.Column(db.String(120), index=True)  # evita duplicados del scanner
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification u={self.user_id} {self.message[:20]!r}>"
