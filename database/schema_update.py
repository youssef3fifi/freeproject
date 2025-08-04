# database/schema_update.py
import mysql.connector
from database.db_connection import create_connection

def update_invoice_schema():
    """Update the invoices table to support enhanced features"""
    conn = create_connection()
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("DESCRIBE invoices")
        columns = [row[0] for row in cursor.fetchall()]
        
        # Add customer_name column if it doesn't exist
        if 'customer_name' not in columns:
            cursor.execute("ALTER TABLE invoices ADD COLUMN customer_name VARCHAR(255) DEFAULT ''")
            print("Added customer_name column")
        
        # Add customer_phone column if it doesn't exist
        if 'customer_phone' not in columns:
            cursor.execute("ALTER TABLE invoices ADD COLUMN customer_phone VARCHAR(50) DEFAULT ''")
            print("Added customer_phone column")
        
        # Add discount_type column if it doesn't exist
        if 'discount_type' not in columns:
            cursor.execute("ALTER TABLE invoices ADD COLUMN discount_type ENUM('fixed', 'percentage') DEFAULT 'fixed'")
            print("Added discount_type column")
        
        # Add subtotal column if it doesn't exist
        if 'subtotal' not in columns:
            cursor.execute("ALTER TABLE invoices ADD COLUMN subtotal FLOAT DEFAULT 0")
            print("Added subtotal column")
        
        conn.commit()
        print("Invoice schema updated successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"Error updating schema: {e}")
        raise e
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    try:
        update_invoice_schema()
    except Exception as e:
        print(f"Failed to update schema: {e}")