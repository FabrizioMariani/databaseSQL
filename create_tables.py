import sqlite3

def create_database():
    conn = sqlite3.connect('olist2.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
        customer_unique_id TEXT PRIMARY KEY,
        customer_city TEXT,
        customer_state TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
        product_id TEXT PRIMARY KEY,
        product_category_name TEXT DEFAULT 'unknown')''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS sellers (
        seller_id TEXT PRIMARY KEY,
        seller_city TEXT,
        seller_state TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
        order_id TEXT,
        product_id TEXT,
        seller_id TEXT,
        customer_unique_id TEXT,
        price REAL NOT NULL CHECK(price > 0),
        order_purchase_timestamp DATETIME,
        PRIMARY KEY (order_id, product_id),
        FOREIGN KEY (customer_unique_id) REFERENCES customers (customer_unique_id),
        FOREIGN KEY (product_id) REFERENCES products (product_id),
        FOREIGN KEY (seller_id) REFERENCES sellers (seller_id))''')

    conn.commit()
    conn.close()
    print("Database creato con successo.")

if __name__ == "__main__":
    create_database()