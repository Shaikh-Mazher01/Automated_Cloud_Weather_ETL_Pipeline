import sqlite3
import pandas as pd

DB_NAME = "weather_database.db"

def analyze_weather_data():
    """Runs analytical SQL queries against the ingested weather database."""
    conn = sqlite3.connect(DB_NAME)
    
    print("==========================================")
    print("    WEATHER DATABASE ANALYTICS REPORT     ")
    print("==========================================")
    
    # 1. Total Rows & Unique Cities
    summary_query = """
    SELECT 
        COUNT(*) AS total_records,
        COUNT(DISTINCT city) AS unique_cities,
        MIN(record_timestamp) AS earliest_record,
        MAX(record_timestamp) AS latest_record
    FROM weather_forecasts;
    """
    df_summary = pd.read_sql_query(summary_query, conn)
    print("\n--- Summary Metrics ---")
    print(df_summary.to_string(index=False))
    
    # 2. Daily Weather Statistics (Aggregations)
    stats_query = """
    SELECT 
        city,
        DATE(record_timestamp) AS forecast_date,
        ROUND(AVG(temperature_c), 2) AS avg_temp_c,
        ROUND(MAX(temperature_c), 2) AS max_temp_c,
        ROUND(MIN(temperature_c), 2) AS min_temp_c,
        ROUND(AVG(humidity_pct), 1) AS avg_humidity_pct,
        ROUND(MAX(wind_speed_kmh), 2) AS max_wind_kmh
    FROM weather_forecasts
    GROUP BY city, forecast_date
    ORDER BY forecast_date ASC
    LIMIT 5;
    """
    df_stats = pd.read_sql_query(stats_query, conn)
    print("\n--- Daily Forecast Aggregations (First 5 Days) ---")
    print(df_stats.to_string(index=False))
    
    conn.close()

if __name__ == "__main__":
    analyze_weather_data()