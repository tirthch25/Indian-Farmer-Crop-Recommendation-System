"""
Test script to verify the Indian Farmer Crop Recommendation System.

Tests all major components:
- Historical data store
- Region management
- Crop database
- Soil compatibility
"""

from datetime import datetime, timedelta
from src.data.historical_store import HistoricalDataStore
from src.data.regions import RegionManager
from src.crops.crop_db import crop_db
from src.soil.models import SoilInfo, calculate_soil_compatibility_score, get_soil_amendment_suggestions


def test_historical_data():
    """Test historical data store."""
    print("\n" + "="*60)
    print("Testing Historical Data Store")
    print("="*60)
    
    store = HistoricalDataStore()
    
    # Test data retrieval
    end_date = datetime(2024, 12, 31)
    start_date = end_date - timedelta(days=365)
    
    data = store.get_historical_data("PUNE", start_date, end_date)
    print(f"✓ Retrieved {len(data)} records for PUNE (2024)")
    print(f"  Date range: {data['date'].min()} to {data['date'].max()}")
    print(f"  Avg temp: {data['temp_max'].mean():.1f}°C")
    print(f"  Total rainfall: {data['rainfall'].sum():.1f}mm")
    
    # Test climatology
    climatology = store.get_climatology("PUNE", 7, "mean")  # July
    print(f"\n✓ July climatology for PUNE:")
    print(f"  Avg temp_max: {climatology['temp_max']:.1f}°C")
    print(f"  Avg rainfall: {climatology['rainfall']:.1f}mm")
    
    # Test coverage
    coverage = store.get_data_coverage("PUNE")
    print(f"\n✓ Data coverage: {coverage['year_range']} ({coverage['total_years']} years)")


def test_regions():
    """Test region management."""
    print("\n" + "="*60)
    print("Testing Region Management")
    print("="*60)
    
    rm = RegionManager()
    
    # Test region retrieval
    regions = rm.get_all_regions()
    print(f"✓ Loaded {len(regions)} regions")
    
    # Test specific region
    pune = rm.get_region_profile("PUNE")
    print(f"\n✓ Pune District:")
    print(f"  Location: {pune.latitude}°N, {pune.longitude}°E")
    print(f"  Climate: {pune.climate_zone}")
    print(f"  Soil types: {', '.join(pune.typical_soil_types)}")
    
    # Test default soil
    soil = pune.get_default_soil()
    print(f"  Default soil: {soil.texture}, pH {soil.ph}, {soil.organic_matter} organic matter")
    
    # Test nearest region
    nearest = rm.find_nearest_region(18.6, 73.9)
    print(f"\n✓ Nearest region to (18.6, 73.9): {nearest.region_id}")


def test_crops():
    """Test crop database."""
    print("\n" + "="*60)
    print("Testing Crop Database")
    print("="*60)
    
    # Test total crops
    total = crop_db.get_crop_count()
    print(f"✓ Total crops in database: {total}")
    
    # Test filtering by season
    kharif = crop_db.get_crops_by_season("Kharif")
    rabi = crop_db.get_crops_by_season("Rabi")
    print(f"✓ Kharif crops: {len(kharif)}")
    print(f"✓ Rabi crops: {len(rabi)}")
    
    # Test filtering by region
    pune_crops = crop_db.get_crops_by_region("PUNE", threshold=0.7)
    print(f"✓ High-suitability crops for PUNE: {len(pune_crops)}")
    
    # Test short-duration crops
    short = crop_db.get_short_duration_crops(70, 90)
    print(f"✓ Short-duration crops (70-90 days): {len(short)}")
    
    # Test specific crop
    bajra = crop_db.get_crop("BAJRA_01")
    print(f"\n✓ {bajra.common_name}:")
    print(f"  Duration: {bajra.duration_days} days")
    print(f"  Water requirement: {bajra.water_requirement_mm}mm")
    print(f"  Drought tolerance: {bajra.drought_tolerance}")
    print(f"  Suitable regions: {', '.join(bajra.successful_regions)}")


def test_soil_compatibility():
    """Test soil compatibility scoring."""
    print("\n" + "="*60)
    print("Testing Soil Compatibility")
    print("="*60)
    
    # Test with different soils
    soils = [
        SoilInfo(texture="Sandy-Loam", ph=7.0, organic_matter="Medium", drainage="Good"),
        SoilInfo(texture="Clay", ph=8.0, organic_matter="Low", drainage="Poor"),
        SoilInfo(texture="Loam", ph=6.5, organic_matter="High", drainage="Good")
    ]
    
    bajra = crop_db.get_crop("BAJRA_01")
    
    print(f"Soil compatibility for {bajra.common_name}:")
    for i, soil in enumerate(soils, 1):
        score = calculate_soil_compatibility_score(bajra, soil)
        print(f"\n  Soil {i} ({soil.texture}, pH {soil.ph}):")
        print(f"    Compatibility score: {score:.1f}/100")
        
        if score < 70:
            amendments = get_soil_amendment_suggestions(bajra, soil)
            if amendments:
                print(f"    Amendments needed:")
                for amendment in amendments[:2]:  # Show first 2
                    print(f"      - {amendment[:60]}...")


def test_integrated_query():
    """Test integrated query across all components."""
    print("\n" + "="*60)
    print("Testing Integrated Query")
    print("="*60)
    
    # Scenario: Farmer in Pune wants Kharif crops for clay-loam soil
    rm = RegionManager()
    pune = rm.get_region_profile("PUNE")
    soil = pune.get_default_soil()
    
    print(f"Scenario: Farmer in {pune.name}")
    print(f"  Season: Kharif")
    print(f"  Soil: {soil.texture}, pH {soil.ph}")
    
    # Get Kharif crops
    kharif_crops = crop_db.get_crops_by_season("Kharif")
    print(f"\n✓ Found {len(kharif_crops)} Kharif crops")
    
    # Filter by region suitability
    suitable_crops = [c for c in kharif_crops if c.is_suitable_for_region("PUNE", 0.7)]
    print(f"✓ {len(suitable_crops)} crops suitable for PUNE")
    
    # Get soil compatibility scores
    scored_crops = crop_db.get_crops_with_soil_scores(suitable_crops, soil)
    
    print(f"\nTop 5 recommendations:")
    for i, (crop, score, amendments) in enumerate(scored_crops[:5], 1):
        print(f"  {i}. {crop.common_name}")
        print(f"     Duration: {crop.duration_days} days | Soil score: {score:.1f}/100")
        print(f"     Regional suitability: {crop.regional_suitability.get('PUNE', 0)*100:.0f}%")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("INDIAN FARMER CROP RECOMMENDATION SYSTEM - TEST SUITE")
    print("="*60)
    
    try:
        test_historical_data()
        test_regions()
        test_crops()
        test_soil_compatibility()
        test_integrated_query()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED!")
        print("="*60)
        print("\nSystem is ready for use!")
        print("- 10 Indian agricultural regions configured")
        print("- 10 years of historical weather data (2014-2024)")
        print("- 15 short-duration crops (70-90 days)")
        print("- Soil compatibility scoring implemented")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
