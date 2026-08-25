import logging
import os
from datetime import datetime
from extract_weather import fetch_and_save_weather
from load_weather import download_latest_blob_csv, load_csv_to_sqlite

# --- LOGGING CONFIGURATION ---
LOG_FILE = "etl.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Print logs to console as well
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

def run_pipeline():
    """Orchestrates the entire extraction, upload, download, and database ingestion workflow."""
    pipeline_start = datetime.now()
    logging.info("==========================================")
    logging.info("STARTING END-TO-END WEATHER ETL PIPELINE")
    logging.info("==========================================")
    
    try:
        # --- STAGE 1: EXTRACTION & AZURE UPLOAD ---
        logging.info("STAGE 1: Fetching API data & uploading to Azure Blob Storage...")
        fetch_and_save_weather()
        logging.info("STAGE 1 COMPLETE: Data extracted and landed successfully.")
        
        # --- STAGE 2: CLOUD DOWNLOAD & SQL LOADING ---
        logging.info("STAGE 2: Downloading latest blob & ingesting into SQL Database...")
        latest_csv = download_latest_blob_csv()
        
        if latest_csv:
            load_csv_to_sqlite(latest_csv)
            logging.info("STAGE 2 COMPLETE: Database updated successfully.")
        else:
            logging.warning("STAGE 2 SKIPPED: No CSV file retrieved from cloud storage.")
            
        duration = (datetime.now() - pipeline_start).total_seconds()
        logging.info(f"--- ETL PIPELINE FINISHED SUCCESSFULLY IN {duration:.2f} SECONDS ---")
        
    except Exception as e:
        logging.error(f"--- PIPELINE FAILED WITH ERROR: {str(e)} ---", exc_info=True)

if __name__ == "__main__":
    run_pipeline()