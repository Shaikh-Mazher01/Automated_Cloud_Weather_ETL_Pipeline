import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

load_dotenv()

# --- CONFIGURATION ---
DB_NAME = os.getenv("DB_PATH", "weather_database.db")
CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME", "raw-weather-data")
AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
LOCAL_DOWNLOAD_DIR = "temp_download"

def download_latest_blob_csv():
    """Finds and downloads the latest weather CSV from Azure Blob storage using system last_modified timestamp."""
    if not AZURE_CONNECTION_STRING:
        print("AZURE_STORAGE_CONNECTION_STRING not configured. Using local CSV files directly.")
        return None

    os.makedirs(LOCAL_DOWNLOAD_DIR, exist_ok=True)
    
    blob_service_client = BlobServiceClient.from_connection_string(
        AZURE_CONNECTION_STRING,
        api_version="2021-08-06"
    )
    
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    
    if not container_client.exists():
        container_client.create_container()
        print(f"Container '{CONTAINER_NAME}' created.")
    
    print("Scanning cloud container for latest weather snapshot...")
    blobs = list(container_client.list_blobs())
    if not blobs:
        print("--- WARNING: No files found in the cloud container! ---")
        return None

    latest_blob = max(blobs, key=lambda b: b.last_modified)
    download_path = os.path.join(LOCAL_DOWNLOAD_DIR, latest_blob.name)
    
    print(f"Downloading {latest_blob.name} (Modified: {latest_blob.last_modified}) from cloud storage...")
    blob_client = container_client.get_blob_client(latest_blob.name)
    with open(download_path, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())
        
    print(f"Downloaded successfully to {download_path}")
    return download_path

def load_csv_to_sqlite(file_path):
    """Loads CSV dataframe into SQLite using batch execution (executemany) with composite key deduplication."""
    if not file_path or not os.path.exists(file_path):
        print(f"File not found for SQL ingestion: {file_path}")
        return
        
    df = pd.read_csv(file_path)
    total_records = len(df)
    print(f"Loaded {total_records} rows from CSV. Ingesting into SQLite database '{DB_NAME}'...")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    records = [
        (
            row["city"],
            row["record_timestamp"],
            row["temperature_c"],
            row["humidity_pct"],
            row["wind_speed_kmh"],
            row["ingested_at"]
        )
        for _, row in df.iterrows()
    ]
    
    cursor.executemany("""
        INSERT OR IGNORE INTO weather_forecasts 
        (city, record_timestamp, temperature_c, humidity_pct, wind_speed_kmh, ingested_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, records)
    
    inserted_count = cursor.rowcount
    duplicate_count = total_records - max(0, inserted_count)
    
    conn.commit()
    conn.close()
    
    print("--- INGESTION COMPLETE ---")
    print(f"Total Records Processed : {total_records}")
    print(f"New Rows Inserted      : {inserted_count}")
    print(f"Duplicates Skipped     : {duplicate_count}")

if __name__ == "__main__":
    latest_csv = download_latest_blob_csv()
    if latest_csv:
        load_csv_to_sqlite(latest_csv)
