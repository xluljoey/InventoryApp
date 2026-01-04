from db.database import get_db_connection

def get_today_revenue():
    """Calculates total revenue from sales made today."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Sums the total_price for all sales made today
        cursor.execute("""
            SELECT SUM(total_price) FROM sales 
            WHERE date(date) = date('now', 'localtime')
        """)
        result = cursor.fetchone()
        return result[0] if result[0] is not None else 0.0
    except Exception as e:
        print(f"Error calculating revenue: {e}")
        return 0.0
    finally:
        conn.close()

def sell_product(product_id, quantity_bags, unit, customer_id, amount_paid):
    """Processes a sale: reduces stock and records the transaction."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 1. Get product details (price and weight to convert bags to KG)
        cursor.execute("SELECT price, weight_per_unit, current_stock FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        
        if not product:
            return False
            
        price_per_bag = product[0]
        weight_per_bag = product[1]
        current_stock_kg = product[2]
        
        total_price = quantity_bags * price_per_bag
        qty_kg = quantity_bags * weight_per_bag
        
        # 2. Check if enough stock exists
        if current_stock_kg < qty_kg:
            return False
            
        # 3. Deduct stock
        cursor.execute("UPDATE products SET current_stock = current_stock - ? WHERE id = ?", (qty_kg, product_id))
        
        # 4. Record the sale
        cursor.execute("""
            INSERT INTO sales (product_id, customer_id, quantity, total_price, amount_paid)
            VALUES (?, ?, ?, ?, ?)
        """, (product_id, customer_id, quantity_bags, total_price, amount_paid))
        
        # 5. Update customer debt if they didn't pay in full
        if customer_id and amount_paid < total_price:
            debt = total_price - amount_paid
            cursor.execute("UPDATE customers SET balance = balance + ? WHERE id = ?", (debt, customer_id))
            
        conn.commit()
        return True
    except Exception as e:
        print(f"Sale Error: {e}")
        return False
    finally:
        conn.close()

def get_sales_history():
    """Fetches all sales for the Reports window."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.id, p.name, c.name, s.quantity, s.total_price, s.date 
        FROM sales s
        JOIN products p ON s.product_id = p.id
        LEFT JOIN customers c ON s.customer_id = c.id
        ORDER BY s.date DESC
    """)
    data = cursor.fetchall()
    conn.close()
    return data