# app/database/db_operations.py
from flask import current_app
from .. import db
import logging
from sqlalchemy.sql import text

logger = logging.getLogger(__name__)

def insert_user_in_bank(user_id):
    try:
        with db.engine.connect() as connection:
            query = text("CALL insertar_usuario_banco(:user_id)")
            result = connection.execute(query, {"user_id": user_id})
            connection.commit()
            logger.info(f"Stored procedure executed successfully for user_id: {user_id}")
            return True
    except Exception as e:
        logger.error(f"Error executing stored procedure: {str(e)}")
        return False