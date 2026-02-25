import pandas as pd
import sqlite3

def load_data():
    try:
        # 1. Leggi il CSV
        df = pd.read_csv('olist.csv')
        conn = sqlite3.connect('olist.db')
        
        print("Inizio pulizia dati...")

        # --- CUSTOMERS ---
        # Teniamo solo l'ultima occorrenza per ogni customer_unique_id per evitare duplicati
        customers = df[['customer_unique_id', 'customer_zip_code_prefix', 'customer_city', 'customer_state']].copy()
        customers = customers.drop_duplicates(subset=['customer_unique_id'], keep='first')
        customers = customers.dropna(subset=['customer_unique_id'])

        # --- PRODUCTS ---
        products = df[['product_id', 'product_category_name', 'product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']].copy()
        products = products.drop_duplicates(subset=['product_id'], keep='first')
        products['product_category_name'] = products['product_category_name'].fillna('altro')
        # Il CHECK nel DB vuole pesi >= 0, puliamo eventuali negativi o nulli
        products['product_weight_g'] = products['product_weight_g'].fillna(0)
        products = products.dropna(subset=['product_id'])

        # --- SELLERS ---
        sellers = df[['seller_id', 'seller_zip_code_prefix', 'seller_city', 'seller_state']].copy()
        sellers = sellers.drop_duplicates(subset=['seller_id'], keep='first')
        sellers = sellers.dropna(subset=['seller_id'])

        # --- ORDERS ---
        orders = df[['order_id', 'customer_unique_id', 'product_id', 'seller_id', 'price', 'freight_value', 'order_purchase_timestamp']].copy()
        # Rimuoviamo righe dove mancano le chiavi esterne o il prezzo
        orders = orders.dropna(subset=['order_id', 'customer_unique_id', 'product_id', 'seller_id', 'price'])
        # Assicuriamoci che il prezzo sia positivo (per il CHECK vincolo)
        orders = orders[orders['price'] > 0]
        # Evitiamo duplicati della coppia chiave primaria (order_id + product_id)
        orders = orders.drop_duplicates(subset=['order_id', 'product_id'])

        print("Caricamento nel database...")
        
        # Inserimento (if_exists='replace' pulisce la tabella prima di caricare, 
        # utile se hai fatto test falliti in precedenza)
        customers.to_sql('customers', conn, if_exists='replace', index=False)
        products.to_sql('products', conn, if_exists='replace', index=False)
        sellers.to_sql('sellers', conn, if_exists='replace', index=False)
        orders.to_sql('orders', conn, if_exists='replace', index=False)

        conn.close()
        print("Successo! Dati caricati senza errori.")
    
    except Exception as e:
        print(f"Errore critico durante il caricamento: {e}")

if __name__ == "__main__":
    load_data()