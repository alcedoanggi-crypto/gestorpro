from flask_wtf import FlaskForm
from wtforms import (DateField, SelectField, StringField, SubmitField, TextAreaField)
from wtforms.validators import DataRequired, Length, Optional, ValidationError

from ..models.enums import ProjectStatus, Priority


class ProjectForm(FlaskForm):
    name = StringField("Nombre del proyecto", validators=[DataRequired(), Length(2, 150)])
    description = TextAreaField("Descripcion", validators=[Optional(), Length(max=4000)])
    status = SelectField("Estado", choices=ProjectStatus.choices(), validators=[DataRequired()])
    priority = SelectField("Prioridad", choices=Priority.choices(), validators=[DataRequired()])
    start_date = DateField("Fecha de inicio", validators=[Optional()])
    end_date = DateField("Fecha de fin", validators=[Optional()])
    manager_id = SelectField("Gerente responsable", coerce=int, validators=[Optional()])
    team_id = SelectField("Equipo", coerce=int, validators=[Optional()])
    submit = SubmitField("Guardar proyecto")

    def validate_end_date(self, field):
        if field.data and self.start_date.data and field.data < self.start_date.data:
            raise ValidationError("La fecha de fin no puede ser anterior a la de inicio.")
