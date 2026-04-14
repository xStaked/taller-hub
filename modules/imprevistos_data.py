"""
================================================================================
IMPREVISTOS DATA ENTRY - Distrikia Dashboard
================================================================================
Data entry form for the Tasa de Imprevistos module.

Features:
- Enter data by period/taller
- Record total vehicles delivered by insurance company
- Record imprevistos with type and cause
- Automatic deduplication (placa+siniestro)
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List

from .imprevistos_config import (
    IMPREVISTO_TIPOS,
    CAUSAS_MANO_OBRA,
    CAUSAS_CULPA_TALLER,
    add_imprevisto_entry,
    load_imprevistos_data,
    get_imprevistos_by_periodo,
    get_resumen_mensual,
)
from .taller_config import get_talleres_disponibles, get_nombre_taller
from .taller_manager import get_talleres_activos


# ============================================================================
# DATA ENTRY FORM
# ============================================================================

def render_imprevistos_data_entry():
    """
    Render the complete data entry form for imprevistos.
    Returns True if data was successfully added.
    """
    
    st.header("📊 Registro de Tasa de Imprevistos")
    
    st.markdown("""
    **Instrucciones:**
    1. Selecciona el taller y período
    2. Ingresa el total de vehículos entregados por compañía de seguros
    3. Registra cada imprevisto con su tipo y causal
    4. El sistema automáticamente deduplica por placa+siniestro
    """)
    
    # =========================================================================
    # STEP 1: Select workshop and period
    # =========================================================================
    st.subheader("Paso 1: Seleccionar Taller y Período")
    
    talleres = get_talleres_activos()
    
    if not talleres:
        st.warning("⚠️ No hay talleres activos. Configura al menos un taller primero.")
        return False
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        taller_id = st.selectbox(
            "🏪 Taller",
            options=list(talleres.keys()),
            format_func=lambda x: talleres[x]["nombre"],
            key="imp_taller_select"
        )
    
    with col2:
        año_actual = datetime.now().year
        año = st.selectbox(
            "📅 Año",
            options=list(range(año_actual - 2, año_actual + 2)),
            index=2,
            key="imp_año_select"
        )
    
    with col3:
        mes_actual = datetime.now().month
        mes = st.selectbox(
            "📆 Mes",
            options=list(range(1, 13)),
            index=mes_actual - 1,
            format_func=lambda x: datetime(2000, x, 1).strftime('%B'),
            key="imp_mes_select"
        )
    
    periodo = f"{año}-{mes:02d}"
    
    # =========================================================================
    # STEP 2: Enter total vehicles by insurance company
    # =========================================================================
    st.subheader("Paso 2: Total de Vehículos Entregados")
    
    total_vehiculos = st.number_input(
        "🚗 Total de vehículos entregados (por todas las compañías)",
        min_value=0,
        value=0,
        step=1,
        help="Cantidad total de vehículos que el taller recibió en este período",
        key="imp_total_vehiculos"
    )
    
    # Optional: breakdown by insurance company
    with st.expander("🏢 Desglose por Compañía de Seguros (opcional)"):
        st.info("Este desglose es opcional y no afecta el cálculo de la tasa.")
        
        num_companias = st.number_input(
            "Número de compañías de seguros",
            min_value=0,
            max_value=20,
            value=0,
            step=1,
            key="imp_num_companias"
        )
        
        companias_data = []
        for i in range(int(num_companias)):
            col_cia1, col_cia2 = st.columns(2)
            with col_cia1:
                nombre_cia = st.text_input(
                    f"Compañía {i+1}",
                    value="",
                    key=f"imp_cia_nombre_{i}"
                )
            with col_cia2:
                cant_cia = st.number_input(
                    f"Cantidad",
                    min_value=0,
                    value=0,
                    step=1,
                    key=f"imp_cia_cant_{i}"
                )
            
            if nombre_cia:
                companias_data.append({
                    "compañia": nombre_cia,
                    "cantidad": cant_cia
                })
    
    # =========================================================================
    # STEP 3: Register imprevistos
    # =========================================================================
    st.subheader("Paso 3: Registrar Imprevistos")
    
    with st.expander("➕ Agregar Nuevo Imprevisto", expanded=True):
        
        col_imp1, col_imp2 = st.columns(2)
        
        with col_imp1:
            placa = st.text_input(
                "🔖 Placa del Vehículo",
                value="",
                key="imp_placa",
                help="Ingresa la placa del vehículo (ej: ABC123)"
            ).strip().upper()
            
            siniestro = st.text_input(
                "📋 Número de Siniestro",
                value="",
                key="imp_siniestro",
                help="Número de siniestro o claim"
            ).strip().upper()
        
        with col_imp2:
            tipo_imprevisto = st.selectbox(
                "⚠️ Tipo de Imprevisto",
                options=list(IMPREVISTO_TIPOS.keys()),
                format_func=lambda x: IMPREVISTO_TIPOS[x]["label"],
                key="imp_tipo"
            )
            
            # Show causal only if MANO_OBRA
            causal = None
            if tipo_imprevisto == "MANO_OBRA":
                causal = st.selectbox(
                    "🔍 Causal",
                    options=CAUSAS_MANO_OBRA,
                    key="imp_causal",
                    help="Selecciona la causa del imprevisto"
                )
                
                # Show fault classification info
                from .imprevistos_config import es_culpa_taller
                es_culpa = es_culpa_taller(tipo_imprevisto, causal)
                
                if es_culpa:
                    st.error("❌ Este imprevisto es **culpa del taller**")
                elif es_culpa is False and causal:
                    st.success("✅ Este imprevisto **NO es culpa del taller**")
                else:
                    st.warning("⚠️ Clasificación pendiente")
        
        # Submit button for imprevisto
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        
        with col_btn1:
            agregar_imprevisto = st.button(
                "➕ Agregar Imprevisto",
                type="primary",
                use_container_width=True,
                key="imp_agregar_btn"
            )
        
        with col_btn2:
            limpiar_form = st.button(
                "🧹 Limpiar",
                use_container_width=True,
                key="imp_limpiar_btn"
            )
        
        # Process imprevisto addition
        if agregar_imprevisto:
            if not placa or not siniestro:
                st.error("❌ Debes ingresar la placa y el número de siniestro.")
            else:
                resultado = add_imprevisto_entry(
                    taller_id=taller_id,
                    taller_name=talleres[taller_id]["nombre"],
                    periodo=periodo,
                    año=año,
                    mes=mes,
                    total_vehiculos=total_vehiculos,
                    placa=placa,
                    siniestro=siniestro,
                    tipo=tipo_imprevisto,
                    causal=causal
                )
                
                if resultado:
                    st.success(f"✅ Imprevisto agregado exitosamente: {placa} + {siniestro}")
                    st.rerun()
                else:
                    st.warning(f"⚠️ Este imprevisto ya existe (deduplicación por placa+siniestro): {placa} + {siniestro}")
        
        if limpiar_form:
            st.rerun()
    
    # =========================================================================
    # STEP 4: View current period summary
    # =========================================================================
    st.subheader("Paso 4: Resumen del Período")
    
    entries = get_imprevistos_by_periodo(taller_id=taller_id, año=año, mes=mes)
    
    if entries:
        entry = entries[0]  # Should be only one for this period/taller
        
        total_imp = sum(len(e["imprevistos"]) for e in entries)
        tasa = (total_imp / total_vehiculos * 100) if total_vehiculos > 0 else 0
        
        col_sum1, col_sum2, col_sum3, col_sum4 = st.columns(4)
        
        with col_sum1:
            st.metric("🚗 Total Vehículos", total_vehiculos)
        
        with col_sum2:
            st.metric("⚠️ Total Imprevistos", total_imp)
        
        with col_sum3:
            st.metric("📊 Tasa de Imprevistos", f"{tasa:.1f}%")
        
        with col_sum4:
            culpa_taller = sum(
                1 for e in entries 
                for imp in e["imprevistos"] 
                if imp.get("es_culpa_taller")
            )
            st.metric("🏪 Culpa del Taller", culpa_taller)
        
        # Show imprevistos list
        if entries[0]["imprevistos"]:
            with st.expander(f"📋 Ver Imprevistos Registrados ({len(entries[0]['imprevistos'])})"):
                df_imprevistos = pd.DataFrame(entries[0]["imprevistos"])
                
                # Format for display
                df_display = df_imprevistos[[
                    "placa", "siniestro", "tipo", "causal", "es_culpa_taller"
                ]].copy()
                
                df_display["tipo"] = df_display["tipo"].map(
                    lambda x: IMPREVISTO_TIPOS.get(x, {}).get("label", x)
                )
                
                df_display["es_culpa_taller"] = df_display["es_culpa_taller"].map(
                    lambda x: "❌ Sí" if x else "✅ No"
                )
                
                st.dataframe(df_display, width="stretch", hide_index=True)
    else:
        st.info(f"No hay imprevistos registrados para {talleres[taller_id]['nombre']} en {datetime(año, mes, 1).strftime('%B %Y')}")
    
    return False


# ============================================================================
# QUICK VIEW: Monthly summary table
# ============================================================================

def render_resumen_mensual_table(taller_id: str = None, año: int = None):
    """
    Render the monthly summary table.
    """
    
    st.subheader("📊 Resumen Mensual")
    
    resumen = get_resumen_mensual(taller_id=taller_id, año=año)
    
    if not resumen:
        st.info("No hay datos disponibles para el resumen mensual.")
        return
    
    # Create display DataFrame
    df_resumen = pd.DataFrame(resumen)
    
    # Format for display
    df_display = df_resumen[[
        "mes", "total_vehiculos", "total_imprevistos", "tasa",
        "culpa_taller", "no_culpa_taller"
    ]].copy()
    
    df_display["mes_nombre"] = df_display["mes"].map(
        lambda x: datetime(2000, int(x), 1).strftime('%B')
    )
    
    df_display["tasa_pct"] = df_display["tasa"].map(lambda x: f"{x:.1f}%")
    df_display["culpa_taller_pct"] = df_display["culpa_taller"].map(lambda x: f"{x:.1f}%")
    
    # Reorder columns
    df_display = df_display[[
        "mes_nombre", "total_vehiculos", "total_imprevistos", "tasa_pct"
    ]].rename(columns={
        "mes_nombre": "Mes",
        "total_vehiculos": "Cantidad Vehículos",
        "total_imprevistos": "Cantidad Imprevistos",
        "tasa_pct": "Tasa (%)"
    })
    
    st.dataframe(df_display, width="stretch", hide_index=True, height=400)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def render_imprevistos_module():
    """
    Main entry point for the Imprevistos module.
    Can be called from app.py or as a standalone page.
    """
    
    # Data entry form
    render_imprevistos_data_entry()
    
    st.divider()
    
    # Monthly summary
    render_resumen_mensual_table()
