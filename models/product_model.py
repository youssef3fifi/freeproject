import mysql.connector
import logging
from database.db_connection import connect


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductModel:
    def __init__(self, db_config):
        self.db_config = db_config
    
    def get_all_products(self):
        """Get all products from the database"""
        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute(
                """
                SELECT id, name, price, quantity, sold, created_at, updated_at
                FROM products
                ORDER BY name
                """
            )
            
            products = cursor.fetchall()
            
            return True, "Products retrieved successfully", products
            
        except Exception as e:
            logger.error(f"Error retrieving products: {str(e)}")
            return False, f"Failed to retrieve products: {str(e)}", None
            
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    
    def get_product(self, product_id):
        """Get a product by ID"""
        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute(
                """
                SELECT id, name, price, quantity, sold, created_at, updated_at
                FROM products
                WHERE id = %s
                """,
                (product_id,)
            )
            
            product = cursor.fetchone()
            
            if not product:
                return False, f"Product with ID {product_id} not found", None
            
            return True, "Product retrieved successfully", product
            
        except Exception as e:
            logger.error(f"Error retrieving product: {str(e)}")
            return False, f"Failed to retrieve product: {str(e)}", None
            
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    
    def add_product(self, product_data):
        """Add a new product"""
        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor()
            
            # Validate product data
            if not product_data.get("name"):
                return False, "Product name is required"
            
            if not product_data.get("price") or float(product_data["price"]) <= 0:
                return False, "Product price must be greater than 0"
            
            if "quantity" not in product_data or int(product_data["quantity"]) < 0:
                return False, "Product quantity cannot be negative"
            
            # Check if product with the same name already exists
            cursor.execute(
                "SELECT id FROM products WHERE name = %s",
                (product_data["name"],)
            )
            
            if cursor.fetchone():
                return False, f"A product with the name '{product_data['name']}' already exists"
            
            # Insert the product
            cursor.execute(
                """
                INSERT INTO products (name, price, quantity, sold)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    product_data["name"],
                    product_data["price"],
                    product_data.get("quantity", 0),
                    0  # Initial sold count is 0
                )
            )
            
            connection.commit()
            product_id = cursor.lastrowid
            
            logger.info(f"Product {product_id} ({product_data['name']}) added successfully by user: youssef3fifi")
            
            return True, f"Product '{product_data['name']}' added successfully"
            
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Error adding product: {str(e)}")
            return False, f"Failed to add product: {str(e)}"
            
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    
    def update_product(self, product_data):
        """Update an existing product"""
        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor()
            
            # Validate product data
            if not product_data.get("id"):
                return False, "Product ID is required for update"
            
            if not product_data.get("name"):
                return False, "Product name is required"
            
            if not product_data.get("price") or float(product_data["price"]) <= 0:
                return False, "Product price must be greater than 0"
            
            if "quantity" not in product_data or int(product_data["quantity"]) < 0:
                return False, "Product quantity cannot be negative"
            
            # Check if product exists
            cursor.execute(
                "SELECT id FROM products WHERE id = %s",
                (product_data["id"],)
            )
            
            if not cursor.fetchone():
                return False, f"Product with ID {product_data['id']} not found"
            
            # Check if name is already used by another product
            cursor.execute(
                "SELECT id FROM products WHERE name = %s AND id != %s",
                (product_data["name"], product_data["id"])
            )
            
            if cursor.fetchone():
                return False, f"Another product with the name '{product_data['name']}' already exists"
            
            # Update the product
            cursor.execute(
                """
                UPDATE products
                SET name = %s, price = %s, quantity = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (
                    product_data["name"],
                    product_data["price"],
                    product_data["quantity"],
                    product_data["id"]
                )
            )
            
            connection.commit()
            
            logger.info(f"Product {product_data['id']} ({product_data['name']}) updated successfully by user: youssef3fifi")
            
            return True, f"Product '{product_data['name']}' updated successfully"
            
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Error updating product: {str(e)}")
            return False, f"Failed to update product: {str(e)}"
            
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    
    def delete_product(self, product_id):
        """Delete a product"""
        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor()
            
            # Check if product exists
            cursor.execute(
                "SELECT id, name FROM products WHERE id = %s",
                (product_id,)
            )
            
            product = cursor.fetchone()
            if not product:
                return False, f"Product with ID {product_id} not found"
            
            product_name = product[1]
            
            # Check if product is used in any invoice
            cursor.execute(
                "SELECT COUNT(*) FROM invoice_items WHERE product_id = %s",
                (product_id,)
            )
            
            invoice_count = cursor.fetchone()[0]
            if invoice_count > 0:
                return False, f"Cannot delete product '{product_name}' as it is used in {invoice_count} invoice(s)"
            
            # Delete the product
            cursor.execute(
                "DELETE FROM products WHERE id = %s",
                (product_id,)
            )
            
            connection.commit()
            
            logger.info(f"Product {product_id} ({product_name}) deleted successfully by user: youssef3fifi")
            
            return True, f"Product '{product_name}' deleted successfully"
            
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Error deleting product: {str(e)}")
            return False, f"Failed to delete product: {str(e)}"
            
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    
    def get_low_stock_products(self, threshold=5):
        """Get products with low stock"""
        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute(
                """
                SELECT id, name, price, quantity, sold, created_at, updated_at
                FROM products
                WHERE quantity <= %s
                ORDER BY quantity ASC
                """,
                (threshold,)
            )
            
            products = cursor.fetchall()
            
            return True, "Low stock products retrieved successfully", products
            
        except Exception as e:
            logger.error(f"Error retrieving low stock products: {str(e)}")
            return False, f"Failed to retrieve low stock products: {str(e)}", None
            
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    
    def get_top_selling_products(self, limit=10):
        """Get top selling products"""
        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute(
                """
                SELECT id, name, price, quantity, sold, created_at, updated_at
                FROM products
                ORDER BY sold DESC
                LIMIT %s
                """,
                (limit,)
            )
            
            products = cursor.fetchall()
            
            return True, "Top selling products retrieved successfully", products
            
        except Exception as e:
            logger.error(f"Error retrieving top selling products: {str(e)}")
            return False, f"Failed to retrieve top selling products: {str(e)}", None
            
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()