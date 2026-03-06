import sqlite3

def get_connection():
    return sqlite3.connect('olist.db', check_same_thread=False)

def update_price(p_id, new_p):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET price = ? WHERE product_id = ?", (new_p, p_id))
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count

def insert_cust(uid, city, state):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO customers (customer_unique_id, customer_city, customer_state) VALUES (?, ?, ?)", 
                       (uid, city, state))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()