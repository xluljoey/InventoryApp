import sqlite3
from db.database import get_db_connection

def get_all_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, category, unit, weight_per_unit, price, current_stock, low_stock_threshold, batch_number, expiry_date, cost_price FROM products")
    res = cursor.fetchall()
    conn.close()
    return res

def get_low_stock_products():
    """Get products that are below their low stock threshold"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, category, unit, weight_per_unit, price, current_stock, 
               low_stock_threshold, batch_number, expiry_date
        FROM products
        WHERE (current_stock / NULLIF(weight_per_unit, 0)) <= COALESCE(low_stock_threshold, 5.0)
        ORDER BY (current_stock / NULLIF(weight_per_unit, 0)) ASC
    """)
    res = cursor.fetchall()
    conn.close()
    return res

def get_expiring_products(days_ahead=30):
    """Get products expiring within specified days (not yet expired)"""
    from datetime import datetime, timedelta
    conn = get_db_connection()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cutoff_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT id, name, category, expiry_date, current_stock, weight_per_unit, batch_number
        FROM products
        WHERE expiry_date IS NOT NULL AND expiry_date > ? AND expiry_date <= ?
        ORDER BY expiry_date ASC
    """, (today, cutoff_date))
    res = cursor.fetchall()
    conn.close()
    return res

def get_expired_products():
    """Get products that have already expired"""
    from datetime import datetime
    conn = get_db_connection()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT id, name, category, expiry_date, current_stock, weight_per_unit, batch_number
        FROM products
        WHERE expiry_date IS NOT NULL AND expiry_date < ?
        ORDER BY expiry_date ASC
    """, (today,))
    res = cursor.fetchall()
    conn.close()
    return res

def get_product_names():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM products")
    res = cursor.fetchall()
    conn.close()
    return res

def get_all_customers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, phone, balance FROM customers")
    res = cursor.fetchall()
    conn.close()
    return res

def add_customer(name, phone):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO customers (name, phone) VALUES (?, ?)", (name, phone))
    conn.commit()
    conn.close()

def add_product(name, category, unit, weight_per_unit, price, current_stock, low_stock_threshold=5.0, batch_number=None, expiry_date=None, cost_price=None):
    """Add a new product to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (name, category, unit, weight_per_unit, price, current_stock, low_stock_threshold, batch_number, expiry_date, cost_price)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, category, unit, weight_per_unit, price, current_stock * weight_per_unit, low_stock_threshold, batch_number, expiry_date, cost_price))
    conn.commit()
    conn.close()

def get_restock_report():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.id, p.name, r.old_qty, r.added_qty, r.new_qty, r.date 
        FROM restock_history r 
        JOIN products p ON r.product_id = p.id 
        ORDER BY r.date DESC
    """)
    res = cursor.fetchall()
    conn.close()
    return res

# --- ADMIN FUNCTIONS ---
def admin_add_product(name, price, weight, bags):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, price, weight_per_unit, current_stock) VALUES (?,?,?,?)",
                   (name, price, weight, bags * weight))
    conn.commit()
    conn.close()

def admin_update_price(p_id, price):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET price = ? WHERE id = ?", (price, p_id))
    conn.commit()
    conn.close()

def admin_overwrite_stock(p_id, bags):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT weight_per_unit, current_stock FROM products WHERE id = ?", (p_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
    weight, old_stock_kg = row[0], row[1]
    new_stock_kg = bags * weight
    
    # Update stock
    cursor.execute("UPDATE products SET current_stock = ? WHERE id = ?", (new_stock_kg, p_id))
    
    # Log the change for Reports
    cursor.execute("INSERT INTO restock_history (product_id, old_qty, added_qty, new_qty) VALUES (?,?,?,?)",
                   (p_id, old_stock_kg/weight, bags - (old_stock_kg/weight), bags))
    conn.commit()
    conn.close()
    return True

def admin_delete_product(p_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (p_id, ))
    conn.commit()
    conn.close()

def restock_product(p_id, bags):
    """Add bags to stock and log the change."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT weight_per_unit, current_stock FROM products WHERE id = ?", (p_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
    weight, old_stock_kg = row[0], row[1]
    old_bags = old_stock_kg / weight if weight > 0 else 0
    new_bags = old_bags + bags
    new_stock_kg = new_bags * weight
    
    # Update stock
    cursor.execute("UPDATE products SET current_stock = ? WHERE id = ?", (new_stock_kg, p_id))
    
    # Log the change for Reports
    cursor.execute("INSERT INTO restock_history (product_id, old_qty, added_qty, new_qty) VALUES (?,?,?,?)",
                   (p_id, old_bags, bags, new_bags))
    conn.commit()
    conn.close()
    return True