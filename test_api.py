import requests
import pandas as pd

# Open-Meteo public weather API for Hyderabad
url = "https://api.open-meteo.com/v1/forecast?latitude=17.3850&longitude=78.4867&hourly=temperature_2m,relative_humidity_2m,rain&timezone=Asia%2FKolkata"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    hourly_data = data["hourly"]
    
    df = pd.DataFrame({
        "timestamp": hourly_data["time"],
        "temperature_c": hourly_data["temperature_2m"],
        "humidity_pct": hourly_data["relative_humidity_2m"],
        "rain": hourly_data["rain"]
    })
    df["city"] = "Hyderabad"
    
    print("--- API Connection Successful ---")
    print(df.head(10))
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")