import pytest
from extract_weather import fetch_weather_data

def test_api_fetch_success():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 17.3850,
        "longitude": 78.4867,
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m"
    }
    data = fetch_weather_data(url, params)
    assert "hourly" in data
    assert "temperature_2m" in data["hourly"]
    assert len(data["hourly"]["temperature_2m"]) > 0