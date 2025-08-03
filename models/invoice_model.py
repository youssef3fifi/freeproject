# models/invoice_model.py
import mysql.connector
from database.db_connection import create_connection

def create_invoice_with_items(items, discount):
    """
    items: list of dicts, each with keys: product_id, quantity, price
    discount: float value to be applied on total
    """
    conn = create_connection()
    cursor = conn.cursor()

    try:
        # 1. حساب إجمالي السعر بدون الخصم
        subtotal = sum(item["quantity"] * item["price"] for item in items)
        total_after_discount = subtotal - discount

        # 2. إنشاء الفاتورة
        cursor.execute(
        "INSERT INTO invoice_items (invoice_id, product_id, quantity, unit_price, total_price) VALUES (%s, %s, %s, %s, %s)",
(
        invoice_id,
        item["product_id"],
        item["quantity"],
        item["price"],
        item["quantity"] * item["price"]
)
)
        invoice_id = cursor.lastrowid

        # 3. إدخال كل منتج في جدول invoice_items
        for item in items:
            cursor.execute(
                "INSERT INTO invoice_items (invoice_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                (invoice_id, item["product_id"], item["quantity"], item["price"])
            )

            # 4. تحديث المخزون
            cursor.execute(
                "UPDATE products SET quantity = quantity - %s, sold = sold + %s WHERE id = %s",
                (item["quantity"], item["quantity"], item["product_id"])
            )

        conn.commit()
        return invoice_id  # ممكن نطبعها لاحقًا

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()
