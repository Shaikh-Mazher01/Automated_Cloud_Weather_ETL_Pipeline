import sys
import os
import pandas as pd
from datetime import datetime
from extract_weather import extract_all_cities
from create_db import load_to_sqlite
from verify_data import analyze_and_export_weather_data

DB_PATH = os.getenv("DB_PATH", "weather_database.db")

def run_pipeline():
    print("Starting Weather ETL Pipeline...")
    
    try:
        # Step 1: Extraction
        raw_df = extract_all_cities()
        initial_count = len(raw_df)
        
        # Step 2: Strict Deduplication & Ingestion Timestamp
        raw_df["record_timestamp"] = pd.to_datetime(raw_df["record_timestamp"])
        clean_df = raw_df.drop_duplicates(subset=["city", "record_timestamp"], keep="last").copy()
        clean_df["ingested_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        dedup_count = len(clean_df)
        skipped_duplicates = initial_count - dedup_count
        
        # Step 3: SQLite Idempotent Load
        final_db_count = load_to_sqlite(clean_df, DB_PATH)
        
        # Step 4: Full Export from SQLite Source of Truth
        analyze_and_export_weather_data()
        
        print("\n--- INGESTION COMPLETE ---")
        print(f"Total Processed      : {dedup_count}")
        print(f"Duplicates Skipped   : {skipped_duplicates}")
        print(f"Database Total Rows  : {final_db_count}")
        
    except Exception as e:
        print(f"\n[!] PIPELINE FAILED: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()
