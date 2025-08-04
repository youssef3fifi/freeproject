# models/invoice_model.py
import mysql.connector
from database.db_connection import create_connection
from decimal import Decimal
from datetime import datetime

class InvoiceModel:
    @staticmethod
    def create_invoice_with_items(items, discount_value=0, discount_type='fixed', customer_name='', customer_phone=''):
        """
        Create invoice with proper transaction handling and enhanced features
        
        Args:
            items: list of dicts, each with keys: product_id, quantity, price
            discount_value: float value for discount
            discount_type: 'fixed' or 'percentage'
            customer_name: string for customer name
            customer_phone: string for customer phone
        
        Returns:
            dict with invoice_id, subtotal, discount_amount, total
        """
        conn = create_connection()
        cursor = conn.cursor()
        
        try:
            # Start transaction
            conn.start_transaction()
            
            # 1. Calculate subtotal
            subtotal = sum(Decimal(str(item["quantity"])) * Decimal(str(item["price"])) for item in items)
            
            # 2. Calculate discount amount based on type
            if discount_type == 'percentage':
                discount_amount = subtotal * (Decimal(str(discount_value)) / 100)
            else:  # fixed
                discount_amount = Decimal(str(discount_value))
            
            # 3. Calculate total after discount
            total_after_discount = subtotal - discount_amount
            
            # 4. Validate stock availability first
            for item in items:
                cursor.execute("SELECT quantity FROM products WHERE id = %s", (item["product_id"],))
                result = cursor.fetchone()
                if not result:
                    raise ValueError(f"Product with ID {item['product_id']} not found")
                
                available_quantity = result[0]
                if item["quantity"] > available_quantity:
                    cursor.execute("SELECT name FROM products WHERE id = %s", (item["product_id"],))
                    product_name = cursor.fetchone()[0]
                    raise ValueError(f"Insufficient stock for {product_name}. Available: {available_quantity}, Requested: {item['quantity']}")
            
            # 5. Create invoice header with enhanced fields
            invoice_sql = """
                INSERT INTO invoices (discount, total_price, customer_name, customer_phone, discount_type, subtotal, created_at) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            # Check if columns exist, if not use basic insertion
            try:
                cursor.execute(invoice_sql, (
                    float(discount_amount), 
                    float(total_after_discount), 
                    customer_name, 
                    customer_phone, 
                    discount_type,
                    float(subtotal),
                    datetime.now()
                ))
            except mysql.connector.Error:
                # Fallback to basic insertion if extended columns don't exist
                cursor.execute(
                    "INSERT INTO invoices (discount, total_price, created_at) VALUES (%s, %s, %s)",
                    (float(discount_amount), float(total_after_discount), datetime.now())
                )
            
            invoice_id = cursor.lastrowid
            
            # 6. Insert invoice items
            for item in items:
                item_total = Decimal(str(item["quantity"])) * Decimal(str(item["price"]))
                cursor.execute(
                    "INSERT INTO invoice_items (invoice_id, product_id, quantity, unit_price, total_price) VALUES (%s, %s, %s, %s, %s)",
                    (invoice_id, item["product_id"], item["quantity"], float(item["price"]), float(item_total))
                )
                
                # 7. Update product inventory
                cursor.execute(
                    "UPDATE products SET quantity = quantity - %s, sold = sold + %s WHERE id = %s",
                    (item["quantity"], item["quantity"], item["product_id"])
                )
            
            # Commit transaction
            conn.commit()
            
            return {
                'invoice_id': invoice_id,
                'subtotal': float(subtotal),
                'discount_amount': float(discount_amount),
                'discount_type': discount_type,
                'total': float(total_after_discount),
                'customer_name': customer_name,
                'customer_phone': customer_phone
            }
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_invoice_details(invoice_id):
        """Get detailed invoice information including items"""
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Get invoice header
            cursor.execute("SELECT * FROM invoices WHERE id = %s", (invoice_id,))
            invoice = cursor.fetchone()
            
            if not invoice:
                return None
            
            # Get invoice items with product details
            cursor.execute("""
                SELECT ii.*, p.name as product_name 
                FROM invoice_items ii 
                JOIN products p ON ii.product_id = p.id 
                WHERE ii.invoice_id = %s
            """, (invoice_id,))
            items = cursor.fetchall()
            
            invoice['items'] = items
            return invoice
            
        except Exception as e:
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_all_invoices(limit=50):
        """Get list of all invoices with summary information"""
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Try to get invoices with extended fields first
            try:
                cursor.execute("""
                    SELECT id, customer_name, customer_phone, subtotal, discount, 
                           total_price, discount_type, created_at 
                    FROM invoices 
                    ORDER BY created_at DESC 
                    LIMIT %s
                """, (limit,))
            except mysql.connector.Error:
                # Fallback to basic fields if extended columns don't exist
                cursor.execute("""
                    SELECT id, discount, total_price, created_at 
                    FROM invoices 
                    ORDER BY created_at DESC 
                    LIMIT %s
                """, (limit,))
            
            return cursor.fetchall()
            
        except Exception as e:
            raise e
        finally:
            cursor.close()
            conn.close()

# Backward compatibility - keep the old function for existing code
def create_invoice_with_items(items, discount):
    """Legacy function for backward compatibility"""
    return InvoiceModel.create_invoice_with_items(items, discount, 'fixed')
