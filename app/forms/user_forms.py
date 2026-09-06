from flask_wtf import FlaskForm
from wtforms import (BooleanField, PasswordField, SelectField, StringField,
                     SubmitField)
from wtforms.validators import DataRequired, Email, Length, Optional


class UserForm(FlaskForm):
    name = StringField("Nombre completo", validators=[DataRequired(), Length(2, 120)])
    email = StringField("Correo", validators=[DataRequired(), Email(), Length(max=120)])
    job_title = StringField("Cargo", validators=[Optional(), Length(max=120)])
    role_id = SelectField("Rol", coerce=int, validators=[DataRequired()])
    is_active = BooleanField("Cuenta activa", default=True)
    password = PasswordField(
        "Contrasena", validators=[Optional(), Length(min=8, message="Minimo 8 caracteres.")]
    )
    submit = SubmitField("Guardar usuario")


class ProfileForm(FlaskForm):
    name = StringField("Nombre completo", validators=[DataRequired(), Length(2, 120)])
    job_title = StringField("Cargo", validators=[Optional(), Length(max=120)])
    avatar_url = StringField("URL de avatar", validators=[Optional(), Length(max=255)])
    current_password = PasswordField("Contrasena actual", validators=[Optional()])
    new_password = PasswordField("Nueva contrasena", validators=[Optional(), Length(min=8)])
    submit = SubmitField("Actualizar perfil")
