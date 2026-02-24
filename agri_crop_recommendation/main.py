from src.weather.open_meteo import fetch_weather
from src.preprocessing.features import add_agri_features
from src.forecasting.medium_range import forecast_days_17_90
from src.recommendation.recommender import recommend_crops

LAT = 18.5204   # Pune
LON = 73.8567

weather = fetch_weather(LAT, LON)
weather = add_agri_features(weather)

forecast = forecast_days_17_90(weather)

print("\n📊 Days 17–90 Weather Outlook")
print(forecast)

results = recommend_crops(
    weather_df=weather,
    season="Rabi",
    irrigation_available=True
)

print("\n🌱 Recommended Crops:\n")
for r in results:
    print(r)
