import requests
import pandas as pd

def fetch_weather(latitude, longitude, days=16):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum"
        ],
        "forecast_days": days,
        "timezone": "auto"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    daily = response.json()["daily"]

    df = pd.DataFrame({
        "date": daily["time"],
        "temp_max": daily["temperature_2m_max"],
        "temp_min": daily["temperature_2m_min"],
        "rainfall": daily["precipitation_sum"]
    })

    return df
