import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from create_tables import get_connection

def load_data():
    df = pd.read_csv('olist.csv')
    conn = get_connection()
    cursor = conn.cursor()

    print("Caricamento customers...")
    customers = df[['customer_unique_id','customer_city','customer_state']] \
        .drop_duplicates('customer_unique_id').values.tolist()
    execute_values(cursor, """
        INSERT INTO customers (customer_unique_id, customer_city, customer_state)
        VALUES %s
        ON CONFLICT (customer_unique_id) DO NOTHING
    """, customers)

    print("Caricamento products...")
    products = df[['product_id','product_category_name']] \
        .drop_duplicates('product_id')
    products['product_category_name'] = products['product_category_name'].fillna('altro')
    execute_values(cursor, """
        INSERT INTO products (product_id, product_category_name)
        VALUES %s
        ON CONFLICT (product_id) DO NOTHING
    """, products.values.tolist())

    print("Caricamento sellers...")
    sellers = df[['seller_id','seller_city','seller_state']] \
        .drop_duplicates('seller_id').values.tolist()
    execute_values(cursor, """
        INSERT INTO sellers (seller_id, seller_city, seller_state)
        VALUES %s
        ON CONFLICT (seller_id) DO NOTHING
    """, sellers)

    print("Caricamento orders...")
    orders = df[['order_id','product_id','seller_id',
                 'customer_unique_id','price',
                 'order_purchase_timestamp']].dropna()
    orders = orders.drop_duplicates(['order_id','product_id']).values.tolist()
    execute_values(cursor, """
        INSERT INTO orders
            (order_id, product_id, seller_id, customer_unique_id, price, order_purchase_timestamp)
        VALUES %s
        ON CONFLICT (order_id, product_id) DO NOTHING
    """, orders)

    conn.commit()
    conn.close()
    print("✅ Dati caricati correttamente in PostgreSQL!")

if __name__ == "__main__":
    load_data()