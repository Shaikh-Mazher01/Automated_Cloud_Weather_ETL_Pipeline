# Automated Cloud Weather ETL & Executive Climate Risk Analytics

An automated Python ETL pipeline and Power BI dashboard built to monitor bi-hourly operational weather hazards across 8 major Indian metropolises (Delhi, Mumbai, Kolkata, Chennai, Bengaluru, Hyderabad, Ahmedabad, and Jaipur).

The goal of this project is to convert raw, continuous meteorological measurements into actionable operational indicators—specifically around thermal stress, extreme precipitation, and sustained wind exposure.

---

## Data Architecture & Workflow

1. **Extraction (`extract_weather.py`)**: Fetches a dynamic rolling 30-day bi-hourly window of meteorological observations from the **Open-Meteo Archive API** with exponential backoff retry handling via `tenacity`.
2. **Cloud Archival (`load_weather.py`)**: Streams per-run raw extract snapshots (`latest_extract.csv`) directly to **Azure Blob Storage** (`weather-raw-data` container) with automatic retries and graceful fallback to local-only mode if Azure credentials are unconfigured.
3. **Transform & Storage (`create_db.py`, `load_weather.py`)**: Enforces strict `(city, record_timestamp)` composite primary key deduplication, injects ISO-formatted ingestion timestamps, and performs idempotent `INSERT OR REPLACE` operations into an **ACID-compliant SQLite database**.
4. **Analytics Export (`verify_data.py`)**: Queries complete cumulative history from SQLite and exports a clean dataset (`bi_hourly_raw.csv`) containing all weather metrics (`feels_like_c`, `precipitation_mm`, `uv_index`, `wind_speed_kmh`, etc.) for DAX modeling in Power BI.

---

## Core Operational Thresholds

* **Thermal Stress**: Hourly windows where feels-like temperature exceeds **≥ 35°C**.
* **Heavy Rain Exposure**: Cumulative rainfall volume where precipitation rates hit **≥ 2.5 mm/h**.
* **Sustained Wind Advisory**: Continuous monitoring of sustained wind speed **≥ 25 km/h**.
* **Risk Score Scaling**: Normalized matrix scoring Thermal Stress Score (0–6) against Rainfall Intensity Index (0–6).

---

## Tech Stack
* **Language**: Python 3.10 (Pandas, Requests, Tenacity, Pytest, Python-Dotenv)
* **Cloud Storage**: Azure Blob Storage (Azure SDK)
* **Database**: SQLite3
* **Analytics & Visualization**: Power BI Desktop, DAX, Power Query
* **CI/CD**: GitHub Actions (Automated Pytest Suite)

---

## Project Structure
```text
Automated_Cloud_Weather_ETL_and_Risk_Analysis/
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI/CD automation workflow
├── raw_data/                  # Local landing directory for staging and export CSVs
├── .env.example               # Template for required environment variables
├── .gitignore                 # Excludes local artifacts, secrets, and DBs
├── create_db.py               # SQL database schema initialization script
├── extract_weather.py         # API extraction module with dynamic rolling dates
├── load_weather.py            # Azure Blob upload & SQLite idempotent loading module
├── main_pipeline.py           # Master ETL pipeline orchestrator with error logging
├── requirements.txt           # Python dependency list for environment replication
├── test_pipeline.py           # Automated Pytest suite for API & data contracts
├── verify_data.py             # SQLite analytics verification & Power BI CSV exporter
├── Weather_Dashboard.pbix     # Complete interactive Power BI dashboard file
└── Dashboard.pdf              # High-resolution PDF export for executive review
```
## How to Run

### 1. Environment Setup
Clone the repository, create a Python virtual environment, and install dependencies:

```bash
# Clone the repository
git clone https://github.com/Shaikh-Mazher01/Automated_Cloud_Weather_ETL_and_Risk_Analysis.git
cd Automated_Cloud_Weather_ETL_and_Risk_Analysis

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
```bash
pytest
```

## Dashboard Features

* **Dynamic Time Windowing**: Seamless switching across rolling continuous time ranges (7, 15, and 30-day windows) without date-gapping or truncation.
* **30-Day Climate & Monsoon Trends**: Dual-axis continuous timeline tracking daily precipitation overlayed with average feels-like temperature.
* **Diurnal Weather Progression**: Hourly profile isolating diurnal spikes in temperature and heavy rain distribution across all monitored cities.
* **Executive Metrics**: Formatted DAX measures ensuring unit-inclusive KPI cards (e.g., `mm`, `hrs`, `%`).

---
