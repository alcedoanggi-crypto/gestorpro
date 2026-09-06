from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class TeamForm(FlaskForm):
    name = StringField("Nombre del equipo", validators=[DataRequired(), Length(2, 120)])
    description = TextAreaField("Descripcion", validators=[Optional(), Length(max=2000)])
    member_ids = SelectMultipleField("Integrantes", coerce=int, validators=[Optional()])
    submit = SubmitField("Guardar equipo")
