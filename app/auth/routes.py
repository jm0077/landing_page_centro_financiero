# app/auth/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from .forms import RegistrationForm
import requests
import logging

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Aquí iría la lógica para registrar al usuario en Keycloak
        # Por ahora, simularemos un registro exitoso
        flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.register_success'))
    return render_template('index.html', form=form)

@auth.route('/register_success')
def register_success():
    return render_template('register_success.html')

def register_user(username, email, password, first_name, last_name):
    # Esta función debería implementar la lógica real para registrar un usuario en Keycloak
    # Por ahora, solo simularemos un registro exitoso
    logging.info(f"Simulando registro de usuario: {username}")
    return True, "Usuario registrado correctamente"