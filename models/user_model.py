import mysql.connector
import hashlib
import logging
from database.db_connection import connect

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username, password):
    """Verify user credentials"""
    try:
        # Get DB configuration
        db_config = connect()
        
        # Hash the password
        hashed_password = hash_password(password)
        
        # Connect to database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # Execute query to find the user
        cursor.execute(
            "SELECT * FROM users WHERE username = %s AND password = %s",
            (username, hashed_password)
        )
        
        # Get the user
        user = cursor.fetchone()
        
        # Close resources
        cursor.close()
        connection.close()
        
        # Return result
        if user:
            logger.info(f"User {username} logged in successfully")
            return True, user
        else:
            logger.warning(f"Failed login attempt for username {username}")
            return False, None
            
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return False, None