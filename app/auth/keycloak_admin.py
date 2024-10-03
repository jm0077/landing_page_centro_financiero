# app/auth/keycloak_admin.py
from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakGetError
import requests
import json
import logging
from google.cloud import storage

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
            
            return True, "User created successfully and GCS folder created"
        except KeycloakGetError as e:
            logger.error(f"Keycloak error: {str(e)}")
            return False, f"Keycloak error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return False, f"Unexpected error: {str(e)}"

    def create_gcs_folder(self, folder_name):
        try:
            bucket = self.gcs_client.get_bucket(self.gcs_bucket_name)
            blob = bucket.blob(f"{folder_name}/")
            blob.upload_from_string('')
            logger.debug(f"Created GCS folder: {folder_name}")
        except Exception as e:
            logger.error(f"Error creating GCS folder: {str(e)}", exc_info=True)
            raise