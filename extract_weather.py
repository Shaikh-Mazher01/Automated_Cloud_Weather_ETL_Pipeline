import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_exponential

CITIES = {
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Delhi": {"lat": 28.6139, "lon": 77.2090},
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867},
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639},
    "Jaipur": {"lat": 26.9124, "lon": 75.7873},
    "Ahmedabad": {"lat": 23.0225, "lon": 72.5714}
}

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_city_weather(city_name: str, lat: float, lon: float) -> pd.DataFrame:
    url = "https://archive-api.open-meteo.com/v1/archive"
    
    # Dynamic rolling 30-day window
    end_dt = datetime.now()
    start_dt = end_dt - timedelta(days=30)
    
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_dt.strftime("%Y-%m-%d"),
        "end_date": end_dt.strftime("%Y-%m-%d"),
        "hourly": [
            "temperature_2m", 
            "relative_humidity_2m", 
            "wind_speed_10m",
            "precipitation",
            "apparent_temperature",
            "uv_index"
        ],
        "timezone": "auto"
    }
    
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    
    hourly = data.get("hourly", {})
    df = pd.DataFrame({
        "city": city_name,
        "record_timestamp": hourly.get("time"),
        "temperature_c": hourly.get("temperature_2m"),
        "humidity_pct": hourly.get("relative_humidity_2m"),
        "wind_speed_kmh": hourly.get("wind_speed_10m"),
        "precipitation_mm": hourly.get("precipitation"),
        "feels_like_c": hourly.get("apparent_temperature"),
        "uv_index": hourly.get("uv_index")
    })
    return df

def extract_all_cities() -> pd.DataFrame:
    all_data = []
    for city, coords in CITIES.items():
        try:
            city_df = fetch_city_weather(city, coords["lat"], coords["lon"])
            all_data.append(city_df)
            time.sleep(1)
        except Exception as e:
            print(f"Error fetching data for {city}: {e}")
            
    if not all_data:
        raise RuntimeError("Failed to extract weather data for any city.")
        
    return pd.concat(all_data, ignore_index=True)
