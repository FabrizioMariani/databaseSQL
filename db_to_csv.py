import sqlite3
import pandas as pd

def export_db_to_csv():
    # Nome del database
    db_name = 'olist.db'
    
    try:
        # Connessione al database
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Ottieni la lista di tutte le tabelle presenti nel database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        if not tables:
            print("Il database è vuoto o non esiste.")
            return

        print(f"Esportazione tabelle da {db_name}...")

        # Per ogni tabella, leggi i dati e salvali in un CSV
        for table_name in tables:
            name = table_name[0]
            print(f"Esportando la tabella: {name}...")
            
            # Leggi la tabella con Pandas
            df = pd.read_sql_query(f"SELECT * FROM {name}", conn)
            
            # Salva in CSV
            csv_filename = f"export_{name}.csv"
            df.to_csv(csv_filename, index=False)
            print(f"File salvato: {csv_filename}")

        conn.close()
        print("\nEsportazione completata con successo!")

    except Exception as e:
        print(f"Errore durante l'esportazione: {e}")

if __name__ == "__main__":
    export_db_to_csv()