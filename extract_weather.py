import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from tenacity import retry, stop_after_attempt, wait_fixed

# Load environment variables from .env file
load_dotenv()

# --- CONFIGURATION ---
CITY = "Hyderabad"
LATITUDE = 17.3850
LONGITUDE = 78.4867
OUTPUT_DIR = "raw_data"
CONTAINER_NAME = "raw-weather-data"
AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

# Open-Meteo API endpoint
URL = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m&timezone=Asia%2FKolkata"

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_weather_data(url, params):
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()  # Throws exception on HTTP 4xx/5xx errors
    return response.json()

def fetch_and_save_weather():
    print(f"Starting weather data extraction for {CITY}...")
    
    # 1. Ensure output folder exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 2. Fetch raw JSON from public API
    response = requests.get(URL)
    
    if response.status_code == 200:
        data = response.json()
        hourly = data["hourly"]
        
        # 3. Construct structured DataFrame
        df = pd.DataFrame({
            "record_timestamp": hourly["time"],
            "temperature_c": hourly["temperature_2m"],
            "humidity_pct": hourly["relative_humidity_2m"],
            "wind_speed_kmh": hourly["wind_speed_10m"]
        })
        
        # 4. Data Transformation & Metadata Enhancement
        df["record_timestamp"] = pd.to_datetime(df["record_timestamp"])
        df["city"] = CITY
        df["ingested_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Reorder columns
        df = df[["city", "record_timestamp", "temperature_c", "humidity_pct", "wind_speed_kmh", "ingested_at"]]
        
        # 5. Export locally
        today_stamp = datetime.now().strftime("%Y%m%d")
        file_name = f"weather_{CITY.lower()}_{today_stamp}.csv"
        file_path = os.path.join(OUTPUT_DIR, file_name)
        df.to_csv(file_path, index=False)
        
        print(f"--- LOCAL SUCCESS ---")
        print(f"Extracted Records : {len(df)} rows")
        print(f"Saved CSV File To : {file_path}")
        print("\nFirst 5 Rows Preview:")
        print(df.head())

        # 6. Upload to Azure Blob Storage (Azurite)
        print("\nUploading CSV to Azure Blob Storage...")
        
        # Connect with explicit API version override for Azurite
        blob_service_client = BlobServiceClient.from_connection_string(
            AZURE_CONNECTION_STRING,
            api_version="2021-08-06"
        )
        
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        
        # Ensure container exists
        if not container_client.exists():
            container_client.create_container()
            
        blob_client = container_client.get_blob_client(file_name)
        
        with open(file_path, "rb") as data_file:
            blob_client.upload_blob(data_file, overwrite=True)
            
        print("--- AZURE UPLOAD SUCCESSFUL ---")
        
    else:
        print(f"--- FAILURE --- Status Code: {response.status_code}")

if __name__ == "__main__":
    fetch_and_save_weather()
