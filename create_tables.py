import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",
        port=5432,        # ← porta cambiata
        database="olist",
        user="postgres",
        password="admin"
    )

def create_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_unique_id TEXT PRIMARY KEY,
            customer_city      TEXT,
            customer_state     TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id            TEXT PRIMARY KEY,
            product_category_name TEXT DEFAULT 'unknown'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sellers (
            seller_id    TEXT PRIMARY KEY,
            seller_city  TEXT,
            seller_state TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id                   TEXT,
            product_id                 TEXT,
            seller_id                  TEXT,
            customer_unique_id         TEXT,
            price                      REAL NOT NULL CHECK(price > 0),
            order_purchase_timestamp   TIMESTAMP,
            PRIMARY KEY (order_id, product_id),
            FOREIGN KEY (customer_unique_id) REFERENCES customers(customer_unique_id),
            FOREIGN KEY (product_id)         REFERENCES products(product_id),
            FOREIGN KEY (seller_id)          REFERENCES sellers(seller_id)
        )
    """)

    conn.commit()
    conn.close()
    print("Database PostgreSQL creato con successo.")

if __name__ == "__main__":
    create_database()