"""
================================================================================
DISTRIKIA - Sistema de Gestión de Ahorros y Análisis de Talleres Automotrices
Dashboard Ejecutivo con Auto-refresh
Versión: 1.0.0 | Fecha: Abril 2026
Stakeholders: Alexander Cano (Analista/Gerente), Sergio Romero (Operativo)
================================================================================

ARCHIVO PRINCIPAL - Entry Point
Este archivo ha sido modularizado. La lógica se encuentra en el paquete modules/.
"""

# Importar configuración
from modules.config import setup_page_config, apply_custom_css

# Importar carga de datos
from modules.data_loader import load_data_from_sheets
from modules.data_processor import get_debug_logs

# Importar validaciones
from modules.validators import run_validations

# Importar visualizaciones
from modules.visualizations import (
    render_kpis,
    render_grafico_ahorro_mes,
    render_grafico_causales,
    render_grafico_tasa_imprevistos,
    render_grafico_cambio_repuestos,
    render_tabla_detalle,
    render_recuperacion_mensual
)

# Importar sidebar y filtros
from modules.sidebar import render_sidebar, render_filtros, aplicar_filtros

# Importar componentes UI
from modules.components import (
    render_header,
    render_footer,
    render_debug_panel,
    render_alerts,
    render_data_info,
    render_export_section,
    render_error_state,
    render_empty_state
)

import streamlit as st


# ============================================================================
# CONFIGURACIÓN INICIAL
# ============================================================================

setup_page_config()
apply_custom_css()


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Función principal del dashboard"""
    
    # Header
    render_header()
    
    # Sidebar
    sheet_url, auto_refresh = render_sidebar()
    
    # DEBUG
    st.sidebar.write(f"📊 Intentando cargar desde: {sheet_url[:50]}...")
    
    # Cargar datos
    with st.spinner("🔄 Cargando datos desde Google Sheets..."):
        df, error = load_data_from_sheets(sheet_url)
    
    # Panel de Debug
    render_debug_panel(df, error, get_debug_logs())
    
    # Manejar errores
    if error:
        render_error_state(error)
        return
    
    if df is None or df.empty:
        render_empty_state()
        return
    
    # Información de datos cargados
    
    # Validaciones (RF-005)
    alerts = run_validations(df)
    render_alerts(alerts)
    
    # Filtros
    filtros = render_filtros(df)
    df_filtered = aplicar_filtros(df, filtros)
    
    # Info de datos y filtros
    render_data_info(df, df_filtered)
    
    # =========================================================================
    # DASHBOARD CONTENT
    # =========================================================================
    
    # KPIs (RF-003.1)
    render_kpis(df_filtered)
    
    st.divider()
    
    # Primera fila de gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        render_grafico_ahorro_mes(df_filtered)  # RF-003.4
    
    with col2:
        render_grafico_causales(df_filtered)  # RF-003.5
    
    # Segunda fila de gráficos
    col3, col4 = st.columns(2)
    
    with col3:
        render_grafico_tasa_imprevistos(df_filtered)  # RF-003.3
    
    with col4:
        render_grafico_cambio_repuestos(df_filtered)  # RF-003.2
    
    st.divider()
    
    # Recuperación mensual (RF-003.7)
    render_recuperacion_mensual(df_filtered)
    
    st.divider()
    
    # Tabla detallada (RF-003.6)
    render_tabla_detalle(df_filtered)
    
    # Exportación (RF-004)
    render_export_section(df_filtered, filtros)
    
    # Footer
    render_footer()


if __name__ == "__main__":
    main()
