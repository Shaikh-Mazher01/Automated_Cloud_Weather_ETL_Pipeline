import os
import sqlite3
import pandas as pd
import pytest
from extract_weather import fetch_weather_data
from load_weather import load_csv_to_sqlite

# --- FIXTURE SETUP ---
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

# --- TESTS ---
def test_api_fetch_success():
    """Verify Open-Meteo API payload structure."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 17.3850,
        "longitude": 78.4867,
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m"
    }
    data = fetch_weather_data(url, params)
    
    assert "hourly" in data, "API response missing 'hourly' key."
    assert "temperature_2m" in data["hourly"], "Hourly data missing 'temperature_2m'."

def test_sqlite_deduplication(memory_db):
    """Verify unique constraint deduplication using fixture-managed database."""
    cursor = memory_db.cursor()
    record = ("Hyderabad", "2026-08-28T00:00", 28.5, 75.0, 12.0, "2026-08-28T10:00:00")
    
    # First insertion
    cursor.execute("""
        INSERT OR IGNORE INTO weather_forecasts 
        (city, record_timestamp, temperature_c, humidity_pct, wind_speed_kmh, ingested_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, record)
    assert cursor.rowcount == 1
    
    # Duplicate insertion attempt
    cursor.execute("""
        INSERT OR IGNORE INTO weather_forecasts 
        (city, record_timestamp, temperature_c, humidity_pct, wind_speed_kmh, ingested_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, record)
    assert cursor.rowcount == 0  # Deduplication successful

def test_load_csv_to_sqlite_end_to_end(tmp_path, monkeypatch):
    """Verify end-to-end load function reading a mock CSV into SQLite."""
    # Create temporary CSV snapshot
    csv_file = tmp_path / "test_weather.csv"
    df = pd.DataFrame([{
        "city": "Hyderabad",
        "record_timestamp": "2026-08-28T01:00",
        "temperature_c": 29.0,
        "humidity_pct": 70.0,
        "wind_speed_kmh": 10.0,
        "ingested_at": "2026-08-28T10:00:00"
    }])
    df.to_csv(csv_file, index=False)
    
    # Point DB_NAME to a temporary SQLite database
    db_file = tmp_path / "test_weather.db"
    monkeypatch.setattr("load_weather.DB_NAME", str(db_file))
    
    # Initialize schema
    conn = sqlite3.connect(db_file)
    conn.execute("""
        CREATE TABLE weather_forecasts (
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
    conn.close()
    
    # Run end-to-end ingestion function
    load_csv_to_sqlite(str(csv_file))
    
    # Verify data landed in database
    conn = sqlite3.connect(db_file)
    rows = conn.execute("SELECT * FROM weather_forecasts").fetchall()
    conn.close()
    
    assert len(rows) == 1
    assert rows[0][1] == "Hyderabad"
