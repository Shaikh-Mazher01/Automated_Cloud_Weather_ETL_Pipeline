import os
import sqlite3
import pandas as pd

DB_NAME = os.getenv("DB_PATH", "weather_database.db")

def analyze_and_export_weather_data():
    """Queries SQLite weather database and exports complete multi-city dataset for Power BI."""
    conn = sqlite3.connect(DB_NAME)
    
    print("==========================================")
    print("     WEATHER DATABASE ANALYTICS REPORT    ")
    print("==========================================")
    
    raw_hourly_query = """
    SELECT 
        city,
        record_timestamp,
        temperature_c,
        humidity_pct,
        wind_speed_kmh,
        precipitation_mm,
        feels_like_c,
        uv_index,
        ingested_at
    FROM weather_forecasts
    ORDER BY record_timestamp ASC, city ASC;
    """
    df_raw = pd.read_sql_query(raw_hourly_query, conn)
    
    os.makedirs("raw_data", exist_ok=True)
    hourly_export_path = os.path.join("raw_data", "bi_hourly_raw.csv")
    df_raw.to_csv(hourly_export_path, index=False)
    
    city_count = df_raw["city"].nunique() if not df_raw.empty else 0
    print(f"\n[+] Full dataset exported ({len(df_raw)} records across {city_count} cities): {hourly_export_path}")
    
    conn.close()
    return df_raw

if __name__ == "__main__":
    analyze_and_export_weather_data()
