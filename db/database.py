import sqlite3
import hashlib
import os

DB_PATH = "inventory.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    # Optimize SQLite for faster performance
    conn.execute("PRAGMA journal_mode=WAL")  # Better concurrency
    conn.execute("PRAGMA synchronous=NORMAL")  # Faster writes
    conn.execute("PRAGMA cache_size=10000")  # Larger cache
    conn.execute("PRAGMA temp_store=memory")  # Use memory for temp tables
    return conn

def hash_password(password):
    """Hash password with SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT DEFAULT 'General',
        unit TEXT DEFAULT 'Bags',
        weight_per_unit REAL DEFAULT 50.0,
        price REAL NOT NULL,
        current_stock REAL DEFAULT 0.0,
        low_stock_threshold REAL DEFAULT 5.0,
        batch_number TEXT,
        expiry_date TEXT,
        cost_price REAL
    )""")
    
    # Add new columns to existing tables if they don't exist (for migration)
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN low_stock_threshold REAL DEFAULT 5.0")
    except:
        pass  # Column already exists
    
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN batch_number TEXT")
    except:
        pass  # Column already exists
    
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN expiry_date TEXT")
    except:
        pass  # Column already exists
    
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN cost_price REAL")
    except:
        pass  # Column already exists
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        balance REAL DEFAULT 0.0
    )""")
    
    # Sales table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        customer_id INTEGER,
        quantity REAL,
        total_price REAL,
        amount_paid REAL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    
    # Restock history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS restock_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        old_qty REAL,
        added_qty REAL,
        new_qty REAL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    
    # Admin settings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin_settings (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        password_hash TEXT NOT NULL,
        reset_code TEXT,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    
    # Payment history table for tracking customer debt payments (consolidated)
    # Remove the duplicate table creation and keep only one with proper structure
    try:
        # Check if the table exists with the right structure
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='payment_history'")
        result = cursor.fetchone()
        if not result:
            # Create the table if it doesn't exist
            cursor.execute("""
            CREATE TABLE payment_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                previous_balance REAL NOT NULL,
                new_balance REAL NOT NULL,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )""")
    except:
        # Fallback: create table if checking fails
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS payment_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            previous_balance REAL NOT NULL,
            new_balance REAL NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )""")
    
    # Initialize with default password "SALES2025!" if not exists
    cursor.execute("SELECT COUNT(*) FROM admin_settings")
    if cursor.fetchone()[0] == 0:
        default_password = hash_password("SALES2025!")
        cursor.execute("INSERT INTO admin_settings (id, password_hash) VALUES (1, ?)", (default_password,))
    
    conn.commit()
    conn.close()

def verify_admin_password(password):
    """Verify admin password"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM admin_settings WHERE id = 1")
    result = cursor.fetchone()
    conn.close()
    
    if result:
        stored_hash = result[0]
        return hash_password(password) == stored_hash
    return False

def change_admin_password(old_password, new_password):
    """Change admin password"""
    if not verify_admin_password(old_password):
        return False, "Current password is incorrect"
    
    if len(new_password) < 4:
        return False, "New password must be at least 4 characters"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    new_hash = hash_password(new_password)
    cursor.execute("""
        UPDATE admin_settings 
        SET password_hash = ?, last_updated = CURRENT_TIMESTAMP 
        WHERE id = 1
    """, (new_hash,))
    conn.commit()
    conn.close()
    
    return True, "Password changed successfully"

def generate_reset_code():
    """Generate a random 6-digit reset code"""
    import random
    code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE admin_settings SET reset_code = ? WHERE id = 1", (code,))
    conn.commit()
    conn.close()
    
    return code

def verify_reset_code(code):
    """Verify reset code"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT reset_code FROM admin_settings WHERE id = 1")
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0]:
        return result[0] == code
    return False

def reset_password_with_code(code, new_password):
    """Reset password using reset code"""
    if not verify_reset_code(code):
        return False, "Invalid reset code"
    
    if len(new_password) < 4:
        return False, "New password must be at least 4 characters"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    new_hash = hash_password(new_password)
    cursor.execute("""
        UPDATE admin_settings 
        SET password_hash = ?, reset_code = NULL, last_updated = CURRENT_TIMESTAMP 
        WHERE id = 1
    """, (new_hash,))
    conn.commit()
    conn.close()
    
    return True, "Password reset successfully"