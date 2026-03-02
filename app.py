import streamlit as st
import pandas as pd
import sqlite3
import os
import sys

sys.path.append(os.path.dirname(__file__))
from database_utils import update_price, insert_cust

st.set_page_config(page_title="Olist Manager", layout="wide")

st.markdown("""
    <style>
    .main-title { font-size: 38px; font-weight: 800; color: #1E3A8A; margin-bottom: 10px; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #1E3A8A; color: white; }
    </style>
    """, unsafe_allow_html=True)

def run_query(query, params=None):
    with sqlite3.connect('olist2.db') as conn:
        return pd.read_sql(query, conn, params=params)

st.markdown('<h1 class="main-title"> Olist Store Management</h1>', unsafe_allow_html=True)

menu = [" Visualizza & Filtra", " Analisi Fatturato", " Gestione Clienti", " Aggiorna Prezzi"]
choice = st.sidebar.radio("Navigazione", menu)

if choice == " Visualizza & Filtra":
    st.subheader("Ricerca Avanzata Ordini")
    col1, col2 = st.columns(2)
    with col1:
        stato = st.text_input("Sigla Stato (es. SP)", "SP").upper()
    with col2:
        prezzo_min = st.number_input("Prezzo Minimo", 0)

    query = """
        SELECT o.order_id, o.price, c.customer_city, c.customer_state 
        FROM orders o JOIN customers c ON o.customer_unique_id = c.customer_unique_id 
        WHERE c.customer_state = ? AND o.price >= ? LIMIT 100
    """
    df = run_query(query, (stato, prezzo_min))
    st.dataframe(df, use_container_width=True)

elif choice == " Analisi Fatturato":
    st.subheader("Top 10 Categorie per Incasso")
    df_analitica = run_query("""
        SELECT p.product_category_name AS Categoria, ROUND(SUM(o.price), 2) AS Totale 
        FROM orders o JOIN products p ON o.product_id = p.product_id 
        GROUP BY 1 ORDER BY 2 DESC LIMIT 10
    """)
    st.bar_chart(df_analitica.set_index('Categoria'))

elif choice == " Gestione Clienti":
    st.subheader("Registrazione Nuovo Cliente")
    with st.form("form_cliente"):
        uid = st.text_input("ID Unico Cliente (es. hash)")
        cit = st.text_input("Città")
        sta = st.text_input("Stato (Sigla)")
        submit = st.form_submit_button("Registra Cliente")
        
        if submit:
            if uid and cit and sta:
                if insert_cust(uid, cit, sta):
                    st.success(f"Cliente {uid} registrato con successo!")
                else:
                    st.error("Errore: ID già esistente o database non pronto.")
            else:
                st.warning("Compila tutti i campi.")

elif choice == " Aggiorna Prezzi":
    st.subheader("Aggiornamento Listino Prezzi")
    col1, col2 = st.columns(2)
    with col1:
        p_id = st.text_input("ID Prodotto")
    with col2:
        new_p = st.number_input("Nuovo Prezzo (R$)", min_value=0.1, step=0.1)
    
    if st.button("Aggiorna Prezzo"):
        if p_id:
            righe_aggiornate = update_price(p_id, new_p)
            if righe_aggiornate > 0:
                st.success(f"Aggiornato! {righe_aggiornate} ordini modificati.")
            else:
                st.info("Nessun prodotto trovato con questo ID.")
        else:
            st.error("Inserisci un ID Prodotto valido.")