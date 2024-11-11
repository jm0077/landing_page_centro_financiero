# app/auth/routes.py
from . import auth
from flask import render_template, redirect, url_for, flash, current_app, request
from .forms import RegistrationForm
from .keycloak_admin import KeycloakAdminClient
import logging

logger = logging.getLogger(__name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            keycloak_admin = KeycloakAdminClient(
                server_url=current_app.config['KEYCLOAK_SERVER_URL'],
                realm_name=current_app.config['KEYCLOAK_REALM_NAME'],
                client_id=current_app.config['KEYCLOAK_CLIENT_ID'],
                client_secret=current_app.config['KEYCLOAK_CLIENT_SECRET'],
                token_uri=current_app.config['KEYCLOAK_TOKEN_URI'],
                gcs_bucket_name=current_app.config['GCS_BUCKET_NAME']
            )
            
            success, message = keycloak_admin.create_user(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data
            )
            
            if success:
                return redirect(url_for('auth.register_success'))
            else:
                flash(f'Error en el registro: {message}', 'danger')
                logger.error(f"Registration failed: {message}")
        except Exception as e:
            flash(f'Ocurrió un error inesperado: {str(e)}', 'danger')
            logger.exception("Unexpected error during registration")
                
    return render_template('register.html', form=form)

@auth.route('/register/success')
def register_success():
    return render_template('register_success.html')