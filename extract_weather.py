import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_fixed
from azure.storage.blob import BlobServiceClient

# Load environment variables
load_dotenv()

# --- CONFIGURATION & VALIDATION ---
AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME", "raw-weather-data")

def download_latest_blob_csv():
    if not AZURE_CONNECTION_STRING:
        raise ValueError("Missing AZURE_STORAGE_CONNECTION_STRING in environment settings.")

# --- API RETRY-PROTECTED HELPER ---
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_weather_data(url, params):
    """Fetches JSON payload from API with automatic retry policy and HTTP status checks."""
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()  # Throws HTTPError on 4xx/5xx status codes
    return response.json()

def fetch_and_save_weather():
    """Fetches weather forecast using retry logic and saves standard CSV snapshot locally."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 17.3850,
        "longitude": 78.4867,
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m"
    }
    
    print("Fetching weather forecast data from API...")
    # Wired up retry-protected API call
    data = fetch_weather_data(url, params)
    
    hourly = data["hourly"]
    df = pd.DataFrame({
        "record_timestamp": hourly["time"],
        "temperature_c": hourly["temperature_2m"],
        "humidity_pct": hourly["relative_humidity_2m"],
        "wind_speed_kmh": hourly["wind_speed_10m"]
    })
    
    # Metadata enrichment
    df["city"] = "Hyderabad"
    df["ingested_at"] = datetime.now().isoformat()
    
    os.makedirs("raw_data", exist_ok=True)
    filename = f"weather_hyderabad_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join("raw_data", filename)
    df.to_csv(filepath, index=False)
    
    print(f"Data saved locally to {filepath}")
    return filepath

def upload_to_azure_blob(local_file_path):
    """Uploads local CSV landing file to Azure Blob Storage (or Azurite emulator)."""
    if not local_file_path or not os.path.exists(local_file_path):
        print("No file found to upload.")
        return

    blob_service_client = BlobServiceClient.from_connection_string(
        AZURE_CONNECTION_STRING,
        api_version="2021-08-06"
    )
    
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    if not container_client.exists():
        container_client.create_container()
        print(f"Container '{CONTAINER_NAME}' created.")

    blob_name = os.path.basename(local_file_path)
    blob_client = container_client.get_blob_client(blob_name)

    print(f"Uploading {blob_name} to cloud landing container '{CONTAINER_NAME}'...")
    with open(local_file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    print("Upload complete!")

if __name__ == "__main__":
    saved_csv = fetch_and_save_weather()
    upload_to_azure_blob(saved_csv)
