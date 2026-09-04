import os
import sqlite3
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
from azure.storage.blob import BlobServiceClient

# Load environment variables from .env file
load_dotenv()

DB_NAME = os.getenv("DB_PATH", "weather_database.db")
AZURE_CONN_STR = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME", "weather-raw-data")

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def _upload_blob_with_retry(container_client, blob_name: str, file_path: str):
    blob_client = container_client.get_blob_client(blob=blob_name)
    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)

def upload_to_azure_blob(file_path: str, blob_name: str) -> bool:
    """Uploads exported CSV file to Azure Blob Storage with automatic retry logic."""
    if not AZURE_CONN_STR:
        print("[!] Azure connection string not configured (AZURE_STORAGE_CONNECTION_STRING missing). Degrading to local-only mode.")
        return False

    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONN_STR)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        
        if not container_client.exists():
            container_client.create_container()

        _upload_blob_with_retry(container_client, blob_name, file_path)
        print(f"[+] Successfully uploaded raw snapshot to Azure Blob Storage: {CONTAINER_NAME}/{blob_name}")
        return True
    except Exception as e:
        print(f"[!] Azure Blob Storage Upload Failed after retries: {e}")
        return False

def load_data_to_db(df: pd.DataFrame, db_path: str = DB_NAME) -> int:
    """Loads DataFrame into SQLite database preserving all weather metrics."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

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

    cursor.execute("SELECT COUNT(*) FROM weather_forecasts;")
    total_count = cursor.fetchone()[0]
    conn.close()

    return total_count
