"""
BDNS Convocatorias - Aplicación de Análisis de Datos
Streamlit app para filtrar y analizar convocatorias BDNS
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from typing import List, Optional
import numpy as np

# Page configuration
st.set_page_config(
    page_title="BDNS Convocatorias",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Data directory
DATA_DIR = Path("data")

# Custom CSS for better styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 2rem;
    }
    h1 {
        color: #1f77b4;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_all_data() -> pd.DataFrame:
    """Load all BDNS data from Parquet files."""
    parquet_files = list(DATA_DIR.glob("bdns_*.parquet"))
    
    if not parquet_files:
        st.error(f"No se encontraron archivos de datos en {DATA_DIR}")
        return pd.DataFrame()
    
    dfs = []
    for file in parquet_files:
        df = pd.read_parquet(file)
        dfs.append(df)
    
    if not dfs:
        return pd.DataFrame()
    
    combined = pd.concat(dfs, ignore_index=True)
    
    # Remove duplicates based on BDNS code only
    combined = combined.drop_duplicates(subset=['codigoBDNS'], keep='last')
    
    # Convert date columns
    date_columns = ['fechaRecepcion', 'fechaInicioSolicitud', 'fechaFinSolicitud']
    for col in date_columns:
        if col in combined.columns:
            combined[col] = pd.to_datetime(combined[col], errors='coerce')
    
    return combined.reset_index(drop=True)


def get_unique_values(df: pd.DataFrame, column: str) -> List:
    """Get sorted unique values from a column."""
    if column not in df.columns:
        return []
    values = df[column].dropna().unique()
    return sorted(values)


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Apply all selected filters to the DataFrame."""
    filtered_df = df.copy()
    
    # BDNS Code filter
    if filters.get('bdns_codes'):
        bdns_list = [x.strip() for x in filters['bdns_codes'].split(',')]
        filtered_df = filtered_df[filtered_df['codigoBDNS'].astype(str).isin(bdns_list)]
    
    # Description search
    if filters.get('descripcion_search'):
        search_term = filters['descripcion_search'].lower()
        filtered_df = filtered_df[
            filtered_df['descripcion'].str.lower().str.contains(search_term, na=False)
        ]
    
    # Date range - Fecha Recepción
    if filters.get('fecha_recepcion_start'):
        filtered_df = filtered_df[filtered_df['fechaRecepcion'] >= pd.to_datetime(filters['fecha_recepcion_start'])]
    if filters.get('fecha_recepcion_end'):
        filtered_df = filtered_df[filtered_df['fechaRecepcion'] <= pd.to_datetime(filters['fecha_recepcion_end'])]
    
    # Date range - Fecha Solicitud
    if filters.get('fecha_solicitud_start'):
        filtered_df = filtered_df[filtered_df['fechaInicioSolicitud'] >= pd.to_datetime(filters['fecha_solicitud_start'])]
    if filters.get('fecha_solicitud_end'):
        filtered_df = filtered_df[filtered_df['fechaFinSolicitud'] <= pd.to_datetime(filters['fecha_solicitud_end'])]
    
    # Institution filters
    if filters.get('organo_nivel1'):
        filtered_df = filtered_df[filtered_df['organo_nivel1'].isin(filters['organo_nivel1'])]
    if filters.get('organo_nivel2'):
        filtered_df = filtered_df[filtered_df['organo_nivel2'].isin(filters['organo_nivel2'])]
    
    # Budget range
    if filters.get('presupuesto_min') is not None:
        filtered_df = filtered_df[filtered_df['presupuestoTotal'] >= filters['presupuesto_min']]
    if filters.get('presupuesto_max') is not None:
        filtered_df = filtered_df[filtered_df['presupuestoTotal'] <= filters['presupuesto_max']]
    
    # Region filter
    if filters.get('regiones'):
        filtered_df = filtered_df[filtered_df['region_descripcion'].isin(filters['regiones'])]
    
    # Sector filter
    if filters.get('sectores'):
        filtered_df = filtered_df[filtered_df['sector_descripcion'].isin(filters['sectores'])]
    
    # Beneficiario filter
    if filters.get('beneficiarios'):
        filtered_df = filtered_df[filtered_df['tipoBeneficiario_descripcion'].isin(filters['beneficiarios'])]
    
    # Tipo Convocatoria filter
    if filters.get('tipo_convocatoria'):
        filtered_df = filtered_df[filtered_df['tipoConvocatoria'].isin(filters['tipo_convocatoria'])]
    
    # Status filter
    if filters.get('abierto') is not None:
        filtered_df = filtered_df[filtered_df['abierto'] == filters['abierto']]
    
    # Year filter
    if filters.get('years'):
        filtered_df = filtered_df[filtered_df['year'].isin(filters['years'])]
    
    return filtered_df


def display_summary_stats(df: pd.DataFrame):
    """Display summary statistics."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Registros", f"{len(df):,}")
    with col2:
        st.metric("BDNS Únicos", f"{df['codigoBDNS'].nunique():,}")
    with col3:
        total_budget = df['presupuestoTotal'].sum()
        st.metric("Presupuesto Total", f"€{total_budget:,.0f}")
    with col4:
        avg_budget = df['presupuestoTotal'].mean()
        st.metric("Presupuesto Medio", f"€{avg_budget:,.0f}")


def main():
    # Header
    st.title("📊 BDNS Convocatorias - Análisis de Datos")
    st.markdown("Herramienta de búsqueda y filtrado de convocatorias BDNS")
    
    # Load data
    with st.spinner("Cargando datos..."):
        df = load_all_data()
    
    if df.empty:
        st.error("No hay datos disponibles. Asegúrate de que existan archivos Parquet en la carpeta 'data/'")
        st.stop()
    
    st.success(f"✅ Datos cargados: {len(df):,} registros")
    
    # Create tabs
    tab1, tab2 = st.tabs(["🔍 Filtros y Búsqueda", "📈 Estadísticas por Año"])
    
    with tab1:
        # Sidebar filters
        st.sidebar.header("Filtros")
        
        filters = {}
        
        # Year filter
        years_available = sorted(df['year'].dropna().unique())
        filters['years'] = st.sidebar.multiselect(
            "Año",
            options=years_available,
            help="Selecciona uno o más años"
        )
        
        # BDNS Code filter
        filters['bdns_codes'] = st.sidebar.text_input(
            "Código BDNS",
            placeholder="Ej: 865179, 865180",
            help="Ingresa uno o más códigos BDNS separados por comas"
        )
        
        # Description search
        filters['descripcion_search'] = st.sidebar.text_input(
            "Buscar en Descripción",
            placeholder="Ej: educación, subvención",
            help="Busca términos en el campo descripción"
        )
        
        # Date range - Fecha Recepción
        st.sidebar.subheader("Fecha de Recepción")
        col1, col2 = st.sidebar.columns(2)
        with col1:
            filters['fecha_recepcion_start'] = st.date_input(
                "Desde",
                value=None,
                key="fecha_rec_start"
            )
        with col2:
            filters['fecha_recepcion_end'] = st.date_input(
                "Hasta",
                value=None,
                key="fecha_rec_end"
            )
        
        # Date range - Fecha Solicitud
        st.sidebar.subheader("Fecha de Solicitud")
        col1, col2 = st.sidebar.columns(2)
        with col1:
            filters['fecha_solicitud_start'] = st.date_input(
                "Desde",
                value=None,
                key="fecha_sol_start"
            )
        with col2:
            filters['fecha_solicitud_end'] = st.date_input(
                "Hasta",
                value=None,
                key="fecha_sol_end"
            )
        
        # Institution filters
        st.sidebar.subheader("Institución")
        organo_nivel1_options = get_unique_values(df, 'organo_nivel1')
        filters['organo_nivel1'] = st.sidebar.multiselect(
            "Órgano Nivel 1",
            options=organo_nivel1_options
        )
        
        # Filter nivel2 based on nivel1 selection
        if filters['organo_nivel1']:
            df_filtered_nivel1 = df[df['organo_nivel1'].isin(filters['organo_nivel1'])]
            organo_nivel2_options = get_unique_values(df_filtered_nivel1, 'organo_nivel2')
        else:
            organo_nivel2_options = get_unique_values(df, 'organo_nivel2')
        
        filters['organo_nivel2'] = st.sidebar.multiselect(
            "Órgano Nivel 2",
            options=organo_nivel2_options
        )
        
        # Budget range
        st.sidebar.subheader("Presupuesto (€)")
        col1, col2 = st.sidebar.columns(2)
        with col1:
            filters['presupuesto_min'] = st.number_input(
                "Mínimo",
                min_value=0.0,
                value=None,
                step=1000.0,
                format="%.0f"
            )
        with col2:
            filters['presupuesto_max'] = st.number_input(
                "Máximo",
                min_value=0.0,
                value=None,
                step=1000.0,
                format="%.0f"
            )
        
        # Region filter
        region_options = get_unique_values(df, 'region_descripcion')
        filters['regiones'] = st.sidebar.multiselect(
            "Región",
            options=region_options
        )
        
        # Sector filter
        sector_options = get_unique_values(df, 'sector_descripcion')
        filters['sectores'] = st.sidebar.multiselect(
            "Sector",
            options=sector_options
        )
        
        # Beneficiario filter
        beneficiario_options = get_unique_values(df, 'tipoBeneficiario_descripcion')
        filters['beneficiarios'] = st.sidebar.multiselect(
            "Beneficiario",
            options=beneficiario_options
        )
        
        # Tipo Convocatoria filter
        tipo_options = get_unique_values(df, 'tipoConvocatoria')
        filters['tipo_convocatoria'] = st.sidebar.multiselect(
            "Tipo de Convocatoria",
            options=tipo_options
        )
        
        # Status filter
        status_option = st.sidebar.radio(
            "Estado",
            options=["Todos", "Abiertas", "Cerradas"],
            index=0
        )
        if status_option == "Abiertas":
            filters['abierto'] = True
        elif status_option == "Cerradas":
            filters['abierto'] = False
        else:
            filters['abierto'] = None
        
        # Apply filters button
        if st.sidebar.button("🔍 Aplicar Filtros", type="primary", use_container_width=True):
            st.session_state['apply_filters'] = True
        
        # Clear filters button
        if st.sidebar.button("🔄 Limpiar Filtros", use_container_width=True):
            st.session_state['apply_filters'] = False
            st.rerun()
        
        # Apply filters
        if st.session_state.get('apply_filters', False):
            filtered_df = apply_filters(df, filters)
        else:
            filtered_df = df
        
        # Display summary
        st.subheader("Resumen de Resultados")
        display_summary_stats(filtered_df)
        
        # Display results table
        st.subheader(f"Resultados ({len(filtered_df):,} registros)")
        
        if len(filtered_df) > 0:
            # Select columns to display
            display_columns = [
                'codigoBDNS', 'fechaRecepcion', 'descripcion', 'presupuestoTotal',
                'organo_nivel1', 'region_descripcion', 'sector_descripcion',
                'tipoBeneficiario_descripcion', 'tipoConvocatoria', 'abierto', 
                'fechaInicioSolicitud', 'fechaFinSolicitud'
            ]
            
            # Filter only existing columns
            display_columns = [col for col in display_columns if col in filtered_df.columns]
            
            # Format the dataframe for display
            display_df = filtered_df[display_columns].copy()
            
            # Format dates (keep as strings for display)
            for col in ['fechaRecepcion', 'fechaInicioSolicitud', 'fechaFinSolicitud']:
                if col in display_df.columns:
                    display_df[col] = display_df[col].dt.strftime('%Y-%m-%d')
            
            # Format boolean
            if 'abierto' in display_df.columns:
                display_df['abierto'] = display_df['abierto'].map({True: '✅ Abierta', False: '❌ Cerrada'})
            
            # Rename columns for better display
            column_names = {
                'codigoBDNS': 'BDNS',
                'fechaRecepcion': 'Fecha Recepción',
                'descripcion': 'Descripción',
                'presupuestoTotal': 'Presupuesto',
                'organo_nivel1': 'Institución',
                'region_descripcion': 'Región',
                'sector_descripcion': 'Sector',
                'tipoBeneficiario_descripcion': 'Beneficiario',
                'tipoConvocatoria': 'Tipo',
                'abierto': 'Estado',
                'fechaInicioSolicitud': 'Inicio Solicitud',
                'fechaFinSolicitud': 'Fin Solicitud'
            }
            display_df = display_df.rename(columns=column_names)
            
            # Configure column formatting (keeps numeric values for sorting)
            column_config = {}
            if 'Presupuesto' in display_df.columns:
                column_config['Presupuesto'] = st.column_config.NumberColumn(
                    'Presupuesto',
                    format="€%.0f",
                    help="Presupuesto total de la convocatoria"
                )
            
            # Display interactive dataframe
            st.dataframe(
                display_df,
                use_container_width=True,
                height=600,
                hide_index=True,
                column_config=column_config
            )
            
            # Download button
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Resultados (CSV)",
                data=csv,
                file_name="bdns_filtrados.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.warning("No se encontraron resultados con los filtros aplicados.")
    
    with tab2:
        st.subheader("📈 Análisis por Año")
        
        years = sorted(df['year'].dropna().unique())
        
        for year in years:
            df_year = df[df['year'] == year]
            
            with st.expander(f"Año {int(year)}", expanded=False):
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Registros", f"{len(df_year):,}")
                with col2:
                    st.metric("BDNS Únicos", f"{df_year['codigoBDNS'].nunique():,}")
                with col3:
                    total = df_year['presupuestoTotal'].sum()
                    st.metric("Presupuesto Total", f"€{total:,.0f}")
                with col4:
                    avg = df_year['presupuestoTotal'].mean()
                    st.metric("Presupuesto Medio", f"€{avg:,.0f}")
                
                # Date range
                min_date = df_year['fechaRecepcion'].min()
                max_date = df_year['fechaRecepcion'].max()
                st.write(f"**Rango de fechas:** {min_date.strftime('%Y-%m-%d')} a {max_date.strftime('%Y-%m-%d')}")
                
                # Status
                status_counts = df_year['abierto'].value_counts()
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"✅ **Abiertas:** {status_counts.get(True, 0):,}")
                with col2:
                    st.write(f"❌ **Cerradas:** {status_counts.get(False, 0):,}")
                
                # Top regions and sectors
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Top 5 Regiones:**")
                    top_regions = df_year['region_descripcion'].value_counts().head(5)
                    for i, (region, count) in enumerate(top_regions.items(), 1):
                        st.write(f"{i}. {region}: {count:,}")
                
                with col2:
                    st.write("**Top 5 Sectores:**")
                    top_sectors = df_year['sector_descripcion'].value_counts().head(5)
                    for i, (sector, count) in enumerate(top_sectors.items(), 1):
                        st.write(f"{i}. {sector}: {count:,}")


if __name__ == "__main__":
    main()

