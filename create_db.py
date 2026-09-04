import os
import sqlite3

DB_NAME = os.getenv("DB_PATH", "weather_database.db")

def init_sqlite_db(db_path: str = DB_NAME) -> None:
    """Initializes the SQLite weather database schema if it does not exist."""
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
        )
    """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_sqlite_db()
    print(f"[+] SQLite database schema initialized at: {DB_NAME}")
