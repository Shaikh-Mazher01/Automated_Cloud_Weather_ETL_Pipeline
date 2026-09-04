import os
import sqlite3
import pandas as pd
import pytest
from extract_weather import fetch_city_weather, CITIES

@pytest.fixture
def memory_db():
    """Provides an isolated in-memory SQLite database matching production schema."""
    conn = sqlite3.connect(":memory:")
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
        )
    """)
    conn.commit()
    yield conn
    conn.close()

def test_api_city_fetch_success():
    """Verify Open-Meteo single-city archive API response structure and returned DataFrame columns."""
    city_name = "Hyderabad"
    coords = CITIES[city_name]
    
    # Fetch data using the actual function signature from extract_weather.py
    df = fetch_city_weather(city_name, coords["lat"], coords["lon"])
    
    assert isinstance(df, pd.DataFrame), "Extraction should return a pandas DataFrame."
    assert not df.empty, "DataFrame should not be empty."
    
    expected_columns = {
        "city", "record_timestamp", "temperature_c", "humidity_pct",
        "wind_speed_kmh", "precipitation_mm", "feels_like_c", "uv_index"
    }
    assert expected_columns.issubset(set(df.columns)), "DataFrame is missing expected weather metric columns."
    assert (df["city"] == city_name).all(), "City column values do not match requested city."

def test_sqlite_deduplication(memory_db):
    """Verify unique composite primary key (city, record_timestamp) deduplication."""
    cursor = memory_db.cursor()
    record1 = ("Hyderabad", "2026-08-28T00:00:00", 28.5, 75.0, 12.0, 0.0, 31.0, 0.0, "2026-08-28T10:00:00")
    record2 = ("Mumbai", "2026-08-28T00:00:00", 30.0, 85.0, 18.0, 2.5, 34.0, 0.0, "2026-08-28T10:00:00")
    
    cursor.execute("""
        INSERT OR IGNORE INTO weather_forecasts 
        (city, record_timestamp, temperature_c, humidity_pct, wind_speed_kmh, precipitation_mm, feels_like_c, uv_index, ingested_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, record1)
    assert cursor.rowcount == 1
    
    # Same timestamp, different city (should insert)
    cursor.execute("""
        INSERT OR IGNORE INTO weather_forecasts 
        (city, record_timestamp, temperature_c, humidity_pct, wind_speed_kmh, precipitation_mm, feels_like_c, uv_index, ingested_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, record2)
    assert cursor.rowcount == 1

    # Duplicate record for same city and timestamp (should be ignored by PRIMARY KEY)
    cursor.execute("""
        INSERT OR IGNORE INTO weather_forecasts 
        (city, record_timestamp, temperature_c, humidity_pct, wind_speed_kmh, precipitation_mm, feels_like_c, uv_index, ingested_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, record1)
    assert cursor.rowcount == 0
