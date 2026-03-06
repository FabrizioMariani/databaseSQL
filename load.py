import pandas as pd
import sqlite3

def load_data():
    df = pd.read_csv('olist.csv')
    conn = sqlite3.connect('olist2.db')

    df[['customer_unique_id', 'customer_city', 'customer_state']].drop_duplicates('customer_unique_id').to_sql('customers', conn, if_exists='replace', index=False)
    
    prod = df[['product_id', 'product_category_name']].drop_duplicates('product_id')
    prod['product_category_name'] = prod['product_category_name'].fillna('altro')
    prod.to_sql('products', conn, if_exists='replace', index=False)

    df[['seller_id', 'seller_city', 'seller_state']].drop_duplicates('seller_id').to_sql('sellers', conn, if_exists='replace', index=False)

    ordini = df[['order_id', 'product_id', 'seller_id', 'customer_unique_id', 'price', 'order_purchase_timestamp']].dropna()
    ordini.drop_duplicates(['order_id', 'product_id']).to_sql('orders', conn, if_exists='replace', index=False)

    conn.close()
    print("Dati caricati correttamente.")

if __name__ == "__main__":
    load_data()