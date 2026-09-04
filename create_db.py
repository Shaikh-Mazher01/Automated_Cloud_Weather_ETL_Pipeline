import sqlite3
import pandas as pd

def initialize_database(db_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_forecasts (
            city TEXT NOT NULL,
            record_timestamp DATETIME NOT NULL,
            temperature_c REAL,
            humidity_pct REAL,
            wind_speed_kmh REAL,
            precipitation_mm REAL,
            feels_like_c REAL,
            uv_index REAL,
            ingested_at DATETIME,
            PRIMARY KEY (city, record_timestamp)
        );
    """)
    conn.commit()
    conn.close()

def load_to_sqlite(df: pd.DataFrame, db_path: str = "weather_database.db"):
    initialize_database(db_path)
    conn = sqlite3.connect(db_path)
    
    df.to_sql("staging_weather", conn, if_exists="replace", index=False)
    
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO weather_forecasts 
        (city, record_timestamp, temperature_c, humidity_pct, wind_speed_kmh, precipitation_mm, feels_like_c, uv_index, ingested_at)
        SELECT city, record_timestamp, temperature_c, humidity_pct, wind_speed_kmh, precipitation_mm, feels_like_c, uv_index, ingested_at
        FROM staging_weather;
    """)
    
    cursor.execute("DROP TABLE staging_weather;")
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM weather_forecasts;")
    total_db_rows = cursor.fetchone()[0]
    conn.close()
    
    return total_db_rows
