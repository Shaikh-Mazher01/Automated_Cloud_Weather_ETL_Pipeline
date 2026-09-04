# Automated Weather ETL & Executive Climate Risk Analytics

An end-to-end cloud data pipeline and Power BI dashboard built to monitor bi-hourly operational weather hazards across 8 major Indian metropolises (Delhi, Mumbai, Kolkata, Chennai, Bengaluru, Hyderabad, Ahmedabad, and Jaipur).

The goal of this project is to convert raw, continuous meteorological measurements into clear risk indicators—specifically around thermal stress, extreme precipitation, and sustained wind exposure.

---

## Data Architecture & Workflow

1. **Extraction (`extract_weather.py`)**: Fetches rolling 30-day bi-hourly meteorological observations from the **Open-Meteo Archive API** with exponential backoff handling via `tenacity`.
2. **Transform & Deduplicate (`main_pipeline.py`)**: Enforces strict `(city, record_timestamp)` composite primary key deduplication and injects ISO-formatted ingestion timestamps.
3. **Storage (`create_db.py`)**: Staging-table pattern with idempotent `INSERT OR REPLACE` operations into an **ACID-compliant SQLite database**.
4. **Export & Analytics (`verify_data.py`)**: Exports complete multi-metric historical data (`bi_hourly_raw.csv`) for DAX modeling in Power BI.

---

## Tech Stack
* **Language**: Python 3.10 (Pandas, Requests, Tenacity, Pytest)
* **Database**: SQLite3
* **Analytics & Visualization**: Power BI Desktop, DAX, Power Query
* **CI/CD**: GitHub Actions (Automated Pytest Suite)

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
└── Weather_Dashboard.pbix     # Complete interactive Power BI dashboard file.
└── Dashboard.pdf              # High-resolution PDF export for executive review.
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
```bash
pytest
```

## Dashboard Features

* **Dynamic Time Windowing**: Seamless switching across rolling continuous time ranges (7, 15, and 30-day windows) without date-gapping or truncation.
* **30-Day Climate & Monsoon Trends**: Dual-axis continuous timeline tracking daily precipitation overlayed with average feels-like temperature.
* **Diurnal Weather Progression**: Hourly profile isolating diurnal spikes in temperature and heavy rain distribution across all monitored cities.
* **Executive Metrics**: Formatted DAX measures ensuring unit-inclusive KPI cards (e.g., `mm`, `hrs`, `%`).

---
