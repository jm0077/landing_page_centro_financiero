# app/auth/keycloak_admin.py
from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakGetError
import requests
import json
import logging
from google.cloud import storage
from ..database.db_operations import insert_user_in_bank

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class KeycloakAdminClient:
    def __init__(self, server_url, realm_name, client_id, client_secret, token_uri, gcs_bucket_name):
        self.server_url = server_url
        self.realm_name = realm_name
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_uri = token_uri
        self.keycloak_admin = None
        self.gcs_bucket_name = gcs_bucket_name
        self.gcs_client = storage.Client()

    def _get_admin_token(self):
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        logger.debug(f"Attempting to get admin token from URL: {self.token_uri}")
        logger.debug(f"Request data: {data}")
        try:
            response = requests.post(self.token_uri, data=data)
            logger.debug(f"Response status code: {response.status_code}")
            logger.debug(f"Response content: {response.text}")
            
            if response.status_code == 200:
                try:
                    token_data = response.json()
                    logger.debug(f"Token data: {json.dumps(token_data, indent=2)}")
                    return token_data  # Return the entire token data dictionary
                except json.JSONDecodeError:
                    raise Exception(f"Failed to decode JSON response: {response.text}")
            else:
                raise Exception(f"Failed to get admin token: {response.status_code} - {response.text}")
        except requests.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise

    def _init_admin(self):
        if not self.keycloak_admin:
            token_data = self._get_admin_token()
            self.keycloak_admin = KeycloakAdmin(
                server_url=self.server_url,
                realm_name=self.realm_name,
                token=token_data
            )

    def _parse_error_message(self, error_str):
        """Traduce y formatea los mensajes de error comunes de Keycloak"""
        error_mappings = {
            "User exists with same username": "Ya existe un usuario con ese nombre de usuario",
            "User exists with same email": "Ya existe un usuario con ese correo electrónico",
            "Invalid username": "El nombre de usuario no es válido",
            "Invalid email": "El correo electrónico no es válido",
            "Password policy not met": "La contraseña no cumple con los requisitos de seguridad",
            "Username contains invalid characters": "El nombre de usuario contiene caracteres no válidos"
        }
        
        # Intenta extraer el mensaje de error del JSON si es posible
        try:
            error_dict = json.loads(error_str)
            original_message = error_dict.get('errorMessage', '')
            return error_mappings.get(original_message, original_message)
        except:
            # Si no es JSON, busca coincidencias directas
            for eng, esp in error_mappings.items():
                if eng in error_str:
                    return esp
            return "Error en el registro: " + error_str
            
    def create_user(self, username, email, password, first_name, last_name):
        try:
            self._init_admin()
            new_user = self.keycloak_admin.create_user({
                "username": username,
                "email": email,
                "firstName": first_name,
                "lastName": last_name,
                "enabled": True,
                "credentials": [{
                    "type": "password",
                    "value": password,
                    "temporary": False
                }]
            })
            logger.debug(f"New user created: {new_user}")
            
            # Get the user ID from Keycloak
            user_id = self.keycloak_admin.get_user_id(username)
            
            # Create a folder in Google Cloud Storage
            self.create_gcs_folder(user_id)
            
            # Insert user in bank database
            if insert_user_in_bank(user_id):
                logger.info(f"Usuario {user_id} registrado exitosamente en la base de datos")
            else:
                logger.error(f"Error al insertar usuario {user_id} en la base de datos")
            
            return True, "Usuario creado exitosamente"
        except KeycloakGetError as e:
            error_msg = self._parse_error_message(str(e))
            logger.error(f"Error de Keycloak: {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = self._parse_error_message(str(e))
            logger.error(f"Error inesperado: {error_msg}", exc_info=True)
            return False, error_msg

    def create_gcs_folder(self, folder_name):
        try:
            bucket = self.gcs_client.get_bucket(self.gcs_bucket_name)
            blob = bucket.blob(f"{folder_name}/")
            blob.upload_from_string('')
            logger.debug(f"Created GCS folder: {folder_name}")
        except Exception as e:
            logger.error(f"Error creating GCS folder: {str(e)}", exc_info=True)
            raise