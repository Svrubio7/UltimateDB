"""
BDNS API Scanner
Scrapes convocatorias from the Spanish government BDNS database.
"""

import requests
import pandas as pd
import json
import time
import random
from pathlib import Path
from datetime import datetime
from itertools import product
from typing import Dict, List, Optional, Any

# Configuration
START_BDNS = 747573
MAX_CONSECUTIVE_404 = 10
DATA_DIR = Path("data")  # Relative path to data directory
API_URL = "https://www.pap.hacienda.gob.es/bdnstrans/api/convocatorias"
USE_DELAY = False  # Set to True to enable random delays
MAX_DELAY = 4  # Maximum delay in seconds

# HTTP Headers to avoid detection
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Referer': 'https://www.pap.hacienda.gob.es/bdnstrans/GE/es/convocatorias/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
}


class BDNSScraper:
    """Main scraper class for BDNS convocatorias."""
    
    def __init__(self, start_bdns: int = START_BDNS):
        self.start_bdns = start_bdns
        self.current_bdns = start_bdns
        self.consecutive_404s = 0
        self.dataframes_by_year = {}
        self.total_records = 0
        self.total_requests = 0
        
        # Create data directory if it doesn't exist
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
    def fetch_convocatoria(self, bdns_num: int) -> Optional[Dict]:
        """Fetch a single convocatoria from the API."""
        url = f"{API_URL}?numConv={bdns_num}&vpd=GE"
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            self.total_requests += 1
            
            if response.status_code == 404:
                self.consecutive_404s += 1
                print(f"[404] BDNS {bdns_num} not found (consecutive: {self.consecutive_404s})")
                return None
            
            if response.status_code == 200:
                self.consecutive_404s = 0  # Reset counter on success
                data = response.json()
                print(f"[✓] BDNS {bdns_num} fetched successfully")
                return data
            
            print(f"[!] BDNS {bdns_num} returned status {response.status_code}")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Request failed for BDNS {bdns_num}: {str(e)}")
            return None
    
    def transform_data(self, data: Dict) -> List[Dict]:
        """
        Transform API response into flat rows.
        Creates Cartesian product of nested arrays.
        """
        # Extract base fields
        base_data = {
            'id': data.get('id'),
            'codigoBDNS': data.get('codigoBDNS'),
            'fechaRecepcion': data.get('fechaRecepcion'),
            'sedeElectronica': data.get('sedeElectronica'),
            'tipoConvocatoria': data.get('tipoConvocatoria'),
            'presupuestoTotal': data.get('presupuestoTotal'),
            'mrr': data.get('mrr'),
            'descripcion': data.get('descripcion'),
            'descripcionLeng': data.get('descripcionLeng'),
            'descripcionFinalidad': data.get('descripcionFinalidad'),
            'descripcionBasesReguladoras': data.get('descripcionBasesReguladoras'),
            'urlBasesReguladoras': data.get('urlBasesReguladoras'),
            'sePublicaDiarioOficial': data.get('sePublicaDiarioOficial'),
            'abierto': data.get('abierto'),
            'fechaInicioSolicitud': data.get('fechaInicioSolicitud'),
            'fechaFinSolicitud': data.get('fechaFinSolicitud'),
            'textInicio': data.get('textInicio'),
            'textFin': data.get('textFin'),
        }
        
        # Flatten organo
        organo = data.get('organo', {})
        base_data['organo_nivel1'] = organo.get('nivel1')
        base_data['organo_nivel2'] = organo.get('nivel2')
        base_data['organo_nivel3'] = organo.get('nivel3')
        
        # Extract year from fechaRecepcion
        if base_data['fechaRecepcion']:
            try:
                year = datetime.strptime(base_data['fechaRecepcion'], '%Y-%m-%d').year
                base_data['year'] = year
            except:
                base_data['year'] = None
        else:
            base_data['year'] = None
        
        # Get nested arrays (or default to single empty dict)
        instrumentos = data.get('instrumentos', [{}])
        tipos_beneficiarios = data.get('tiposBeneficiarios', [{}])
        sectores = data.get('sectores', [{}])
        regiones = data.get('regiones', [{}])
        
        # Handle empty arrays
        if not instrumentos:
            instrumentos = [{}]
        if not tipos_beneficiarios:
            tipos_beneficiarios = [{}]
        if not sectores:
            sectores = [{}]
        if not regiones:
            regiones = [{}]
        
        # Create Cartesian product
        rows = []
        for inst, benef, sector, region in product(instrumentos, tipos_beneficiarios, sectores, regiones):
            row = base_data.copy()
            row['instrumento_descripcion'] = inst.get('descripcion')
            row['tipoBeneficiario_descripcion'] = benef.get('descripcion')
            row['sector_descripcion'] = sector.get('descripcion')
            row['sector_codigo'] = sector.get('codigo')
            row['region_descripcion'] = region.get('descripcion')
            rows.append(row)
        
        return rows
    
    def save_to_parquet(self, year: int):
        """Save DataFrame for a specific year to Parquet file."""
        if year not in self.dataframes_by_year or self.dataframes_by_year[year].empty:
            return
        
        file_path = DATA_DIR / f"bdns_{year}.parquet"
        
        try:
            # If file exists, load it and append
            if file_path.exists():
                existing_df = pd.read_parquet(file_path)
                combined_df = pd.concat([existing_df, self.dataframes_by_year[year]], ignore_index=True)
                
                # Remove duplicates based on BDNS code only
                combined_df = combined_df.drop_duplicates(subset=['codigoBDNS'], keep='last')
                combined_df.to_parquet(file_path, engine='pyarrow', index=False)
            else:
                self.dataframes_by_year[year].to_parquet(file_path, engine='pyarrow', index=False)
            
            print(f"[SAVED] {len(self.dataframes_by_year[year])} rows saved to {file_path.name}")
            
            # Clear the in-memory DataFrame for this year
            self.dataframes_by_year[year] = pd.DataFrame()
            
        except Exception as e:
            print(f"[ERROR] Failed to save {file_path.name}: {str(e)}")
    
    def add_rows(self, rows: List[Dict]):
        """Add rows to the appropriate year's DataFrame."""
        if not rows:
            return
        
        # Group rows by year
        rows_by_year = {}
        for row in rows:
            year = row.get('year')
            if year:
                if year not in rows_by_year:
                    rows_by_year[year] = []
                rows_by_year[year].append(row)
        
        # Add to DataFrames
        for year, year_rows in rows_by_year.items():
            if year not in self.dataframes_by_year:
                self.dataframes_by_year[year] = pd.DataFrame()
            
            new_df = pd.DataFrame(year_rows)
            self.dataframes_by_year[year] = pd.concat(
                [self.dataframes_by_year[year], new_df], 
                ignore_index=True
            )
            
            self.total_records += len(year_rows)
    
    def run(self):
        """Main scraping loop."""
        print(f"Starting BDNS scraper from {self.start_bdns}")
        print(f"Data will be saved to: {DATA_DIR}")
        print(f"Delay enabled: {USE_DELAY}")
        print("-" * 60)
        
        try:
            while self.consecutive_404s < MAX_CONSECUTIVE_404:
                # Fetch data
                data = self.fetch_convocatoria(self.current_bdns)
                
                if data:
                    # Transform data
                    rows = self.transform_data(data)
                    
                    # Add to DataFrames
                    self.add_rows(rows)
                    
                    # Save every 100 successful requests
                    if self.total_records > 0 and self.total_records % 100 == 0:
                        for year in self.dataframes_by_year.keys():
                            if not self.dataframes_by_year[year].empty:
                                self.save_to_parquet(year)
                
                # Move to next BDNS number
                self.current_bdns += 1
                
                # Optional delay
                if USE_DELAY and data:
                    delay = random.uniform(0, MAX_DELAY)
                    time.sleep(delay)
        
        except KeyboardInterrupt:
            print("\n[!] Scraping interrupted by user")
        
        finally:
            # Save all remaining data
            print("\n" + "-" * 60)
            print("Saving remaining data...")
            for year in self.dataframes_by_year.keys():
                if not self.dataframes_by_year[year].empty:
                    self.save_to_parquet(year)
            
            print("\n" + "=" * 60)
            print("SCRAPING SUMMARY")
            print("=" * 60)
            print(f"Total requests: {self.total_requests}")
            print(f"Total records saved: {self.total_records}")
            print(f"Last BDNS processed: {self.current_bdns - 1}")
            print(f"Consecutive 404s: {self.consecutive_404s}")
            print(f"Data directory: {DATA_DIR}")
            print("=" * 60)


if __name__ == "__main__":
    scraper = BDNSScraper(start_bdns=START_BDNS)
    scraper.run()

