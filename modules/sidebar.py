"""
================================================================================
SIDEBAR - Distrikia Dashboard
================================================================================
Funciones para el panel lateral: configuración, filtros y auto-refresh.
"""

import streamlit as st
import time
from datetime import datetime


# ============================================================================
# CONFIGURACIÓN DEL SIDEBAR
# ============================================================================

def render_sidebar():
    """Configuración y filtros en sidebar"""
    
    st.sidebar.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2 style="color: #0066CC; margin-bottom: 0.5rem;">🚗 DISTRIKIA</h2>
        <p style="color: #64748B; font-size: 0.9rem;">Sistema de Gestión de Ahorros</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Configuración de conexión
    st.sidebar.header("🔗 Conexión a Datos")
    
    # URL de Google Sheets
    default_url = st.secrets.get("SHEET_URL", "https://docs.google.com/spreadsheets/d/13sR-FFPIasaY0xlkpmcZnyLJfCVKGUNNoK4RFO6R6pY/edit")
    if not default_url:
        default_url = "https://docs.google.com/spreadsheets/d/TU_ID/edit"
    
    sheet_url = st.sidebar.text_input(
        "URL de Google Sheets",
        value=default_url,
        type="password",
        help="Pega aquí la URL de tu hoja de cálculo"
    )
    
    # Guardar en session state
    st.session_state['sheet_url'] = sheet_url
    
    st.sidebar.divider()
    
    # Auto-refresh
    st.sidebar.header("⏱️ Actualización Automática")
    auto_refresh = st.sidebar.toggle("Auto-refresh activado", value=False)
    
    if auto_refresh:
        refresh_interval = st.sidebar.slider("Intervalo (segundos)", 10, 300, 30, step=10)
        st.sidebar.caption(f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")
        
        # Trigger refresh
        time.sleep(refresh_interval)
        st.rerun()
    
    st.sidebar.divider()
    
    return sheet_url, auto_refresh


# ============================================================================
# FILTROS DE DATOS
# ============================================================================

def render_filtros(df):
    """Filtros dinámicos basados en los datos"""
    
    st.sidebar.header("🔍 Filtros de Datos")
    
    filtros = {}
    
    # Filtro de Año
    if 'AÑO' in df.columns:
        años = sorted(df['AÑO'].dropna().unique(), reverse=True)
        años_options = ["Todos"] + [str(int(a)) for a in años if a > 0]
        filtros['año'] = st.sidebar.selectbox("📅 Año", años_options)
    
    # Filtro de Mes
    if 'MES' in df.columns:
        meses = sorted(df['MES'].dropna().unique())
        meses_names = ["Todos"] + [datetime(2000, int(m), 1).strftime('%B') for m in meses if m > 0]
        mes_sel = st.sidebar.selectbox("📆 Mes", meses_names)
        filtros['mes'] = mes_sel if mes_sel == "Todos" else meses_names.index(mes_sel)
    
    # Filtro de Compañía
    if 'COMPAÑIA_DE_SEGUROS' in df.columns:
        cias = sorted(df['COMPAÑIA_DE_SEGUROS'].dropna().unique())
        cias = [c for c in cias if c != '']
        filtros['compañia'] = st.sidebar.multiselect(
            "🏢 Compañía de Seguros",
            options=cias,
            default=[]
        )
    
    # Filtro de Estado
    if 'ESTATUS' in df.columns:
        estados = sorted(df['ESTATUS'].dropna().unique())
        estados = [e for e in estados if e != '']
        filtros['estado'] = st.sidebar.multiselect(
            "📋 Estado Autorización",
            options=estados,
            default=[]
        )
    
    # Filtro de Acción
    if 'ACCION' in df.columns:
        acciones = sorted(df['ACCION'].dropna().unique())
        acciones = [a for a in acciones if a != '']
        filtros['accion'] = st.sidebar.multiselect(
            "🔧 Tipo de Acción",
            options=acciones,
            default=[]
        )
    
    # Filtro de rango de fechas
    if 'FECHA_INGR' in df.columns:
        st.sidebar.divider()
        st.sidebar.subheader("📅 Rango de Fechas")
        
        fechas_validas = df[df['FECHA_INGR'].notna()]['FECHA_INGR']
        if not fechas_validas.empty:
            min_date = fechas_validas.min().date()
            max_date = fechas_validas.max().date()
            
            filtros['fecha_desde'] = st.sidebar.date_input("Desde", value=min_date, min_value=min_date, max_value=max_date)
            filtros['fecha_hasta'] = st.sidebar.date_input("Hasta", value=max_date, min_value=min_date, max_value=max_date)
    
    # Botón de limpiar filtros
    if st.sidebar.button("🧹 Limpiar Filtros", type="secondary"):
        st.rerun()
    
    return filtros


def aplicar_filtros(df, filtros):
    """Aplicar filtros seleccionados al dataframe"""
    
    if df is None or df.empty:
        return df
    
    df_filtered = df.copy()
    
    # Filtro de año
    if filtros.get('año') and filtros['año'] != "Todos":
        df_filtered = df_filtered[df_filtered['AÑO'] == int(filtros['año'])]
    
    # Filtro de mes
    if filtros.get('mes') and filtros['mes'] != "Todos":
        df_filtered = df_filtered[df_filtered['MES'] == int(filtros['mes'])]
    
    # Filtro de compañía
    if filtros.get('compañia') and len(filtros['compañia']) > 0:
        df_filtered = df_filtered[df_filtered['COMPAÑIA_DE_SEGUROS'].isin(filtros['compañia'])]
    
    # Filtro de estado
    if filtros.get('estado') and len(filtros['estado']) > 0:
        df_filtered = df_filtered[df_filtered['ESTATUS'].isin(filtros['estado'])]
    
    # Filtro de acción
    if filtros.get('accion') and len(filtros['accion']) > 0:
        df_filtered = df_filtered[df_filtered['ACCION'].isin(filtros['accion'])]
    
    # Filtro de fechas
    if filtros.get('fecha_desde') and 'FECHA_INGR' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['FECHA_INGR'].dt.date >= filtros['fecha_desde']]
    
    if filtros.get('fecha_hasta') and 'FECHA_INGR' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['FECHA_INGR'].dt.date <= filtros['fecha_hasta']]
    
    return df_filtered
