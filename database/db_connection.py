import mysql.connector
import logging

# إعداد السجل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_connection():
    """إنشاء اتصال بقاعدة البيانات"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="0000",  # عدلها حسب كلمة المرور لديك
            database="sharp_db"
            
        )
        return connection
    except Exception as e:
        logger.error(f"خطأ في الاتصال بقاعدة البيانات: {str(e)}")
        raise