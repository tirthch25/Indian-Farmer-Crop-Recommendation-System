"""
Generate synthetic historical weather data for testing.

Creates realistic weather patterns for all supported Indian agricultural regions
covering 10 years (2014-2024) with seasonal variations.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.regions import RegionManager
from src.data.historical_store import HistoricalDataStore


def generate_weather_for_region(
    region_id: str,
    latitude: float,
    climate_zone: str,
    start_year: int = 2014,
    end_year: int = 2024
) -> pd.DataFrame:
    """
    Generate synthetic weather data for a region with realistic patterns.
    
    Args:
        region_id: Region identifier
        latitude: Latitude for seasonal patterns
        climate_zone: Climate classification
        start_year: Start year
        end_year: End year (inclusive)
        
    Returns:
        DataFrame with daily weather data
    """
    print(f"Generating data for {region_id} ({climate_zone})...")
    
    # Generate date range
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    dates = pd.date_range(start_date, end_date, freq='D')
    
    # Initialize arrays
    n_days = len(dates)
    temp_max = np.zeros(n_days)
    temp_min = np.zeros(n_days)
    rainfall = np.zeros(n_days)
    humidity = np.zeros(n_days)
    wind_speed = np.zeros(n_days)
    
    # Base temperature parameters by climate zone
    if climate_zone == "Semi-Arid":
        base_temp = 28.0
        temp_amplitude = 8.0
        base_humidity = 45.0
        monsoon_rainfall_mean = 5.0
    else:  # Sub-Humid
        base_temp = 26.0
        temp_amplitude = 7.0
        base_humidity = 60.0
        monsoon_rainfall_mean = 7.0
    
    for i, date in enumerate(dates):
        day_of_year = date.timetuple().tm_yday
        
        # Seasonal temperature variation (sinusoidal)
        seasonal_temp = base_temp + temp_amplitude * np.sin(2 * np.pi * (day_of_year - 80) / 365)
        
        # Add random daily variation
        daily_variation = np.random.normal(0, 2.0)
        temp_max[i] = seasonal_temp + 5 + daily_variation
        temp_min[i] = seasonal_temp - 5 + daily_variation * 0.5
        
        # Monsoon season (June-September: days 152-273)
        month = date.month
        is_monsoon = month in [6, 7, 8, 9]
        is_winter = month in [12, 1, 2]
        
        if is_monsoon:
            # Monsoon rainfall (higher probability and amount)
            if np.random.random() < 0.4:  # 40% chance of rain
                rainfall[i] = np.random.exponential(monsoon_rainfall_mean)
            humidity[i] = base_humidity + 25 + np.random.normal(0, 5)
        elif is_winter:
            # Winter (dry season)
            if np.random.random() < 0.05:  # 5% chance of rain
                rainfall[i] = np.random.exponential(2.0)
            humidity[i] = base_humidity - 10 + np.random.normal(0, 5)
        else:
            # Other seasons
            if np.random.random() < 0.15:  # 15% chance of rain
                rainfall[i] = np.random.exponential(3.0)
            humidity[i] = base_humidity + np.random.normal(0, 8)
        
        # Wind speed (slightly higher in monsoon)
        if is_monsoon:
            wind_speed[i] = np.random.gamma(3, 2) + 5
        else:
            wind_speed[i] = np.random.gamma(2, 1.5) + 2
        
        # Ensure realistic bounds
        temp_max[i] = np.clip(temp_max[i], 15, 45)
        temp_min[i] = np.clip(temp_min[i], 5, 35)
        rainfall[i] = np.clip(rainfall[i], 0, 150)
        humidity[i] = np.clip(humidity[i], 20, 95)
        wind_speed[i] = np.clip(wind_speed[i], 0, 40)
    
    # Create DataFrame
    df = pd.DataFrame({
        'region_id': region_id,
        'date': dates,
        'temp_max': np.round(temp_max, 2),
        'temp_min': np.round(temp_min, 2),
        'rainfall': np.round(rainfall, 2),
        'humidity': np.round(humidity, 2),
        'wind_speed': np.round(wind_speed, 2)
    })
    
    return df


def main():
    """Generate historical data for all regions."""
    print("=" * 60)
    print("Generating Historical Weather Data")
    print("=" * 60)
    
    # Load regions
    region_manager = RegionManager()
    regions = region_manager.get_all_regions()
    
    print(f"\nFound {len(regions)} regions to process")
    print(f"Generating data for years 2014-2024 (10 years)\n")
    
    # Initialize data store
    data_store = HistoricalDataStore()
    
    # Generate data for each region
    for region in regions:
        df = generate_weather_for_region(
            region_id=region.region_id,
            latitude=region.latitude,
            climate_zone=region.climate_zone,
            start_year=2014,
            end_year=2024
        )
        
        # Save by year
        for year in range(2014, 2025):
            year_data = df[df['date'].dt.year == year].copy()
            if len(year_data) > 0:
                data_store.save_historical_data(
                    region_id=region.region_id,
                    data=year_data,
                    year=year
                )
        
        print(f"  ✓ Saved {len(df)} records for {region.region_id}")
    
    print("\n" + "=" * 60)
    print("Data Generation Complete!")
    print("=" * 60)
    
    # Print summary
    print("\nData Coverage Summary:")
    for region in regions:
        coverage = data_store.get_data_coverage(region.region_id)
        if coverage['available']:
            print(f"  {region.region_id:15} {coverage['year_range']:15} "
                  f"{coverage['total_records']:6} records")
    
    print("\nHistorical data is ready for use!")


if __name__ == "__main__":
    main()
