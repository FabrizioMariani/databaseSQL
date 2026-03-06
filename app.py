import streamlit as st
import pandas as pd
import sqlite3
import os
import sys
from create_tables import get_connection

sys.path.append(os.path.dirname(__file__))
try:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    versione = cursor.fetchone()[0]
    conn.close()
    st.sidebar.success("✅ Connesso a PostgreSQL")
    st.sidebar.caption(f"🐘 {versione[:30]}")
    st.sidebar.caption("🐳 Docker container attivo")
except:
    st.sidebar.error("❌ Database non raggiungibile")
st.set_page_config(page_title="Olist Manager", layout="wide")
try:
    conn = get_connection()
    conn.close()
    st.sidebar.success("✅ Connesso a PostgreSQL")
except:
    st.sidebar.error("❌ Database non raggiungibile")
st.markdown("""
    <style>
    .main-title { font-size: 38px; font-weight: 800; color: #1E3A8A; margin-bottom: 10px; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #1E3A8A; color: white; }
    </style>
    """, unsafe_allow_html=True)

def run_query(query, params=None):
    with sqlite3.connect('olist2.db') as conn:
        return pd.read_sql(query, conn, params=params or [])

def run_write(query, params=None):
    with sqlite3.connect('olist2.db') as conn:
        cursor = conn.cursor()
        cursor.execute(query, params or [])
        conn.commit()
        return cursor.rowcount

st.markdown('<h1 class="main-title">📊 Olist Store Management</h1>', unsafe_allow_html=True)

menu = ["🔍 Visualizza & Filtra", "📈 Analisi Fatturato", "👤 Gestione Clienti", "💰 Aggiorna Prezzi", "🗑️ Elimina Ordine"]
choice = st.sidebar.radio("Navigazione", menu)

# ─────────────────────────────────────────
# QUERY 1 — conteggio totale risultati
# QUERY 2 — lista ordini paginata con JOIN
# ─────────────────────────────────────────
if choice == "🔍 Visualizza & Filtra":
    st.subheader("Ricerca Avanzata Ordini")
    col1, col2 = st.columns(2)
    with col1:
        stato = st.text_input("Sigla Stato (es. SP)", "SP").upper()
    with col2:
        prezzo_min = st.number_input("Prezzo Minimo", 0)

    PAGE_SIZE = 100
    if "pagina" not in st.session_state:
        st.session_state.pagina = 0

    # QUERY 1 — conteggio con cursore diretto
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) AS totale
        FROM orders o
        JOIN customers c ON o.customer_unique_id = c.customer_unique_id
        WHERE c.customer_state = %s
          AND o.price >= %s
    """, (stato, prezzo_min))
    n_totale = cursor.fetchone()[0]
    conn.close()

    n_pagine = max(1, -(-n_totale // PAGE_SIZE))
    st.caption(f"🔎 {n_totale} ordini trovati — pagina {st.session_state.pagina + 1} di {n_pagine}")

    col_prev, col_info, col_next = st.columns([1, 2, 1])
    with col_prev:
        if st.button("⬅️ Precedente") and st.session_state.pagina > 0:
            st.session_state.pagina -= 1
    with col_next:
        if st.button("Successivo ➡️") and st.session_state.pagina < n_pagine - 1:
            st.session_state.pagina += 1
    with col_info:
        st.markdown(f"<center>Pagina {st.session_state.pagina + 1} / {n_pagine}</center>", unsafe_allow_html=True)

    offset = st.session_state.pagina * PAGE_SIZE

    # QUERY 2 — lista ordini con cursore diretto
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            o.order_id,
            o.price,
            c.customer_city,
            c.customer_state,
            o.order_purchase_timestamp
        FROM orders o
        JOIN customers c ON o.customer_unique_id = c.customer_unique_id
        WHERE c.customer_state = %s
          AND o.price >= %s
        ORDER BY o.price DESC
        LIMIT %s OFFSET %s
    """, (stato, prezzo_min, PAGE_SIZE, offset))
    righe = cursor.fetchall()
    conn.close()

    df = pd.DataFrame(righe, columns=['ID_Ordine','Prezzo','Città','Stato','Data_Acquisto'])

    if df.empty:
        st.warning("Nessun ordine trovato con questi filtri.")
    else:
        st.dataframe(df, use_container_width=True)
# ─────────────────────────────────────────
# QUERY 3 — top 10 categorie per fatturato
# QUERY 4 — totale generale e media ordine
# QUERY 5 — top 5 stati per fatturato
# ─────────────────────────────────────────
elif choice == "📈 Analisi Fatturato":
    st.subheader("Analisi Fatturato")

    # QUERY 3 — top 10 categorie per incasso totale
    df_cat = run_query("""
        SELECT
            p.product_category_name     AS Categoria,
            COUNT(o.order_id)           AS Num_Ordini,
            ROUND(SUM(o.price), 2)      AS Fatturato_Totale,
            ROUND(AVG(o.price), 2)      AS Prezzo_Medio
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        GROUP BY p.product_category_name
        ORDER BY Fatturato_Totale DESC
        LIMIT 10
    """)
    st.markdown("#### 🏆 Top 10 Categorie per Incasso")
    st.bar_chart(df_cat.set_index('Categoria')['Fatturato_Totale'])
    st.dataframe(df_cat, use_container_width=True)

    st.divider()

    # QUERY 4 — statistiche generali: totale ordini, fatturato totale, media
    df_stats = run_query("""
        SELECT
            COUNT(*)                AS Totale_Ordini,
            ROUND(SUM(price), 2)    AS Fatturato_Totale,
            ROUND(AVG(price), 2)    AS Prezzo_Medio,
            ROUND(MIN(price), 2)    AS Prezzo_Minimo,
            ROUND(MAX(price), 2)    AS Prezzo_Massimo
        FROM orders
    """)
    st.markdown("#### 📊 Statistiche Generali")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Totale Ordini",   df_stats['Totale_Ordini'][0])
    col2.metric("Fatturato (R$)",  df_stats['Fatturato_Totale'][0])
    col3.metric("Prezzo Medio",    df_stats['Prezzo_Medio'][0])
    col4.metric("Prezzo Minimo",   df_stats['Prezzo_Minimo'][0])
    col5.metric("Prezzo Massimo",  df_stats['Prezzo_Massimo'][0])

    st.divider()

    # QUERY 5 — top 5 stati per fatturato
    df_stati = run_query("""
        SELECT
            c.customer_state            AS Stato,
            COUNT(o.order_id)           AS Num_Ordini,
            ROUND(SUM(o.price), 2)      AS Fatturato_Totale
        FROM orders o
        JOIN customers c ON o.customer_unique_id = c.customer_unique_id
        GROUP BY c.customer_state
        ORDER BY Fatturato_Totale DESC
        LIMIT 5
    """)
    st.markdown("#### 🗺️ Top 5 Stati per Fatturato")
    st.bar_chart(df_stati.set_index('Stato')['Fatturato_Totale'])
    st.dataframe(df_stati, use_container_width=True)

# ─────────────────────────────────────────
# QUERY 6  — COUNT duplicato cliente
# QUERY 7  — INSERT nuovo cliente
# QUERY 8  — SELECT lista ultimi clienti
# ─────────────────────────────────────────
elif choice == "👤 Gestione Clienti":
    st.subheader("Registrazione Nuovo Cliente")

    with st.form("form_cliente"):
        uid = st.text_input("ID Unico Cliente (es. hash)")
        cit = st.text_input("Città")
        sta = st.text_input("Stato (Sigla, es. SP)")
        submit = st.form_submit_button("Registra Cliente")

        if submit:
            if uid and cit and sta:
                # QUERY 6 — controlla se il cliente esiste già
                dup = run_query("""
                    SELECT COUNT(*) AS esiste
                    FROM customers
                    WHERE customer_unique_id = ?
                """, (uid,))

                if dup['esiste'][0] > 0:
                    st.error(f"❌ Il cliente con ID '{uid}' esiste già nel database.")
                else:
                    # QUERY 7 — inserisce il nuovo cliente
                    try:
                        run_write("""
                            INSERT INTO customers
                                (customer_unique_id, customer_city, customer_state)
                            VALUES (?, ?, ?)
                        """, (uid, cit, sta))
                        st.success(f"✅ Cliente {uid} registrato con successo!")
                    except sqlite3.IntegrityError:
                        st.error("❌ Errore inaspettato durante l'inserimento.")
            else:
                st.warning("⚠️ Compila tutti i campi.")

    st.divider()

    # QUERY 8 — mostra gli ultimi 10 clienti registrati
    st.markdown("#### 👥 Ultimi 10 Clienti Registrati")
    df_clienti = run_query("""
        SELECT
            customer_unique_id  AS ID_Cliente,
            customer_city       AS Città,
            customer_state      AS Stato
        FROM customers
        ORDER BY rowid DESC
        LIMIT 10
    """)
    st.dataframe(df_clienti, use_container_width=True)

# ─────────────────────────────────────────
# QUERY 9  — COUNT verifica prodotto
# QUERY 10 — UPDATE prezzo
# QUERY 11 — SELECT storico prezzi prodotto
# ─────────────────────────────────────────
elif choice == "💰 Aggiorna Prezzi":
    st.subheader("Aggiornamento Listino Prezzi")
    col1, col2 = st.columns(2)
    with col1:
        p_id = st.text_input("ID Prodotto")
    with col2:
        new_p = st.number_input("Nuovo Prezzo (R$)", min_value=0.1, step=0.1)

    if st.button("Aggiorna Prezzo"):
        if p_id:
            # QUERY 9 — verifica che il prodotto esista
            check = run_query("""
                SELECT COUNT(*) AS esiste
                FROM products
                WHERE product_id = ?
            """, (p_id,))

            if check['esiste'][0] == 0:
                st.error(f"❌ Nessun prodotto trovato con ID '{p_id}'.")
            else:
                # QUERY 10 — aggiorna il prezzo su tutti gli ordini del prodotto
                righe = run_write("""
                    UPDATE orders
                    SET price = ?
                    WHERE product_id = ?
                """, (new_p, p_id))

                if righe > 0:
                    st.success(f"✅ Aggiornati {righe} ordini con il nuovo prezzo di R$ {new_p}.")
                else:
                    st.info("ℹ️ Prodotto trovato ma nessun ordine collegato.")
        else:
            st.error("⚠️ Inserisci un ID Prodotto valido.")

    st.divider()

    # QUERY 11 — mostra dettaglio ordini del prodotto cercato (prezzo attuale)
    if p_id:
        st.markdown("#### 📋 Ordini collegati al prodotto")
        df_ordini = run_query("""
            SELECT
                o.order_id                      AS ID_Ordine,
                o.price                         AS Prezzo_Attuale,
                p.product_category_name         AS Categoria,
                o.order_purchase_timestamp      AS Data_Acquisto
            FROM orders o
            JOIN products p ON o.product_id = p.product_id
            WHERE o.product_id = ?
            ORDER BY o.order_purchase_timestamp DESC
            LIMIT 20
        """, (p_id,))

        if df_ordini.empty:
            st.info("Nessun ordine trovato per questo prodotto.")
        else:
            st.dataframe(df_ordini, use_container_width=True)    
            # --- 5. ELIMINA ORDINE ---
elif choice == "🗑️ Elimina Ordine":
    st.subheader("Eliminazione Ordine")

    # Ultimi 10 ordini con cursore diretto
    st.markdown("#### 📋 Ultimi 10 ordini nel database")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            o.order_id,
            o.price,
            c.customer_city,
            c.customer_state,
            o.order_purchase_timestamp
        FROM orders o
        JOIN customers c ON o.customer_unique_id = c.customer_unique_id
        ORDER BY o.order_purchase_timestamp DESC
        LIMIT 10
    """)
    righe = cursor.fetchall()
    conn.close()

    df_ultimi = pd.DataFrame(righe, columns=['ID_Ordine','Prezzo','Città','Stato','Data_Acquisto'])
    st.dataframe(df_ultimi, use_container_width=True)

    st.divider()

    st.markdown("#### 🗑️ Elimina un ordine")
    order_id = st.text_input("ID Ordine da eliminare")
    conferma = st.checkbox("⚠️ Confermo di voler eliminare questo ordine")

    if st.button("Elimina Ordine"):
        if not order_id:
            st.error("⚠️ Inserisci un ID Ordine valido.")
        elif not conferma:
            st.warning("⚠️ Spunta la casella di conferma prima di eliminare.")
        else:
            conn = get_connection()
            cursor = conn.cursor()

            # Controlla se esiste
            cursor.execute("""
                SELECT COUNT(*) FROM orders
                WHERE order_id = %s
            """, (order_id,))
            esiste = cursor.fetchone()[0]

            if esiste == 0:
                st.error(f"❌ Nessun ordine trovato con ID '{order_id}'.")
                conn.close()
            else:
                cursor.execute("""
                    DELETE FROM orders
                    WHERE order_id = %s
                """, (order_id,))
                conn.commit()
                righe = cursor.rowcount
                conn.close()

                if righe > 0:
                    st.success(f"✅ Ordine '{order_id}' eliminato con successo!")
                else:
                    st.error("❌ Errore durante l'eliminazione.")
            