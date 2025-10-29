"""
Test script for BDNS scraper
Tests the scraper on a small range to verify everything works correctly.
"""

import requests
import pandas as pd
from pathlib import Path

# Configuration for testing
TEST_BDNS = 865179  # Known working BDNS number from your example
API_URL = "https://www.pap.hacienda.gob.es/bdnstrans/api/convocatorias"
DATA_DIR = Path("data")  # Relative path to data directory

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Referer': 'https://www.pap.hacienda.gob.es/bdnstrans/GE/es/convocatorias/',
}


def test_api_connection():
    """Test if we can connect to the API."""
    print("=" * 60)
    print("TEST 1: API Connection")
    print("=" * 60)
    
    url = f"{API_URL}?numConv={TEST_BDNS}&vpd=GE"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            print("✓ Successfully connected to API")
            print(f"✓ BDNS {TEST_BDNS} found")
            data = response.json()
            print(f"✓ Received data with {len(data)} fields")
            return True
        else:
            print(f"✗ API returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error connecting to API: {str(e)}")
        return False


def test_data_parsing():
    """Test if we can parse the API response correctly."""
    print("\n" + "=" * 60)
    print("TEST 2: Data Parsing")
    print("=" * 60)
    
    url = f"{API_URL}?numConv={TEST_BDNS}&vpd=GE"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        data = response.json()
        
        # Check key fields
        required_fields = [
            'codigoBDNS', 'fechaRecepcion', 'descripcion', 
            'presupuestoTotal', 'organo'
        ]
        
        missing = [f for f in required_fields if f not in data]
        
        if missing:
            print(f"✗ Missing required fields: {missing}")
            return False
        else:
            print("✓ All required fields present")
            
        # Test nested arrays
        print(f"✓ instrumentos: {len(data.get('instrumentos', []))} items")
        print(f"✓ tiposBeneficiarios: {len(data.get('tiposBeneficiarios', []))} items")
        print(f"✓ sectores: {len(data.get('sectores', []))} items")
        print(f"✓ regiones: {len(data.get('regiones', []))} items")
        
        return True
        
    except Exception as e:
        print(f"✗ Error parsing data: {str(e)}")
        return False


def test_parquet_saving():
    """Test if we can save data to Parquet format."""
    print("\n" + "=" * 60)
    print("TEST 3: Parquet File Saving")
    print("=" * 60)
    
    try:
        # Create test DataFrame
        test_data = {
            'codigoBDNS': ['865179'],
            'descripcion': ['Test convocatoria'],
            'presupuestoTotal': [230000],
            'year': [2025]
        }
        df = pd.DataFrame(test_data)
        
        # Ensure data directory exists
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✓ Data directory exists: {DATA_DIR}")
        
        # Try to save
        test_file = DATA_DIR / "test.parquet"
        df.to_parquet(test_file, engine='pyarrow', index=False)
        print(f"✓ Successfully saved test Parquet file")
        
        # Try to read back
        df_read = pd.read_parquet(test_file)
        print(f"✓ Successfully read test Parquet file")
        print(f"✓ Read {len(df_read)} rows with {len(df_read.columns)} columns")
        
        # Clean up
        test_file.unlink()
        print(f"✓ Cleaned up test file")
        
        return True
        
    except Exception as e:
        print(f"✗ Error with Parquet operations: {str(e)}")
        return False


def test_full_workflow():
    """Test the complete scraping workflow on one BDNS entry."""
    print("\n" + "=" * 60)
    print("TEST 4: Full Workflow (One Entry)")
    print("=" * 60)
    
    try:
        from scraper import BDNSScraper
        
        # Create scraper instance
        scraper = BDNSScraper(start_bdns=TEST_BDNS)
        print("✓ Scraper instance created")
        
        # Fetch one entry
        data = scraper.fetch_convocatoria(TEST_BDNS)
        if not data:
            print("✗ Failed to fetch convocatoria")
            return False
        print(f"✓ Fetched BDNS {TEST_BDNS}")
        
        # Transform data
        rows = scraper.transform_data(data)
        print(f"✓ Transformed into {len(rows)} rows (Cartesian product)")
        
        # Add to dataframes
        scraper.add_rows(rows)
        print(f"✓ Added rows to in-memory DataFrames")
        
        # Save to parquet
        for year in scraper.dataframes_by_year.keys():
            scraper.save_to_parquet(year)
        print(f"✓ Saved to Parquet file(s)")
        
        # Verify file exists
        year = rows[0]['year']
        saved_file = DATA_DIR / f"bdns_{year}.parquet"
        if saved_file.exists():
            df = pd.read_parquet(saved_file)
            print(f"✓ Verified: {len(df)} rows in bdns_{year}.parquet")
            
            # Clean up test file
            saved_file.unlink()
            print(f"✓ Cleaned up test file")
            return True
        else:
            print("✗ Parquet file was not created")
            return False
            
    except Exception as e:
        print(f"✗ Error in full workflow: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "BDNS SCRAPER TEST SUITE" + " " * 20 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    tests = [
        test_api_connection,
        test_data_parsing,
        test_parquet_saving,
        test_full_workflow,
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed! Ready to run full scraper.")
        print("\nNext steps:")
        print("  1. Run: python scraper.py")
        print("  2. Open: analysis.ipynb in Jupyter")
    else:
        print("\n✗ Some tests failed. Please check the output above.")
    
    print("=" * 60)


if __name__ == "__main__":
    main()

