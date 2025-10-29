# BDNS API Scanner

A Python tool to scrape and analyze convocatorias (grants/calls) from the Spanish government's BDNS (Base de Datos Nacional de Subvenciones) database.

## Features

- **Automated Scraping**: Fetches convocatorias data from BDNS API starting from a specified number
- **Incremental Storage**: Saves data incrementally to Parquet files organized by year
- **Error Handling**: Robust error handling with automatic retry logic and 404 detection
- **Streamlit Web App**: Interactive web application for filtering and analyzing data (deployable for free)
- **Jupyter Notebook**: Alternative analysis interface with comprehensive filtering capabilities
- **Privacy Headers**: Uses appropriate HTTP headers to avoid detection

## Project Structure

```
Mapscanner/
├── scraper.py                  # Main scraping script
├── streamlit_app.py            # Streamlit web application
├── analysis.ipynb              # Jupyter notebook for data analysis
├── data/                       # Directory for Parquet files (created automatically)
│   └── bdns_YYYY.parquet       # One file per year
├── .streamlit/                 # Streamlit configuration
│   └── config.toml             # App configuration
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── STREAMLIT_DEPLOYMENT.md     # Deployment guide for Streamlit Cloud
```

## Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify installation**:
   ```bash
   python -c "import pandas, requests, pyarrow; print('All dependencies installed successfully!')"
   ```

## Usage

### Running the Scraper

The scraper will fetch convocatorias starting from BDNS number 600000 and continue until it encounters 10 consecutive 404 errors.

```bash
python scraper.py
```

**Configuration** (edit `scraper.py` to change these):
- `START_BDNS = 600000`: Starting BDNS number
- `MAX_CONSECUTIVE_404 = 10`: Stop after this many consecutive 404s
- `USE_DELAY = False`: Enable random delays between requests
- `MAX_DELAY = 4`: Maximum delay in seconds (if enabled)

**During scraping**:
- Data is saved incrementally to the `data/` directory
- Each year's data is stored in a separate Parquet file (`bdns_YYYY.parquet`)
- Press `Ctrl+C` to stop scraping at any time (data will be saved)

### Using the Streamlit Web App (Recommended)

**Run locally**:
```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

**Deploy to Streamlit Community Cloud (FREE)**:
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Deploy your app with one click

See `STREAMLIT_DEPLOYMENT.md` for detailed deployment instructions.

**Features of the Streamlit App**:
- 🔍 Interactive filters with real-time results
- 📊 Summary statistics and metrics
- 📈 Year-by-year analysis
- 📥 Download filtered results as CSV
- 🔄 Sortable and searchable data tables
- 📱 Mobile-friendly interface
- 🌐 Accessible from anywhere (when deployed)

### Analyzing Data with Jupyter Notebook

1. **Start Jupyter Notebook**:
   ```bash
   jupyter notebook
   ```

2. **Open `analysis.ipynb`** in your browser

3. **Load and analyze data** using the provided functions

## Analysis Features

The `analysis.ipynb` notebook provides:

### Data Loading
- Load all years of data
- Load specific year(s)
- Get list of available years

### Filtering Capabilities
- **BDNS Number**: Search by specific BDNS code(s)
- **Description**: Search keywords in convocatoria descriptions
- **Date Ranges**: Filter by reception, start, or end dates
- **Institution**: Filter by government institution (nivel1, nivel2)
- **Budget**: Filter by budget range (presupuestoTotal)
- **Region**: Filter by Spanish region
- **Sector**: Filter by sector description or code
- **Type**: Filter by convocatoria type
- **Status**: Filter by open/closed status
- **Combined Filters**: Chain multiple filters together

### Analysis Functions
- **Summary Statistics**: Overview of the dataset with key metrics
- **Display Results**: Show filtered results in readable format
- **Export**: Export filtered results to CSV

## Data Schema

Each row in the dataset contains:

- `id`, `codigoBDNS`, `fechaRecepcion`, `sedeElectronica`
- `organo_nivel1`, `organo_nivel2`, `organo_nivel3`
- `instrumento_descripcion`
- `tipoConvocatoria`, `presupuestoTotal`, `mrr`
- `descripcion`, `descripcionLeng`
- `tipoBeneficiario_descripcion`
- `sector_descripcion`, `sector_codigo`
- `region_descripcion`
- `descripcionFinalidad`, `descripcionBasesReguladoras`, `urlBasesReguladoras`
- `sePublicaDiarioOficial`, `abierto`
- `fechaInicioSolicitud`, `fechaFinSolicitud`, `textInicio`, `textFin`
- `year` (extracted from fechaRecepcion)

**Note**: Due to Cartesian product of nested arrays (instrumentos, tiposBeneficiarios, sectores, regiones), one BDNS entry may result in multiple rows.

## Example Queries

```python
# Load all data
df = load_all_data()

# Find open education convocatorias in Valencia with budget > €100,000
result = df.copy()
result = filter_by_status(result, abierto=True)
result = filter_by_sector(result, sector_desc="Educación")
result = filter_by_region(result, "VALENCIANA")
result = filter_by_budget(result, min_budget=100000)
display_results(result)

# Search for specific keywords
result = search_descripcion(df, "investigación")
display_results(result)

# Get summary statistics
get_summary(df)
```

## Technical Details

### Scraper Features
- **HTTP Headers**: Uses standard browser headers to avoid detection
- **Incremental Saving**: Data is saved after each successful request to prevent loss
- **Year-based Organization**: Automatically creates separate files per year
- **Robust Error Handling**: Continues on errors, only stops after 10 consecutive 404s
- **Progress Logging**: Real-time logging of scraping progress

### Data Format
- **Parquet**: Efficient columnar storage format
- **Compression**: Automatic compression for smaller file sizes
- **Fast Queries**: Optimized for filtering and analysis

### Rate Limiting
By default, the scraper makes requests without delays. If you encounter rate limiting:

1. Edit `scraper.py`
2. Set `USE_DELAY = True`
3. Adjust `MAX_DELAY` as needed (default: 4 seconds)

## Troubleshooting

### "No data files found"
- Run `scraper.py` first to collect data
- Check that the `data/` directory exists and contains `.parquet` files

### Rate Limiting / 429 Errors
- Enable delays in `scraper.py`: `USE_DELAY = True`
- Increase `MAX_DELAY` to add more time between requests

### Memory Issues
- Load specific years instead of all data: `load_data_by_year(2025)`
- Use filtering functions to reduce dataset size before analysis

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (3.8+ recommended)

## Ethical Considerations

This tool is designed for legitimate research and analysis purposes. Please:

- Respect the API's rate limits
- Use delays if making many requests
- Only collect publicly available data
- Follow Spain's data protection regulations (LOPD/GDPR)
- Attribute data source when publishing findings

## License

This project is for educational and research purposes.

## Data Source

Data is sourced from:
- **Website**: https://www.pap.hacienda.gob.es/bdnstrans/
- **API**: https://www.pap.hacienda.gob.es/bdnstrans/api/convocatorias
- **Source**: Base de Datos Nacional de Subvenciones (BDNS)
- **Authority**: Ministerio de Hacienda y Función Pública, España

## Disclaimer

The data collected through this tool is subject to the terms and conditions set by the Spanish government. Users are responsible for ensuring their use complies with all applicable laws and regulations.

