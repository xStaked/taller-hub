"""
================================================================================
COMPONENTES UI - Distrikia Dashboard
================================================================================
Componentes reutilizables para el dashboard.
"""

import streamlit as st
from datetime import datetime


def render_header():
    """Renderiza el header principal del dashboard"""
    st.markdown('<div class="main-header">🚗 DISTRIKIA</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Sistema de Gestión de Ahorros y Análisis de Talleres Automotrices</div>',
        unsafe_allow_html=True
    )


def render_footer():
    """Renderiza el footer del dashboard"""
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #94A3B8; font-size: 0.8rem; padding: 2rem 0;">
        <p>Distrikia Dashboard v1.0 | Desarrollado para RENOMOTRIZ</p>
        <p>Stakeholders: Alexander Cano (Analista) | Sergio Romero (Operativo)</p>
    </div>
    """, unsafe_allow_html=True)


def render_debug_panel(df, error, debug_logs):
    """
    Panel de debug para diagnosticar problemas con los datos
    """
    with st.expander("🔧 Panel de Debug (Diagnóstico)", expanded=True):
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🔄 Limpiar Caché y Recargar", type="primary"):
                st.cache_data.clear()
                st.cache_resource.clear()
                st.rerun()
        
        st.write(f"**df is None:** {df is None}")
        st.write(f"**error:** {error}")
        
        if df is not None:
            st.write(f"**df.shape:** {df.shape}")
            st.write(f"**df.empty:** {df.empty}")
            st.write(f"**Columnas:** {list(df.columns)}")
            
            # Verificar columnas críticas para gráficas
            cols_criticas = ['AÑO', 'MES', 'DIFERENCIA', 'CAUSAL', 'ACCION', 'IMPREVISTO']
            st.write("**Columnas críticas para gráficas:**")
            for col in cols_criticas:
                existe = col in df.columns
                st.write(f"  - {col}: {'✅' if existe else '❌'}")
                if existe and col == 'DIFERENCIA':
                    st.write(f"    - Suma DIFERENCIA: ${df[col].sum():,.0f}")
                    st.write(f"    - Valores > 0: {len(df[df[col] > 0])}")
                    st.write(f"    - Valores nulos: {df[col].isna().sum()}")
            
            # Mostrar logs de procesamiento
            if debug_logs:
                st.write("**Logs de procesamiento:**")
                for log in debug_logs:
                    st.text(log)
                
        else:
            st.error("❌ DataFrame es None - No se pudieron cargar los datos")


def render_alerts(alerts):
    """Muestra las alertas de validación"""
    for severity, message in alerts:
        if severity == "error":
            st.error(f"🚨 {message}")
        elif severity == "warning":
            st.warning(f"⚠️ {message}")
        elif severity == "success":
            st.success(f"✅ {message}")


def render_data_info(df, df_filtered):
    """Muestra información sobre los datos cargados y filtros aplicados"""
    st.success(f"✅ Datos cargados: {len(df)} registros | Última actualización: {datetime.now().strftime('%H:%M:%S')}")
    
    if len(df_filtered) != len(df):
        st.info(f"📊 Mostrando {len(df_filtered)} de {len(df)} registros (filtros aplicados)")


def render_export_section(df_filtered, filtros):
    """Sección de exportación de datos"""
    from .exporters import generate_excel_report, generate_csv_export
    
    st.divider()
    st.header("📥 Exportación de Datos")
    
    col_exp1, col_exp2, col_exp3 = st.columns(3)
    
    # Exportar Excel
    with col_exp1:
        excel_buffer = generate_excel_report(df_filtered, filtros)
        st.download_button(
            label="📊 Descargar Excel (Múltiples hojas)",
            data=excel_buffer,
            file_name=f"distrikia_reporte_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    # Exportar CSV
    with col_exp2:
        csv_data = generate_csv_export(df_filtered)
        st.download_button(
            label="📄 Descargar CSV",
            data=csv_data,
            file_name=f"distrikia_datos_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # Generar PDF (placeholder)
    with col_exp3:
        if st.button("📑 Generar Reporte PDF", use_container_width=True):
            st.info("💡 Para PDF: Usa la función 'Imprimir a PDF' de tu navegador (Ctrl+P)")


def render_error_state(error):
    """Muestra el estado de error cuando no se pueden cargar los datos"""
    st.error(f"❌ {error}")
    st.info("""💡 Verifica:
1. La URL de Google Sheets es correcta
2. La hoja 'BASE DE DATOS' existe
3. Las credenciales de Google Cloud están configuradas""")


def render_empty_state():
    """Muestra el estado cuando no hay datos"""
    st.warning("⚠️ No se encontraron datos en la hoja")
