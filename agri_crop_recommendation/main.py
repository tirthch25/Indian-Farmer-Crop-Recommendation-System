"""
Quick sanity test — runs a single recommendation against MH_PUNE.
Run from the agri_crop_recommendation/ directory: python main.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from src.weather.fetcher import fetch_weather
from src.ml.pipeline import add_agri_features
from src.weather.forecast import forecast_days_17_90
from src.services.recommender import recommend_crops

LAT, LON = 18.5204, 73.8567   # Pune

weather = fetch_weather(LAT, LON)
weather = add_agri_features(weather)

forecast = forecast_days_17_90(weather, region_id="MH_PUNE")
print("\n📊 Days 17–90 Weather Outlook")
print(f"  Avg temp : {forecast.get('expected_avg_temp')}°C")
print(f"  Rainfall : {forecast.get('expected_rainfall_mm')} mm")
print(f"  Source   : {forecast.get('forecast_source')}")

results = recommend_crops(region_id="MH_PUNE", irrigation_available=True, planning_days=90)
print("\n🌱 Top Recommended Crops:\n")
for r in results[:5]:
    print(f"  {r.get('rank', '-')}. {r.get('crop', r.get('crop_id', ''))}  — score: {r.get('score', 'N/A')}")
