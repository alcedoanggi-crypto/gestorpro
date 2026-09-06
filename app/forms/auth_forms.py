from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp

_pwd_rules = [
    DataRequired(),
    Length(min=8, message="Minimo 8 caracteres."),
    Regexp(r".*[A-Za-z].*", message="Debe incluir al menos una letra."),
    Regexp(r".*\d.*", message="Debe incluir al menos un numero."),
]


class LoginForm(FlaskForm):
    email = StringField("Correo", validators=[DataRequired(), Email()])
    password = PasswordField("Contrasena", validators=[DataRequired()])
    remember = BooleanField("Recordarme")
    submit = SubmitField("Iniciar sesion")


class RegisterForm(FlaskForm):
    name = StringField("Nombre completo", validators=[DataRequired(), Length(2, 120)])
    email = StringField("Correo", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Contrasena", validators=_pwd_rules)
    confirm = PasswordField(
        "Confirmar contrasena",
        validators=[DataRequired(), EqualTo("password", message="Las contrasenas no coinciden.")],
    )
    submit = SubmitField("Crear cuenta")


class ForgotPasswordForm(FlaskForm):
    email = StringField("Correo", validators=[DataRequired(), Email()])
    submit = SubmitField("Enviar enlace de recuperacion")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("Nueva contrasena", validators=_pwd_rules)
    confirm = PasswordField(
        "Confirmar contrasena",
        validators=[DataRequired(), EqualTo("password", message="Las contrasenas no coinciden.")],
    )
    submit = SubmitField("Restablecer contrasena")
