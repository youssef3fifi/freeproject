import mysql.connector
from datetime import datetime
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InvoiceModel:
    def __init__(self, db_config):
        self.db_config = db_config

    def create_invoice(self, invoice_data):
        """
        Create a new invoice with improved validation and error handling.
        Returns a tuple of (success, message, invoice_id)
        """
        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor(dictionary=True)

            # Start a transaction - important for data integrity
            connection.start_transaction()

            # Extract invoice data
            items = invoice_data.get('items', [])
            customer_name = invoice_data.get('customer_name', '')
            discount = float(invoice_data.get('discount', 0))
            discount_type = invoice_data.get('discount_type', 'amount')  # 'amount' or 'percentage'

            # Calculate subtotal
            subtotal = sum(item['price'] * item['quantity'] for item in items)

            # Calculate final total based on discount type
            if discount_type == 'percentage':
                if discount < 0 or discount > 100:
                    raise ValueError("Percentage discount must be between 0 and 100")
                total = subtotal * (1 - discount / 100)
            else:  # amount
                if discount < 0 or discount > subtotal:
                    raise ValueError("Amount discount cannot be negative or exceed the subtotal")
                total = subtotal - discount

            # Validate all items have sufficient stock BEFORE making any changes
            for item in items:
                cursor.execute("SELECT quantity, name FROM products WHERE id = %s", (item["product_id"],))
                result = cursor.fetchone()
                if not result:
                    raise ValueError(f"Product with ID {item['product_id']} does not exist")

                available_quantity = result['quantity']
                product_name = result['name']

                if item["quantity"] > available_quantity:
                    raise ValueError(
                        f"Insufficient stock for '{product_name}'. Available: {available_quantity}, Requested: {item['quantity']}")

            # Create the invoice
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO invoices (date, subtotal, discount, total, discount_type, customer_name) VALUES (%s, %s, %s, %s, %s, %s)",
                (current_time, subtotal, discount, total, discount_type, customer_name)
            )

            invoice_id = cursor.lastrowid

            # Add items to invoice_items and update product inventory
            for item in items:
                product_id = item["product_id"]
                quantity = item["quantity"]
                price = item["price"]

                # Add to invoice_items
                cursor.execute(
                    "INSERT INTO invoice_items (invoice_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                    (invoice_id, product_id, quantity, price)
                )

                # Update product inventory and sales stats
                cursor.execute(
                    "UPDATE products SET quantity = quantity - %s, sold = sold + %s WHERE id = %s",
                    (quantity, quantity, product_id)
                )

                # Verify the update was successful
                if cursor.rowcount == 0:
                    # This shouldn't happen if we validated correctly above, but just to be safe
                    connection.rollback()
                    return False, f"Failed to update inventory for product ID {product_id}", None

            # Commit the transaction if everything succeeded
            connection.commit()

            # Log successful invoice creation
            logger.info(f"Invoice #{invoice_id} created successfully at {current_time} by user: youssef3fifi")

            # Format items for the response
            formatted_items = []
            for item in items:
                cursor.execute("SELECT name FROM products WHERE id = %s", (item["product_id"],))
                product_name = cursor.fetchone()['name']
                formatted_items.append({
                    'product_id': item["product_id"],
                    'name': product_name,
                    'quantity': item["quantity"],
                    'price': item["price"]
                })

            # Prepare success message with invoice details
            invoice_details = {
                'invoice_id': invoice_id,
                'date': current_time,
                'items': formatted_items,
                'subtotal': subtotal,
                'discount': discount,
                'discount_type': discount_type,
                'total': total,
                'customer_name': customer_name
            }

            success_message = f"Invoice #{invoice_id} completed successfully"

            return True, success_message, invoice_details

        except ValueError as e:
            if connection:
                connection.rollback()
            logger.error(f"Validation error: {str(e)}")
            return False, str(e), None

        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Error creating invoice: {str(e)}")
            return False, f"Failed to complete invoice: {str(e)}", None

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    def get_invoice(self, invoice_id):
        """Get invoice details by ID"""
        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor(dictionary=True)

            # Get invoice header
            cursor.execute(
                "SELECT * FROM invoices WHERE id = %s",
                (invoice_id,)
            )
            invoice = cursor.fetchone()

            if not invoice:
                return False, f"Invoice #{invoice_id} not found", None

            # Get invoice items
            cursor.execute(
                """
                SELECT ii.*, p.name
                FROM invoice_items ii
                         JOIN products p ON ii.product_id = p.id
                WHERE invoice_id = %s
                """,
                (invoice_id,)
            )
            items = cursor.fetchall()

            invoice['items'] = items

            return True, "Invoice retrieved successfully", invoice

        except Exception as e:
            logger.error(f"Error retrieving invoice: {str(e)}")
            return False, f"Failed to retrieve invoice: {str(e)}", None

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    def get_all_invoices(self, limit=100, offset=0):
        """Get a list of all invoices with pagination"""
        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor(dictionary=True)

            # Get invoice headers
            cursor.execute(
                "SELECT * FROM invoices ORDER BY date DESC LIMIT %s OFFSET %s",
                (limit, offset)
            )
            invoices = cursor.fetchall()

            # Get total count for pagination
            cursor.execute("SELECT COUNT(*) as total FROM invoices")
            total = cursor.fetchone()['total']

            return True, "Invoices retrieved successfully", {
                'invoices': invoices,
                'total': total,
                'limit': limit,
                'offset': offset
            }

        except Exception as e:
            logger.error(f"Error retrieving invoices: {str(e)}")
            return False, f"Failed to retrieve invoices: {str(e)}", None

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()