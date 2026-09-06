"""Enumeraciones de dominio compartidas por los modelos."""


class ProjectStatus:
    PLANNING = "planificacion"
    ACTIVE = "activo"
    ON_HOLD = "en_pausa"
    COMPLETED = "completado"
    CANCELLED = "cancelado"

    ALL = [PLANNING, ACTIVE, ON_HOLD, COMPLETED, CANCELLED]
    LABELS = {
        PLANNING: "Planificacion",
        ACTIVE: "Activo",
        ON_HOLD: "En pausa",
        COMPLETED: "Completado",
        CANCELLED: "Cancelado",
    }
    CLOSED = {COMPLETED, CANCELLED}

    @classmethod
    def choices(cls):
        return [(v, cls.LABELS[v]) for v in cls.ALL]


class TaskStatus:
    TODO = "pendiente"
    IN_PROGRESS = "en_progreso"
    REVIEW = "en_revision"
    DONE = "completada"

    ALL = [TODO, IN_PROGRESS, REVIEW, DONE]
    LABELS = {
        TODO: "Pendiente",
        IN_PROGRESS: "En progreso",
        REVIEW: "En revision",
        DONE: "Completada",
    }

    @classmethod
    def choices(cls):
        return [(v, cls.LABELS[v]) for v in cls.ALL]


class Priority:
    LOW = "baja"
    MEDIUM = "media"
    HIGH = "alta"
    CRITICAL = "critica"

    ALL = [LOW, MEDIUM, HIGH, CRITICAL]
    LABELS = {LOW: "Baja", MEDIUM: "Media", HIGH: "Alta", CRITICAL: "Critica"}
    WEIGHT = {LOW: 1, MEDIUM: 2, HIGH: 3, CRITICAL: 4}

    @classmethod
    def choices(cls):
        return [(v, cls.LABELS[v]) for v in cls.ALL]
