import os
import sqlite3
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
DB_NAME = "weather_database.db"
CONTAINER_NAME = "raw-weather-data"
AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
LOCAL_DOWNLOAD_DIR = "temp_download"

def download_latest_blob_csv():
    """Finds and downloads the latest weather CSV from Azure Blob storage using system timestamp."""
    os.makedirs(LOCAL_DOWNLOAD_DIR, exist_ok=True)
    
    blob_service_client = BlobServiceClient.from_connection_string(
        AZURE_CONNECTION_STRING,
        api_version="2021-08-06"
    )
    
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    
    if not container_client.exists():
        container_client.create_container()
        print(f"Container '{CONTAINER_NAME}' created.")
    
    print("Scanning cloud container for the latest weather CSV...")
    blobs = list(container_client.list_blobs())
    if not blobs:
        print("--- ERROR: No files found in the cloud container! ---")
        return None

    # Correct selection: Grab latest blob by last_modified system metadata
    latest_blob = max(blobs, key=lambda b: b.last_modified)
    download_path = os.path.join(LOCAL_DOWNLOAD_DIR, latest_blob.name)
    
    print(f"Downloading {latest_blob.name} (Modified: {latest_blob.last_modified}) from cloud storage...")
    blob_client = container_client.get_blob_client(latest_blob.name)
    with open(download_path, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())
        
    print(f"Downloaded successfully to {download_path}")
    return download_path

def load_csv_to_sqlite(file_path):
    """Loads the downloaded CSV dataframe into the SQLite database with duplicate protection."""
    if not file_path:
        return
        
    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} rows from CSV. Inserting into database...")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    inserted_count = 0
    duplicate_count = 0
    
    for _, row in df.iterrows():
        try:
            # Using INSERT OR IGNORE to respect our UNIQUE constraint (city, record_timestamp)
            cursor.execute("""
                INSERT OR IGNORE INTO weather_forecasts 
                (city, record_timestamp, temperature_c, humidity_pct, wind_speed_kmh, ingested_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                row["city"],
                row["record_timestamp"],
                row["temperature_c"],
                row["humidity_pct"],
                row["wind_speed_kmh"],
                row["ingested_at"]
            ))
            
            if cursor.rowcount > 0:
                inserted_count += 1
            else:
                duplicate_count += 1
                
        except sqlite3.Error as e:
            print(f"Error inserting row: {e}")
            
    conn.commit()
    conn.close()
    
    print(f"--- INGESTION COMPLETE ---")
    print(f"New Rows Inserted : {inserted_count}")
    print(f"Duplicates Skipped: {duplicate_count}")

if __name__ == "__main__":
    latest_csv = download_latest_blob_csv()
    if latest_csv:
        load_csv_to_sqlite(latest_csv)
