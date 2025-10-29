"""
Check scraping progress and find the last BDNS number saved.
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")  # Relative path to data directory

def check_progress():
    """Check all Parquet files and find the highest BDNS number."""
    parquet_files = list(DATA_DIR.glob("bdns_*.parquet"))
    
    if not parquet_files:
        print("No data files found!")
        return
    
    all_bdns = []
    total_rows = 0
    
    print("=" * 80)
    print("SCRAPING PROGRESS REPORT")
    print("=" * 80)
    
    for file in sorted(parquet_files):
        df = pd.read_parquet(file)
        year = file.stem.split('_')[1]
        unique_bdns = df['codigoBDNS'].unique()
        
        print(f"\n{file.name}:")
        print(f"  Total rows: {len(df):,}")
        print(f"  Unique BDNS codes: {len(unique_bdns):,}")
        print(f"  BDNS range: {unique_bdns.min()} - {unique_bdns.max()}")
        
        all_bdns.extend(unique_bdns)
        total_rows += len(df)
    
    # Convert to integers for proper sorting
    all_bdns_int = [int(b) for b in all_bdns]
    all_bdns_int.sort()
    
    print("\n" + "=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)
    print(f"Total rows across all files: {total_rows:,}")
    print(f"Total unique BDNS codes: {len(set(all_bdns)):,}")
    print(f"Lowest BDNS number: {min(all_bdns_int):,}")
    print(f"Highest BDNS number: {max(all_bdns_int):,}")
    print(f"\n✓ Resume scraping from: {max(all_bdns_int) + 1:,}")
    
    # Check for gaps
    print("\n" + "-" * 80)
    print("Checking for gaps in BDNS sequence...")
    print("-" * 80)
    
    bdns_set = set(all_bdns_int)
    min_bdns = min(all_bdns_int)
    max_bdns = max(all_bdns_int)
    
    gaps = []
    gap_ranges = []
    in_gap = False
    gap_start = None
    
    for i in range(min_bdns, max_bdns + 1):
        if i not in bdns_set:
            if not in_gap:
                gap_start = i
                in_gap = True
        else:
            if in_gap:
                gap_end = i - 1
                gap_ranges.append((gap_start, gap_end))
                in_gap = False
    
    # Handle case where gap extends to the end
    if in_gap:
        gap_ranges.append((gap_start, max_bdns))
    
    if gap_ranges:
        print(f"\nFound {len(gap_ranges)} gap(s) in the data:")
        for start, end in gap_ranges[:10]:  # Show first 10 gaps
            gap_size = end - start + 1
            print(f"  BDNS {start:,} to {end:,} ({gap_size:,} missing numbers)")
        
        if len(gap_ranges) > 10:
            print(f"  ... and {len(gap_ranges) - 10} more gaps")
        
        total_missing = sum(end - start + 1 for start, end in gap_ranges)
        print(f"\nTotal missing BDNS numbers: {total_missing:,}")
    else:
        print("\n✓ No gaps found - all BDNS numbers are consecutive!")
    
    print("\n" + "=" * 80)
    
    return max(all_bdns_int)

if __name__ == "__main__":
    check_progress()

