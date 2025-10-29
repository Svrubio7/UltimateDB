"""
Resume scraping from the last saved BDNS number.
Automatically detects where to resume from.
"""

import pandas as pd
from pathlib import Path
from scraper import BDNSScraper, DATA_DIR

def find_last_bdns():
    """Find the highest BDNS number in saved data."""
    parquet_files = list(DATA_DIR.glob("bdns_*.parquet"))
    
    if not parquet_files:
        print("No existing data found. Starting from 600000")
        return 600000
    
    all_bdns = []
    for file in parquet_files:
        df = pd.read_parquet(file)
        all_bdns.extend(df['codigoBDNS'].astype(int).tolist())
    
    max_bdns = max(all_bdns)
    print(f"Last BDNS number found in data: {max_bdns:,}")
    print(f"Resuming from: {max_bdns + 1:,}")
    return max_bdns + 1

if __name__ == "__main__":
    resume_from = find_last_bdns()
    
    print("\n" + "=" * 60)
    print(f"Starting scraper from BDNS {resume_from:,}")
    print("Target: 865569 (latest known BDNS)")
    print("Press Ctrl+C to stop at any time")
    print("=" * 60 + "\n")
    
    # Create scraper starting from the resume point
    scraper = BDNSScraper(start_bdns=resume_from)
    scraper.run()

