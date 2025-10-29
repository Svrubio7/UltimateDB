"""
Test script to verify Streamlit app functionality
Run this before deploying to ensure everything works correctly
"""

import pandas as pd
from pathlib import Path
import sys

def test_dependencies():
    """Test if all required dependencies are installed."""
    print("Testing dependencies...")
    
    try:
        import streamlit
        print(f"✅ Streamlit version: {streamlit.__version__}")
    except ImportError:
        print("❌ Streamlit not installed. Run: pip install streamlit")
        return False
    
    try:
        import pandas
        print(f"✅ Pandas version: {pandas.__version__}")
    except ImportError:
        print("❌ Pandas not installed. Run: pip install pandas")
        return False
    
    try:
        import pyarrow
        print(f"✅ PyArrow version: {pyarrow.__version__}")
    except ImportError:
        print("❌ PyArrow not installed. Run: pip install pyarrow")
        return False
    
    return True


def test_data_files():
    """Test if data files exist."""
    print("\nTesting data files...")
    
    data_dir = Path("data")
    
    if not data_dir.exists():
        print(f"❌ Data directory '{data_dir}' does not exist")
        print("   Create it or run scraper.py first")
        return False
    
    parquet_files = list(data_dir.glob("bdns_*.parquet"))
    
    if not parquet_files:
        print(f"❌ No Parquet files found in '{data_dir}'")
        print("   Run scraper.py to generate data files")
        return False
    
    print(f"✅ Found {len(parquet_files)} Parquet file(s):")
    total_size = 0
    for file in parquet_files:
        size_mb = file.stat().st_size / (1024 * 1024)
        total_size += size_mb
        print(f"   - {file.name}: {size_mb:.2f} MB")
    
    print(f"   Total size: {total_size:.2f} MB")
    
    if total_size > 100:
        print("   ⚠️  Warning: Files are large (>100MB). Consider using Git LFS for deployment")
    
    return True


def test_data_loading():
    """Test if data can be loaded correctly."""
    print("\nTesting data loading...")
    
    try:
        data_dir = Path("data")
        parquet_files = list(data_dir.glob("bdns_*.parquet"))
        
        if not parquet_files:
            print("❌ No data files to load")
            return False
        
        # Try loading the first file
        df = pd.read_parquet(parquet_files[0])
        print(f"✅ Successfully loaded {parquet_files[0].name}")
        print(f"   Rows: {len(df):,}")
        print(f"   Columns: {len(df.columns)}")
        
        # Check required columns
        required_columns = [
            'codigoBDNS', 'fechaRecepcion', 'descripcion', 'presupuestoTotal',
            'organo_nivel1', 'region_descripcion', 'year', 'abierto'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ Missing required columns: {missing_columns}")
            return False
        
        print("✅ All required columns present")
        
        # Test for duplicates
        dupes = df['codigoBDNS'].duplicated().sum()
        if dupes > 0:
            print(f"   ⚠️  Found {dupes} duplicate BDNS codes (will be cleaned automatically)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading data: {str(e)}")
        return False


def test_streamlit_imports():
    """Test if streamlit_app.py can be imported."""
    print("\nTesting streamlit_app.py...")
    
    if not Path("streamlit_app.py").exists():
        print("❌ streamlit_app.py not found")
        return False
    
    try:
        # Just check if the file can be read
        with open("streamlit_app.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for required functions
        required_functions = ["load_all_data", "apply_filters", "main"]
        missing = [func for func in required_functions if f"def {func}" not in content]
        
        if missing:
            print(f"❌ Missing functions in streamlit_app.py: {missing}")
            return False
        
        print("✅ streamlit_app.py structure looks good")
        return True
        
    except Exception as e:
        print(f"❌ Error reading streamlit_app.py: {str(e)}")
        return False


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("STREAMLIT APP VERIFICATION")
    print("=" * 60)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Data Files", test_data_files),
        ("Data Loading", test_data_loading),
        ("Streamlit App", test_streamlit_imports),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            results.append((test_name, test_func()))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with error: {str(e)}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All tests passed! Your app is ready to deploy.")
        print("\nNext steps:")
        print("1. Run locally: streamlit run streamlit_app.py")
        print("2. Test the UI and filters")
        print("3. Deploy to Streamlit Cloud (see STREAMLIT_DEPLOYMENT.md)")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues before deploying.")
    
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

