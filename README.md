# Automated Cloud Weather ETL & Executive Climate Risk Analytics

An end-to-end pipeline that pulls rolling 30-day weather data for 8 major Indian cities — Delhi, Mumbai, Kolkata, Chennai, Bengaluru, Hyderabad, Ahmedabad, and Jaipur — and turns it into a Power BI dashboard for spotting heat, rain, and wind risk.

---
## How it works
 
1. **Extract** — `extract_weather.py` pulls hourly temperature, humidity, wind speed, precipitation, feels-like temperature, and UV index from the **Open-Meteo Archive API** for each city, covering the trailing 30 days. It's wrapped in retry logic (via `tenacity`) with exponential backoff, so a single flaky API call doesn't kill the whole run.
2. **Store** — Raw extracts are deduplicated on `(city, timestamp)` and loaded into a local **SQLite** database (`create_db.py`, `load_weather.py`). Every run also uploads a timestamped CSV snapshot to **Azure Blob Storage** as a raw-layer backup.
3. **Verify & export** — `verify_data.py` queries the SQLite store and exports a clean CSV that Power BI reads from.
4. **Visualize** — `Weather_Dashboard.pbix` turns that export into a dashboard.

---


## Tech
 
Python (requests, pandas, tenacity), SQLite, Azure Blob Storage, Power BI / DAX, GitHub Actions, pytest.

---

## Project Structure
```text
Automated_Cloud_Weather_ETL_and_Risk_Analysis/
├── .github/
│   └── workflows/
│       └── ci.yml             # CI pipeline (GitHub Actions)
├── raw_data/                  # Local landing directory
├── .env.example               # Template for required environment variables
├── .gitignore                 # Excludes local artifacts, secrets, and DBs
├── create_db.py               # SQLite schema setup
├── extract_weather.py         # Open-Meteo API extraction with retries
├── load_weather.py            # Azure Blob upload + SQLite load
├── main_pipeline.py           # Orchestrates the full run
├── requirements.txt           # Python dependency
├── test_pipeline.py           # Pytest suite
├── verify_data.py             # Query + export for Power BI
├── Weather_Dashboard.pbix     # Power BI dashboard
└── Dashboard.pdf              # Static export of the dashboard
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
---
## Dashboard highlights
 
- Dual-axis chart tracking daily precipitation against average feels-like temperature
- Hour-by-hour view of temperature and rain spikes across all 8 cities
- KPI cards with correct units baked in (mm, hrs, %) via DAX
---
