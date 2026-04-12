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
    col_logo, col_title = st.columns([1, 5])

    with col_logo:
        st.image("logo.png", width=100)

    with col_title:
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
    Soporte multitaller
    """
    with st.expander("🔧 Panel de Debug (Diagnóstico)", expanded=False):
        
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
            
            # Información de multitaller
            if "TALLER_ORIGEN" in df.columns:
                st.write("**Información Multitaller:**")
                st.write(f"  - Talleres únicos: {df['TALLER_ORIGEN'].nunique()}")
                st.write(f"  - Lista de talleres: {df['TALLER_ORIGEN'].unique().tolist()}")
                
                # Desglose por taller
                st.write("  - Registros por taller:")
                for taller, count in df.groupby("TALLER_ORIGEN").size().items():
                    st.write(f"    - {taller}: {count}")
            
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
    
    # Información básica
    mensaje = f"✅ Datos cargados: **{len(df)}** registros | Última actualización: {datetime.now().strftime('%H:%M:%S')}"
    
    # Si es multitaller, mostrar desglose por taller
    if "TALLER_ORIGEN" in df.columns:
        talleres = df["TALLER_ORIGEN"].unique()
        if len(talleres) > 1:
            # Crear desglose por taller
            desglose = df.groupby("TALLER_ORIGEN").size().to_dict()
            detalle = " | ".join([f"**{t}**: {c} regs" for t, c in desglose.items()])
            mensaje += f"\n\n🏪 **Desglose por taller:** {detalle}"
    
    st.success(mensaje)
    
    # Información de filtros aplicados
    if len(df_filtered) != len(df):
        st.info(f"📊 Mostrando {len(df_filtered)} de {len(df)} registros (filtros aplicados)")


def render_export_section(df_filtered, filtros):
    """Sección de exportación de datos"""
    from .exporters import generate_excel_report, generate_csv_export, generate_pdf_report
    from .fee_config import load_fee_config

    st.divider()
    st.header("📥 Exportación de Datos")

    # Toggle para incluir honorarios en PDF
    fee_config = load_fee_config()
    include_honorarios = st.toggle(
        "📊 Incluir honorarios en el reporte PDF",
        value=not fee_config.get('hide_fees_presentation', False),
        help="Activa/desactiva la inclusión de datos de honorarios en el PDF exportado"
    )

    col_exp1, col_exp2, col_exp3 = st.columns(3)

    # Exportar Excel
    with col_exp1:
        excel_buffer = generate_excel_report(df_filtered, filtros)
        st.download_button(
            label="📊 Descargar Excel (Múltiples hojas)",
            data=excel_buffer,
            file_name=f"distrikia_reporte_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width='stretch'
        )

    # Exportar CSV
    with col_exp2:
        csv_data = generate_csv_export(df_filtered)
        st.download_button(
            label="📄 Descargar CSV",
            data=csv_data,
            file_name=f"distrikia_datos_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            width='stretch'
        )

    # Generar PDF
    with col_exp3:
        pdf_buffer = generate_pdf_report(df_filtered, filtros, include_honorarios=include_honorarios)
        honorarios_text = "con" if include_honorarios else "sin"
        st.download_button(
            label=f"📑 Descargar PDF ({honorarios_text} honorarios)",
            data=pdf_buffer,
            file_name=f"distrikia_dashboard_{honorarios_text}_honorarios_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            width='stretch'
        )


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
