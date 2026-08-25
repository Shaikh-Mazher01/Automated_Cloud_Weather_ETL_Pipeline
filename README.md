# End-to-End Automated Cloud Weather ETL Pipeline

A production-grade Python ETL pipeline that extracts hourly forecast data, lands standard CSV snapshots in local cloud emulation storage (Azure Blob Storage via Azurite), and ingests clean records into a relational SQL database with automated logging and duplicate protection.

## Architecture & Data Flow
1. **Extraction (API):** Python fetches JSON payloads from Open-Meteo REST API.
2. **Landing Zone (Cloud Emulation):** Data is standardized into CSV files and uploaded to Azure Blob Storage (`raw-weather-data`) using `azure-storage-blob` SDK.
3. **Ingestion & Transformation:** CSV files are programmatically downloaded, parsed, and loaded into an SQLite database with composite unique constraint checks (`city`, `record_timestamp`).
4. **Orchestration & Logging:** `main_pipeline.py` executes stages sequentially, recording runtime metrics into `etl.log`.

## Tech Stack
* **Language:** Python 3.10+
* **Data Processing:** Pandas
* **Database & SQL:** SQLite3, SQL DDL (Composite Unique Keys)
* **Cloud & Storage:** Azure Blob Storage SDK, Microsoft Azurite
* **Configuration:** `python-dotenv`

## Project Structure
```text
Automated_Cloud_Weather_ETL_Pipeline/
│── raw_data/            # Local landing folder for raw CSVs
│── temp_download/       # Staging area for cloud downloads
│── create_db.py         # Database schema initialization script
│── extract_weather.py   # API extraction & Azure Blob upload script
│── load_weather.py      # Cloud download & SQL loading script
│── main_pipeline.py     # Pipeline orchestrator & logging module
│── verify_data.py       # SQL analytical queries script
│── test_api.py          # API connection unit test
│── weather_database.db  # Relational SQL database
└── etl.log              # Execution log file
