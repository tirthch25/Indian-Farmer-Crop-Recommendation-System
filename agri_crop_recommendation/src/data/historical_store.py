"""
Historical Weather Data Store

Provides efficient access to historical weather data for Indian agricultural regions.
Uses Parquet files partitioned by region and year for efficient querying.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class HistoricalDataStore:
    """
    Manages historical weather data storage and retrieval.
    
    Data is stored in Parquet format, partitioned by region and year:
    data/historical/{region_id}/{year}.parquet
    """
    
    def __init__(self, data_dir: str = "data/historical"):
        """
        Initialize the historical data store.
        
        Args:
            data_dir: Base directory for historical data storage
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized HistoricalDataStore with data_dir={self.data_dir}")
    
    def get_historical_data(
        self,
        region_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> pd.DataFrame:
        """
        Retrieve historical weather data for a specific region and date range.
        
        Args:
            region_id: Region identifier (e.g., "PUNE", "SOLAPUR")
            start_date: Start date for data retrieval
            end_date: End date for data retrieval
            
        Returns:
            DataFrame with columns: date, temp_max, temp_min, rainfall, humidity, wind_speed
            
        Raises:
            FileNotFoundError: If no data exists for the region
        """
        region_dir = self.data_dir / region_id
        
        if not region_dir.exists():
            logger.error(f"No historical data found for region {region_id}")
            raise FileNotFoundError(f"No historical data available for region {region_id}")
        
        # Determine which years to load
        start_year = start_date.year
        end_year = end_date.year
        
        dfs = []
        for year in range(start_year, end_year + 1):
            year_file = region_dir / f"{year}.parquet"
            if year_file.exists():
                df = pd.read_parquet(year_file)
                dfs.append(df)
            else:
                logger.warning(f"Missing data file: {year_file}")
        
        if not dfs:
            raise FileNotFoundError(
                f"No historical data files found for region {region_id} "
                f"between {start_year} and {end_year}"
            )
        
        # Combine all years
        combined_df = pd.concat(dfs, ignore_index=True)
        
        # Filter by date range
        combined_df['date'] = pd.to_datetime(combined_df['date'])
        mask = (combined_df['date'] >= start_date) & (combined_df['date'] <= end_date)
        filtered_df = combined_df[mask].copy()
        
        logger.info(
            f"Retrieved {len(filtered_df)} records for {region_id} "
            f"from {start_date.date()} to {end_date.date()}"
        )
        
        return filtered_df.sort_values('date').reset_index(drop=True)
    
    def get_climatology(
        self,
        region_id: str,
        month: int,
        statistic: str = "mean"
    ) -> Dict[str, float]:
        """
        Compute climatological statistics for a specific month.
        
        Args:
            region_id: Region identifier
            month: Month number (1-12)
            statistic: Type of statistic ("mean", "p25", "p75", "max", "min")
            
        Returns:
            Dictionary with climatological values for temp_max, temp_min, rainfall, etc.
        """
        region_dir = self.data_dir / region_id
        
        if not region_dir.exists():
            logger.error(f"No historical data found for region {region_id}")
            raise FileNotFoundError(f"No historical data available for region {region_id}")
        
        # Load all available years
        dfs = []
        for year_file in region_dir.glob("*.parquet"):
            df = pd.read_parquet(year_file)
            dfs.append(df)
        
        if not dfs:
            raise FileNotFoundError(f"No historical data files found for region {region_id}")
        
        combined_df = pd.concat(dfs, ignore_index=True)
        combined_df['date'] = pd.to_datetime(combined_df['date'])
        combined_df['month'] = combined_df['date'].dt.month
        
        # Filter by month
        month_data = combined_df[combined_df['month'] == month]
        
        if len(month_data) == 0:
            logger.warning(f"No data found for month {month} in region {region_id}")
            return {}
        
        # Calculate statistics
        numeric_cols = ['temp_max', 'temp_min', 'rainfall', 'humidity', 'wind_speed']
        result = {}
        
        for col in numeric_cols:
            if col in month_data.columns:
                if statistic == "mean":
                    result[col] = float(month_data[col].mean())
                elif statistic == "p25":
                    result[col] = float(month_data[col].quantile(0.25))
                elif statistic == "p75":
                    result[col] = float(month_data[col].quantile(0.75))
                elif statistic == "max":
                    result[col] = float(month_data[col].max())
                elif statistic == "min":
                    result[col] = float(month_data[col].min())
        
        logger.info(f"Computed {statistic} climatology for {region_id}, month {month}")
        return result
    
    def save_historical_data(
        self,
        region_id: str,
        data: pd.DataFrame,
        year: int
    ) -> None:
        """
        Save historical weather data for a region and year.
        
        Args:
            region_id: Region identifier
            data: DataFrame with weather data
            year: Year of the data
        """
        region_dir = self.data_dir / region_id
        region_dir.mkdir(parents=True, exist_ok=True)
        
        year_file = region_dir / f"{year}.parquet"
        data.to_parquet(year_file, index=False)
        
        logger.info(f"Saved {len(data)} records for {region_id} year {year} to {year_file}")
    
    def get_available_regions(self) -> list:
        """
        Get list of regions with available historical data.
        
        Returns:
            List of region IDs
        """
        regions = [d.name for d in self.data_dir.iterdir() if d.is_dir()]
        logger.info(f"Found {len(regions)} regions with historical data")
        return sorted(regions)
    
    def get_data_coverage(self, region_id: str) -> Dict[str, any]:
        """
        Get information about data coverage for a region.
        
        Args:
            region_id: Region identifier
            
        Returns:
            Dictionary with coverage information (years, record count, etc.)
        """
        region_dir = self.data_dir / region_id
        
        if not region_dir.exists():
            return {"region_id": region_id, "available": False}
        
        years = sorted([int(f.stem) for f in region_dir.glob("*.parquet")])
        
        if not years:
            return {"region_id": region_id, "available": False}
        
        # Count total records
        total_records = 0
        for year_file in region_dir.glob("*.parquet"):
            df = pd.read_parquet(year_file)
            total_records += len(df)
        
        return {
            "region_id": region_id,
            "available": True,
            "years": years,
            "year_range": f"{min(years)}-{max(years)}",
            "total_years": len(years),
            "total_records": total_records
        }
