import sqlite3
import pandas as pd
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_db():
    try:
        conn = sqlite3.connect('creds.db')
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS keyvault (
            store_id INTEGER PRIMARY KEY AUTOINCREMENT,
            type_of_service TEXT NOT NULL,
            created_by TEXT NOT NULL,
            created_date DATE NOT NULL,
            modified_by TEXT,
            modified_date DATE,
            api_key TEXT NOT NULL,
            endpoint TEXT NOT NULL,
            api_category TEXT NOT NULL,
            version TEXT NOT NULL
        )
        ''')
        conn.commit()
        logging.info("Database and table created successfully.")
    except sqlite3.Error as e:
        logging.error(f"Error creating database and table: {e}")
    finally:
        if conn:
            conn.close()

def reset_db():
    try:
        conn = sqlite3.connect('creds.db')
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS keyvault')
        conn.commit()
        logging.info("Database reset successfully.")
    except sqlite3.Error as e:
        logging.error(f"Error resetting database: {e}")
    finally:
        if conn:
            conn.close()
    create_db()

def insert_record(type_of_service, created_by, created_date, api_key, endpoint, api_category, version, modified_by=None):
    try:
        modified_date = None
        conn = sqlite3.connect('creds.db')
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO keyvault (type_of_service, created_by, created_date, modified_by, modified_date, api_key, endpoint, api_category, version)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (type_of_service, created_by, created_date, modified_by, modified_date, api_key, endpoint, api_category, version))
        conn.commit()
        store_id = cursor.lastrowid
        logging.info(f"Record inserted successfully with store_id: {store_id}")
        return store_id
    except sqlite3.Error as e:
        logging.error(f"Error inserting record: {e}")
    finally:
        if conn:
            conn.close()

def update_record(store_id, type_of_service, modified_by, api_key, endpoint, api_category, version):
    try:
        modified_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn = sqlite3.connect('creds.db')
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE keyvault
        SET type_of_service = ?, modified_by = ?, modified_date = ?, api_key = ?, endpoint = ?, api_category = ?, version = ?
        WHERE store_id = ?
        ''', (type_of_service, modified_by, modified_date, api_key, endpoint, api_category, version, store_id))
        conn.commit()
        logging.info(f"Record with store_id: {store_id} updated successfully.")
    except sqlite3.Error as e:
        logging.error(f"Error updating record with store_id {store_id}: {e}")
    finally:
        if conn:
            conn.close()

def fetch_record_by_store_id(store_id):
    try:
        conn = sqlite3.connect('creds.db')
        cursor = conn.cursor()
        cursor.execute('''
        SELECT * FROM keyvault
        WHERE store_id = ?
        ''', (store_id,))
        row = cursor.fetchone()
        if row:
            columns = ['store_id', 'type_of_service', 'created_by', 'created_date', 'modified_by', 'modified_date', 'api_key', 'endpoint', 'api_category', 'version']
            record = dict(zip(columns, row))
            logging.info(f"Record fetched successfully for store_id: {store_id}")
            return json.dumps(record)
        else:
            logging.warning(f"No record found for store_id: {store_id}")
            return json.dumps({})
    except sqlite3.Error as e:
        logging.error(f"Error fetching record for store_id {store_id}: {e}")
        return json.dumps({})
    finally:
        if conn:
            conn.close()

def fetch_all_records_as_df():
    try:
        conn = sqlite3.connect('creds.db')
        df = pd.read_sql_query('SELECT * FROM keyvault', conn)
        logging.info("All records fetched successfully as DataFrame.")
        return df
    except sqlite3.Error as e:
        logging.error(f"Error fetching all records: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

# Example usage
if __name__ == "__main__":
    # Create the database and table
    create_db()

    # Insert sample data and get the store_id
    store_id = insert_record('Azure', 'admin', '2024-08-06', 'azure_api_key', 'https://azure.endpoint', 'cloud', 'v1')
    print(f"Inserted record store_id: {store_id}")

    # Update the inserted record
    update_record(3, 'AzureOpenAI', 'admin2', 'openaikey232', 'https://new.azure.endpoint_LLM', 'LLM', 'v2')

    # Fetch the updated record by store_id and print as JSON
    record_json = fetch_record_by_store_id(store_id)
    print(record_json)

    # Insert more sample data
    store_id = insert_record('Azure', 'admin', '2024-08-06', 'azure_api_key', 'https://azure.endpoint', 'OCR', 'v1')
    print(f"Inserted record store_id: {store_id}")

    store_id = insert_record('AzureOpenAI', 'admin', '2024-08-06', 'azure_api_key', 'https://azure.endpoint.openai', 'LLM', 'v1')
    print(f"Inserted record store_id: {store_id}")

    # Fetch the inserted record by store_id and print as JSON
    record_json = fetch_record_by_store_id(3)
    print(record_json)

    # Fetch all records as a DataFrame and print
    df = fetch_all_records_as_df()
    print(df)
