import os
import pandas as pd
from datetime import datetime
from extract_weather import extract_all_cities
from create_db import load_to_sqlite

OUTPUT_DIR = "raw_data"
CSV_PATH = os.path.join(OUTPUT_DIR, "bi_hourly_raw.csv")
DB_PATH = "weather_database.db"

def run_pipeline():
    print("Starting Weather ETL Pipeline...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Step 1: Extraction
    raw_df = extract_all_cities()
    initial_count = len(raw_df)
    
    # Step 2: Strict Deduplication & Ingestion Timestamp
    raw_df["record_timestamp"] = pd.to_datetime(raw_df["record_timestamp"])
    clean_df = raw_df.drop_duplicates(subset=["city", "record_timestamp"], keep="last").copy()
    
    # Add ingested_at column to satisfy SQLite NOT NULL constraint
    clean_df["ingested_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    dedup_count = len(clean_df)
    skipped_duplicates = initial_count - dedup_count
    
    # Step 3: SQLite Idempotent Load
    final_db_count = load_to_sqlite(clean_df, DB_PATH)
    
    # Step 4: Overwrite CSV Export
    clean_df.to_csv(CSV_PATH, index=False, mode="w")
    
    print("\n--- INGESTION COMPLETE ---")
    print(f"Total Records Processed : {dedup_count}")
    print(f"New Rows Inserted      : {dedup_count}")
    print(f"Duplicates Skipped     : {skipped_duplicates}")
    print(f"Database Total Rows    : {final_db_count}")
    print(f"CSV Exported To        : {CSV_PATH}")

if __name__ == "__main__":
    run_pipeline()
