import os
import sqlite3
import pandas as pd
import pytest
from extract_weather import fetch_weather_data, CITIES
from load_weather import load_csv_to_sqlite

@pytest.fixture
def memory_db():
    """Provides an isolated in-memory SQLite database matching production schema."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_forecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            record_timestamp TEXT NOT NULL,
            temperature_c REAL,
            humidity_pct REAL,
            wind_speed_kmh REAL,
            ingested_at TEXT NOT NULL,
            UNIQUE(city, record_timestamp)
        )
    """)
    conn.commit()
    yield conn
    conn.close()

def test_api_multi_city_fetch_success():
    """Verify Open-Meteo multi-city archive API response structure."""
    url = "https://archive-api.open-meteo.com/v1/archive"
    lats = [str(coord[0]) for coord in CITIES.values()]
    lons = [str(coord[1]) for coord in CITIES.values()]
    
    params = {
        "latitude": ",".join(lats),
        "longitude": ",".join(lons),
        "past_days": 2,
        "hourly": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m"],
        "timezone": "auto"
    }
    data = fetch_weather_data(url, params)
    
    assert isinstance(data, list), "Multi-location API should return a list of JSON payloads."
    assert len(data) == len(CITIES), "API payload count does not match city count."

def test_sqlite_deduplication(memory_db):
    """Verify unique composite constraint deduplication across cities."""
    cursor = memory_db.cursor()
    record1 = ("Hyderabad", "2026-08-28T00:00", 28.5, 75.0, 12.0, "2026-08-28T10:00:00")
    record2 = ("Mumbai", "2026-08-28T00:00", 30.0, 85.0, 18.0, "2026-08-28T10:00:00")
    
    cursor.execute("""
        INSERT OR IGNORE INTO weather_forecasts 
        (city, record_timestamp, temperature_c, humidity_pct, wind_speed_kmh, ingested_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, record1)
    assert cursor.rowcount == 1
    
    # Same timestamp, different city (should insert)
    cursor.execute("""
        INSERT OR IGNORE INTO weather_forecasts 
        (city, record_timestamp, temperature_c, humidity_pct, wind_speed_kmh, ingested_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, record2)
    assert cursor.rowcount == 1

    # Exact duplicate record (should be ignored)
    cursor.execute("""
        INSERT OR IGNORE INTO weather_forecasts 
        (city, record_timestamp, temperature_c, humidity_pct, wind_speed_kmh, ingested_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, record1)
    assert cursor.rowcount == 0
