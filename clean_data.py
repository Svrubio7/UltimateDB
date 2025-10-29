"""
Utility to clean existing Parquet files and remove duplicates.
Run this after scraping to ensure data quality.
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")  # Relative path to data directory


def clean_all_files():
    """Clean all Parquet files in the data directory."""
    parquet_files = list(DATA_DIR.glob("bdns_*.parquet"))
    
    if not parquet_files:
        print("No data files found!")
        return
    
    print("=" * 80)
    print("DATA CLEANING UTILITY")
    print("=" * 80)
    
    total_removed = 0
    
    for file in sorted(parquet_files):
        print(f"\nProcessing {file.name}...")
        
        # Load data
        df = pd.read_parquet(file)
        initial_count = len(df)
        print(f"  Initial rows: {initial_count:,}")
        print(f"  Unique BDNS codes: {df['codigoBDNS'].nunique():,}")
        
        # Remove duplicates based on BDNS code only
        df_clean = df.drop_duplicates(subset=['codigoBDNS'], keep='last')
        
        removed = initial_count - len(df_clean)
        total_removed += removed
        
        if removed > 0:
            print(f"  ✓ Removed {removed:,} duplicate rows")
            print(f"  Final rows: {len(df_clean):,}")
            
            # Save cleaned data
            df_clean.to_parquet(file, engine='pyarrow', index=False)
            print(f"  ✓ Saved cleaned data to {file.name}")
        else:
            print(f"  ✓ No duplicates found")
    
    print("\n" + "=" * 80)
    print("CLEANING SUMMARY")
    print("=" * 80)
    print(f"Files processed: {len(parquet_files)}")
    print(f"Total duplicates removed: {total_removed:,}")
    
    if total_removed > 0:
        print("\n✓ Data cleaning complete!")
    else:
        print("\n✓ All files were already clean!")
    
    print("=" * 80)


if __name__ == "__main__":
    clean_all_files()

