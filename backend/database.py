import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "data" / "company.db"


def get_connection():
    """Create a connection to the SQLite database."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def create_database():
    """Create tables and insert demo e-commerce data."""

    DB_PATH.parent.mkdir(exist_ok=True)

    connection = get_connection()
    cursor = connection.cursor()

    # Customers
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            city TEXT,
            country TEXT
        )
    """)

    # Products
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            price REAL
        )
    """)

    # Orders
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            order_date TEXT,
            status TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    """)

    # Order Items
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id INTEGER PRIMARY KEY,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)

    # Inventory
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            inventory_id INTEGER PRIMARY KEY,
            product_id INTEGER,
            stock INTEGER,
            warehouse TEXT,
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)

    # Insert customers
    cursor.executemany("""
        INSERT OR IGNORE INTO customers
        (customer_id, name, city, country)
        VALUES (?, ?, ?, ?)
    """, [
        (1, "Arun Kumar", "Chennai", "India"),
        (2, "Priya Sharma", "Bangalore", "India"),
        (3, "Rahul Singh", "Mumbai", "India"),
        (4, "Meera Das", "Delhi", "India"),
        (5, "Karthik Raj", "Hyderabad", "India"),
        (6, "Ananya Rao", "Pune", "India"),
        (7, "Vikram Patel", "Ahmedabad", "India"),
        (8, "Sneha Iyer", "Kochi", "India"),
    ])

    # Insert products
    cursor.executemany("""
        INSERT OR IGNORE INTO products
        (product_id, name, category, price)
        VALUES (?, ?, ?, ?)
    """, [
        (1, "Laptop Pro", "Electronics", 75000),
        (2, "Wireless Headphones", "Electronics", 5000),
        (3, "Smart Watch", "Electronics", 12000),
        (4, "Office Chair", "Furniture", 15000),
        (5, "Mechanical Keyboard", "Accessories", 7000),
        (6, "Gaming Mouse", "Accessories", 3000),
        (7, "USB-C Hub", "Accessories", 2500),
        (8, "Monitor 24 Inch", "Electronics", 18000),
    ])

    # Insert orders
    cursor.executemany("""
        INSERT OR IGNORE INTO orders
        (order_id, customer_id, order_date, status)
        VALUES (?, ?, ?, ?)
    """, [
        (101, 1, "2026-01-15", "Delivered"),
        (102, 2, "2026-01-22", "Delivered"),
        (103, 3, "2026-02-10", "Delivered"),
        (104, 4, "2026-02-18", "Delivered"),
        (105, 5, "2026-03-05", "Delivered"),
        (106, 6, "2026-03-20", "Shipped"),
        (107, 7, "2026-04-02", "Delivered"),
        (108, 8, "2026-04-15", "Processing"),
        (109, 1, "2026-05-01", "Delivered"),
        (110, 3, "2026-05-18", "Delivered"),
        (111, 5, "2026-06-03", "Shipped"),
        (112, 7, "2026-06-20", "Delivered"),
    ])

    # Insert order items
    cursor.executemany("""
        INSERT OR IGNORE INTO order_items
        (order_item_id, order_id, product_id, quantity)
        VALUES (?, ?, ?, ?)
    """, [
        (1, 101, 1, 1),
        (2, 101, 2, 2),
        (3, 102, 3, 1),
        (4, 102, 6, 2),
        (5, 103, 1, 1),
        (6, 103, 5, 1),
        (7, 104, 4, 1),
        (8, 104, 7, 2),
        (9, 105, 8, 2),
        (10, 105, 2, 1),
        (11, 106, 3, 2),
        (12, 106, 6, 1),
        (13, 107, 1, 1),
        (14, 107, 8, 1),
        (15, 108, 5, 2),
        (16, 108, 7, 3),
        (17, 109, 1, 2),
        (18, 109, 2, 1),
        (19, 110, 4, 1),
        (20, 110, 6, 2),
        (21, 111, 3, 1),
        (22, 111, 5, 1),
        (23, 112, 8, 2),
        (24, 112, 2, 2),
    ])

    # Insert inventory
    cursor.executemany("""
        INSERT OR IGNORE INTO inventory
        (inventory_id, product_id, stock, warehouse)
        VALUES (?, ?, ?, ?)
    """, [
        (1, 1, 15, "Chennai"),
        (2, 2, 45, "Chennai"),
        (3, 3, 20, "Bangalore"),
        (4, 4, 8, "Mumbai"),
        (5, 5, 30, "Delhi"),
        (6, 6, 60, "Chennai"),
        (7, 7, 50, "Bangalore"),
        (8, 8, 12, "Mumbai"),
    ])

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_database()
    print(f"Database created successfully at: {DB_PATH}")