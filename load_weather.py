import os
import sqlite3
import pandas as pd
from datetime import datetime
from azure.storage.blob import BlobServiceClient

DB_NAME = os.getenv("DB_PATH", "weather_database.db")
AZURE_CONN_STR = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME", "weather-raw-data")

def upload_to_azure_blob(file_path: str, blob_name: str) -> bool:
    """Uploads exported CSV file to Azure Blob Storage container."""
    if not AZURE_CONN_STR:
        print("[!] Azure connection string not configured (AZURE_STORAGE_CONNECTION_STRING missing). Skipping cloud upload.")
        return False

    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONN_STR)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        
        # Create container if it does not exist
        if not container_client.exists():
            container_client.create_container()

        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=blob_name)
        
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
            
        print(f"[+] Successfully uploaded raw data to Azure Blob Storage: {CONTAINER_NAME}/{blob_name}")
        return True
    except Exception as e:
        print(f"[!] Azure Blob Storage Upload Failed: {e}")
        return False

def load_data_to_db(df: pd.DataFrame, db_path: str = DB_NAME) -> int:
    """Loads DataFrame into SQLite database preserving all weather metrics."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Ensure ingestion timestamp exists
    if "ingested_at" not in df.columns:
        df["ingested_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    records = df[[
        "city", "record_timestamp", "temperature_c", "humidity_pct",
        "wind_speed_kmh", "precipitation_mm", "feels_like_c", "uv_index", "ingested_at"
    ]].values.tolist()

    insert_query = """
    INSERT OR REPLACE INTO weather_forecasts (
        city, record_timestamp, temperature_c, humidity_pct,
        wind_speed_kmh, precipitation_mm, feels_like_c, uv_index, ingested_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    cursor.executemany(insert_query, records)
    conn.commit()

    # Get accurate count of rows after idempotent upsert
    cursor.execute("SELECT COUNT(*) FROM weather_forecasts;")
    total_count = cursor.fetchone()[0]
    conn.close()

    return total_count
