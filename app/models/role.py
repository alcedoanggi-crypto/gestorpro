from ..extensions import db


class Role(db.Model):
    __tablename__ = "roles"

    ADMIN = "admin"
    MANAGER = "gerente"
    COLLABORATOR = "colaborador"

    DEFAULTS = {
        ADMIN: "Acceso total: usuarios, configuracion y todos los proyectos.",
        MANAGER: "Gestiona sus proyectos, equipos, tareas y reportes.",
        COLLABORATOR: "Trabaja sobre las tareas que tiene asignadas.",
    }

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))

    users = db.relationship("User", back_populates="role")

    @staticmethod
    def seed_defaults():
        for name, desc in Role.DEFAULTS.items():
            if not Role.query.filter_by(name=name).first():
                db.session.add(Role(name=name, description=desc))
        db.session.commit()

    @staticmethod
    def get(name):
        return Role.query.filter_by(name=name).first()

    def __repr__(self):
        return f"<Role {self.name}>"
