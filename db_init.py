
import sqlite3
from datetime import datetime

DB = "restaurant.db"

def init_db(db_path=None):
    db = DB if db_path is None else db_path
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS menu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        category TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS staff (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        role TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS tables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_no INTEGER UNIQUE,
        capacity INTEGER,
        reserved INTEGER DEFAULT 0,
        reserved_name TEXT,
        reserved_time TEXT,
        occupied INTEGER DEFAULT 0
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_no INTEGER,
        total REAL,
        paid INTEGER DEFAULT 0,
        created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        menu_id INTEGER,
        qty INTEGER,
        price REAL
    )""")
    conn.commit()

    # seed menu
    c.execute("SELECT COUNT(*) FROM menu")
    if c.fetchone()[0] == 0:
        items = [
            ('Margherita Pizza', 8.5, 'Pizza'),
            ('Pepperoni Pizza', 9.5, 'Pizza'),
            ('Pasta Carbonara', 10.0, 'Pasta'),
            ('Veggie Burger', 7.0, 'Burgers'),
            ('Caesar Salad', 5.5, 'Salads'),
            ('French Fries', 3.0, 'Sides'),
            ('Tiramisu', 4.5, 'Dessert'),
            ('Lemonade', 2.0, 'Drinks'),
        ]
        c.executemany("INSERT INTO menu (name, price, category) VALUES (?, ?, ?)", items)

    # seed staff
    c.execute("SELECT COUNT(*) FROM staff")
    if c.fetchone()[0] == 0:
        staff = [
            ('Aman', 'Chef'),
            ('Ram', 'Waiter'),
            ('Jasmine', 'Cashier'),
            ('Sehaj', 'Manager'),
            ('Sham', 'Cleaner')
        ]
        c.executemany("INSERT INTO staff (name, role) VALUES (?, ?)", staff)

    # seed tables
    c.execute("SELECT COUNT(*) FROM tables")
    if c.fetchone()[0] == 0:
        tables = [(i, 4, 0, None, None, 0) for i in range(1,7)]
        c.executemany("INSERT INTO tables (table_no, capacity, reserved, reserved_name, reserved_time, occupied) VALUES (?, ?, ?, ?, ?, ?)", tables)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("DB initialized")
