import sqlite3
import os

# --- CONFIGURATION ---
DB_NAME = "weather_database.db"

def create_weather_table():
    """Initializes the database and creates the weather table schema."""
    conn = None
    try:
        # Connect to SQLite database (creates the file if it doesn't exist)
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # DDL Query: Create structured table with constraints
        create_table_query = """
        CREATE TABLE IF NOT EXISTS weather_forecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city VARCHAR(50) NOT NULL,
            record_timestamp DATETIME NOT NULL,
            temperature_c REAL NOT NULL,
            humidity_pct INTEGER NOT NULL,
            wind_speed_kmh REAL NOT NULL,
            ingested_at DATETIME NOT NULL,
            CONSTRAINT unique_city_record UNIQUE (city, record_timestamp)
        );
        """
        
        cursor.execute(create_table_query)
        conn.commit()
        
        print(f"--- SUCCESS ---")
        print(f"Database '{DB_NAME}' initialized.")
        print("Table 'weather_forecasts' is ready with primary keys and constraints!")
        
    except sqlite3.Error as e:
        print(f"--- FAILURE --- Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_weather_table()