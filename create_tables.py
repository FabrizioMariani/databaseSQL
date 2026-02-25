import sqlite3

def create_database():
    conn = sqlite3.connect('olist.db')
    cursor = conn.cursor()

    # 1. Tabella Clienti (Normalizzata)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            customer_unique_id TEXT PRIMARY KEY,
            customer_zip_code_prefix INTEGER,
            customer_city TEXT NOT NULL,
            customer_state TEXT NOT NULL
        )
    ''')

    # 2. Tabella Prodotti
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            product_category_name TEXT DEFAULT 'altro',
            product_weight_g REAL CHECK(product_weight_g >= 0),
            product_length_cm REAL,
            product_height_cm REAL,
            product_width_cm REAL
        )
    ''')

    # 3. Tabella Venditori
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sellers (
            seller_id TEXT PRIMARY KEY,
            seller_zip_code_prefix INTEGER,
            seller_city TEXT,
            seller_state TEXT
        )
    ''')

    # 4. Tabella Ordini (Tabella dei fatti con Foreign Keys)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT,
            customer_unique_id TEXT,
            product_id TEXT,
            seller_id TEXT,
            price REAL NOT NULL CHECK(price > 0),
            freight_value REAL,
            order_purchase_timestamp DATETIME,
            PRIMARY KEY (order_id, product_id),
            FOREIGN KEY (customer_unique_id) REFERENCES customers (customer_unique_id),
            FOREIGN KEY (product_id) REFERENCES products (product_id),
            FOREIGN KEY (seller_id) REFERENCES sellers (seller_id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Database creato con successo!")

if __name__ == "__main__":
    create_database()