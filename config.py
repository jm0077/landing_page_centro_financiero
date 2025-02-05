# config.py
import os
import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load the OIDC client secrets
with open('client_secrets.json') as f:
    client_secrets = json.load(f)

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'you-will-never-guess')
    KEYCLOAK_SERVER_URL = client_secrets['web']['issuer'].rstrip('/realms/master')
    KEYCLOAK_REALM_NAME = 'master'
    KEYCLOAK_CLIENT_ID = client_secrets['web']['client_id']
    KEYCLOAK_CLIENT_SECRET = client_secrets['web']['client_secret']
    KEYCLOAK_REDIRECT_URI = client_secrets['web']['redirect_uris'][0]
    KEYCLOAK_TOKEN_URI = client_secrets['web']['token_uri']
    GCS_BUCKET_NAME = 'account-statements_customers'
    
    # Database configuration
    DB_USER = 'jm_07'
    DB_PASS = '12345'
    DB_NAME = 'dashboard_db'
    CLOUD_SQL_CONNECTION_NAME = 'northern-hope-449920-t0:southamerica-west1:my-mysql-instance'
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASS}@/{DB_NAME}?unix_socket=/cloudsql/{CLOUD_SQL_CONNECTION_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    logger.debug(f"KEYCLOAK_SERVER_URL: {KEYCLOAK_SERVER_URL}")
    logger.debug(f"KEYCLOAK_REALM_NAME: {KEYCLOAK_REALM_NAME}")
    logger.debug(f"KEYCLOAK_CLIENT_ID: {KEYCLOAK_CLIENT_ID}")
    logger.debug(f"KEYCLOAK_REDIRECT_URI: {KEYCLOAK_REDIRECT_URI}")
    logger.debug(f"KEYCLOAK_TOKEN_URI: {KEYCLOAK_TOKEN_URI}")
    logger.debug(f"GCS_BUCKET_NAME: {GCS_BUCKET_NAME}")
    logger.debug(f"SQLALCHEMY_DATABASE_URI: {SQLALCHEMY_DATABASE_URI}")