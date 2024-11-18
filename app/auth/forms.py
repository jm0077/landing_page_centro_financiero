# app/auth/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
import re

class RegistrationForm(FlaskForm):
    username = StringField('Usuario', validators=[
        DataRequired(message="El nombre de usuario es obligatorio"),
        Length(min=4, max=20, message="El nombre de usuario debe tener entre 4 y 20 caracteres")
    ])
    email = StringField('Correo electrónico', validators=[
        DataRequired(message="El correo electrónico es obligatorio"),
        Email(message="Por favor, introduce una dirección de correo válida")
    ])
    first_name = StringField('Nombre', validators=[
        DataRequired(message="El nombre es obligatorio")
    ])
    last_name = StringField('Apellido', validators=[
        DataRequired(message="El apellido es obligatorio")
    ])
    dni = StringField('DNI', validators=[
        DataRequired(message="El DNI es obligatorio"),
        Length(min=8, max=8, message="El DNI debe tener exactamente 8 dígitos")
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message="La contraseña es obligatoria"),
        Length(min=6, message="La contraseña debe tener al menos 6 caracteres")
    ])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(message="Por favor, confirma tu contraseña"),
        EqualTo('password', message="Las contraseñas deben coincidir")
    ])
    submit = SubmitField('Registrarse')

    def validate_password(self, field):
        if not re.search(r'[A-Z]', field.data):
            raise ValidationError("La contraseña debe contener al menos una letra mayúscula")
        if not re.search(r'[a-z]', field.data):
            raise ValidationError("La contraseña debe contener al menos una letra minúscula")
        if not re.search(r'\d', field.data):
            raise ValidationError("La contraseña debe contener al menos un número")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', field.data):
            raise ValidationError("La contraseña debe contener al menos un carácter especial")

    def validate_dni(self, field):
        if len(field.data) != 8 or not field.data.isdigit():
            raise ValidationError("El DNI debe tener exactamente 8 dígitos")