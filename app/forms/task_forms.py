from flask_wtf import FlaskForm
from wtforms import (DateField, DecimalField, IntegerField, SelectField,
                     SelectMultipleField, StringField, SubmitField, TextAreaField)
from wtforms.validators import (DataRequired, Length, NumberRange, Optional,
                                ValidationError)

from ..models.enums import TaskStatus, Priority


class TaskForm(FlaskForm):
    title = StringField("Titulo", validators=[DataRequired(), Length(2, 200)])
    description = TextAreaField("Descripcion", validators=[Optional(), Length(max=4000)])
    project_id = SelectField("Proyecto", coerce=int, validators=[DataRequired()])
    assignee_id = SelectField("Responsable", coerce=int, validators=[Optional()])
    status = SelectField("Estado", choices=TaskStatus.choices(), validators=[DataRequired()])
    priority = SelectField("Prioridad", choices=Priority.choices(), validators=[DataRequired()])
    progress = IntegerField("% Avance", default=0, validators=[Optional(), NumberRange(0, 100)])
    estimated_hours = DecimalField("Horas estimadas", places=1, validators=[Optional(), NumberRange(min=0)])
    start_date = DateField("Fecha de inicio", validators=[Optional()])
    due_date = DateField("Fecha de vencimiento", validators=[Optional()])
    dependencies = SelectMultipleField("Depende de", coerce=int, validators=[Optional()])
    submit = SubmitField("Guardar tarea")

    def validate_due_date(self, field):
        if field.data and self.start_date.data and field.data < self.start_date.data:
            raise ValidationError("El vencimiento no puede ser anterior al inicio.")


class QuickCommentForm(FlaskForm):
    body = TextAreaField("Comentario", validators=[DataRequired(), Length(1, 2000)])
    submit = SubmitField("Comentar")
