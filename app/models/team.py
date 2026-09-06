from datetime import datetime

from ..extensions import db
from .user import team_members


class Team(db.Model):
    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    members = db.relationship("User", secondary=team_members, back_populates="teams")
    projects = db.relationship("Project", back_populates="team")

    @property
    def member_count(self):
        return len(self.members)

    def __repr__(self):
        return f"<Team {self.name}>"
