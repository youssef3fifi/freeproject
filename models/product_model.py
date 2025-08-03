# models/product_model.py
from database.db_connection import create_connection

def add_product(name, quantity, price):
    conn = create_connection()
    cursor = conn.cursor()
    
    # Ensure the "sold" column exists or default it to zero
    sql = "INSERT INTO products (name, quantity, price, sold) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (name, quantity, price, 0))
    
    conn.commit()
    conn.close()

def get_all_products():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return products

def update_product_quantity(product_id, sold_quantity):
    conn = create_connection()
    cursor = conn.cursor()

    # First, fetch the current quantity
    cursor.execute("SELECT quantity FROM products WHERE id = %s", (product_id,))
    result = cursor.fetchone()

    if result is None:
        conn.close()
        raise ValueError("Product not found")

    current_quantity = result[0]

    if sold_quantity > current_quantity:
        conn.close()
        raise ValueError("Sold quantity exceeds available stock")

    # Update quantity and sold count
    cursor.execute("""
        UPDATE products 
        SET quantity = quantity - %s,
            sold = sold + %s
        WHERE id = %s
    """, (sold_quantity, sold_quantity, product_id))
    
    conn.commit()
    conn.close()
