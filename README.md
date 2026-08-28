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
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI/CD automation workflow
├── raw_data/                  # Local landing directory for API CSV snapshots
├── temp_download/             # Staging directory for cloud blob downloads
├── .env.example               # Template for required environment variables
├── .gitignore                 # Excludes local artifacts, secrets, and DBs
├── create_db.py               # SQL database schema initialization script
├── extract_weather.py         # API extraction with retries & Azure Blob upload
├── load_weather.py            # Azure Blob download & SQL loading module
├── main_pipeline.py           # Master ETL pipeline orchestrator & logger
├── requirements.txt           # Python dependency list for environment replication
├── test_pipeline.py           # Automated Pytest suite for API & data contracts
└── verify_data.py             # SQL analytical verification & query script
```
## How to Run

### 1. Environment Setup
Clone the repository, create a Python virtual environment, and install dependencies:

```bash
# Clone the repository
git clone https://github.com/Shaikh-Mazher01/Automated_Cloud_Weather_ETL_Pipeline.git
cd Automated_Cloud_Weather_ETL_Pipeline

# Create and activate virtual environment (Windows PowerShell)
py -m venv etl_env
.\etl_env\Scripts\activate

# Install required dependencies
pip install -r requirements.txt

```
### 2. Environment Configuration
Copy the example environment file and configure it:

```bash
cp .env.example .env
```
(Default values work out-of-the-box with Azurite's development storage.)


### 3. Start Azure Blob Emulator (Azurite)
Requires Node.js. Install and run Azurite in a separate terminal:
```bash
npm install -g azurite
azurite --silent --location ./azurite-data
```

### 4. Initialize the Database
```bash
python create_db.py
```

### 5. Run the Full Pipeline
```bash
python main_pipeline.py
```

### 6. Verify Ingested Data (optional)
```bash
python verify_data.py
```

### 7. Run Tests (optional)
```
pytest
