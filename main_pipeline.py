import sys
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

from extract_weather import extract_all_cities
from create_db import init_sqlite_db
from load_weather import load_data_to_db, upload_to_azure_blob
from verify_data import analyze_and_export_weather_data

DB_PATH = os.getenv("DB_PATH", "weather_database.db")

def run_pipeline():
    print("Starting Weather ETL Pipeline...")
    
    try:
        # Step 1: Initialize Database Schema
        init_sqlite_db(DB_PATH)

        # Step 2: Extraction
        raw_df = extract_all_cities()
        initial_count = len(raw_df)
        
        # Step 3: Transform & Deduplicate
        raw_df["record_timestamp"] = pd.to_datetime(raw_df["record_timestamp"])
        clean_df = raw_df.drop_duplicates(subset=["city", "record_timestamp"], keep="last").copy()
        clean_df["ingested_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        dedup_count = len(clean_df)
        skipped_duplicates = initial_count - dedup_count
        
        # Save staging extract
        os.makedirs("raw_data", exist_ok=True)
        raw_file_path = os.path.join("raw_data", "latest_extract.csv")
        clean_df.to_csv(raw_file_path, index=False)

        # Step 4: Azure Blob Storage Upload
        blob_name = f"raw_weather_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        upload_to_azure_blob(raw_file_path, blob_name)

        # Step 5: Database Load
        final_db_count = load_data_to_db(clean_df, DB_PATH)
        
        # Step 6: Export for Power BI
        analyze_and_export_weather_data()
        
        print("\n--- INGESTION COMPLETE ---")
        print(f"Processed Rows       : {dedup_count}")
        print(f"Duplicates Skipped   : {skipped_duplicates}")
        print(f"Database Total Rows  : {final_db_count}")
        
    except Exception as e:
        print(f"\n[!] PIPELINE FAILED: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()
