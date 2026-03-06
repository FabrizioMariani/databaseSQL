import sqlite3
import psycopg2
from create_tables import get_connection
# PRIMA (puntava a olist.db corrotto)
def get_connection():
    return sqlite3.connect('olist.db', check_same_thread=False)

# DOPO (punta a olist2.db dove ci sono i dati)
def get_connection():
    return sqlite3.connect('olist2.db', check_same_thread=False)

def update_price(p_id, new_p):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET price = ? WHERE product_id = ?", (new_p, p_id))
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count
def delete_order(order_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Controlla se l'ordine esiste
        cursor.execute("""
            SELECT COUNT(*) FROM orders
            WHERE order_id = %s
        """, (order_id,))
        if cursor.fetchone()[0] == 0:
            return False
        # Elimina l'ordine
        cursor.execute("""
            DELETE FROM orders
            WHERE order_id = %s
        """, (order_id,))
        conn.commit()
        return True
    except psycopg2.Error:
        conn.rollback()
        return False
    finally:
        conn.close()

# database_utils.py
def insert_cust(uid, city, state):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Controllo duplicato sulla stessa connessione dell'inserimento
        cursor.execute(
            "SELECT customer_unique_id FROM customers WHERE customer_unique_id = ?",
            (uid,)
        )
        if cursor.fetchone() is not None:
            return False  # Cliente già esistente
        
        cursor.execute(
            "INSERT INTO customers (customer_unique_id, customer_city, customer_state) VALUES (?, ?, ?)",
            (uid, city, state)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()