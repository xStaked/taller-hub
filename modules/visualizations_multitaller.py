"""
================================================================================
VISUALIZACIONES MULTITALLER - Distrikia Dashboard
================================================================================
Funciones específicas para visualizaciones comparativas entre talleres.
RF-MT: Análisis multitaller
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .config import PORCENTAJE_HONORARIOS
from .taller_config import get_color_taller, TALLERES_CONFIG
from .fee_config import calculate_fee, load_fee_config, calculate_fees_for_df


# ============================================================================
# KPIs MULTITALLER
# ============================================================================

def render_kpis_multitaller(df):
    """
    Muestra KPIs comparativos cuando hay múltiples talleres.
    """
    if df is None or df.empty:
        return
    
    if "TALLER_ORIGEN" not in df.columns:
        # Fallback: usar KPIs normales
        return
    
    talleres = df["TALLER_ORIGEN"].unique()
    
    if len(talleres) <= 1:
        # Solo hay un taller, no mostrar comparativas
        return
    
    st.subheader("🏪 Comparativa de Talleres")

    # Calcular métricas por taller
    resumen = df.groupby("TALLER_ORIGEN").agg({
        "DIFERENCIA": ["sum", "mean", "count"],
        "PLACA": "nunique"
    }).reset_index()

    resumen.columns = ["TALLER", "AHORRO_TOTAL", "AHORRO_PROMEDIO", "TOTAL_REPARACIONES", "VEHICULOS_UNICOS"]
    
    # Apply per-taller fee calculation
    fee_config = load_fee_config()
    fee_info = calculate_fees_for_df(df, fee_config)
    
    # Update resumen with per-taller fees
    for idx, row in resumen.iterrows():
        taller = row["TALLER"]
        if taller in fee_info['by_taller']:
            resumen.loc[idx, "HONORARIOS"] = fee_info['by_taller'][taller]['fee_amount']
            resumen.loc[idx, "UTILIDAD"] = row["AHORRO_TOTAL"] - fee_info['by_taller'][taller]['fee_amount']
        else:
            # Fallback to default calculation
            resumen.loc[idx, "HONORARIOS"] = row["AHORRO_TOTAL"] * fee_config['global_defaults']['base_percentage']
            resumen.loc[idx, "UTILIDAD"] = row["AHORRO_TOTAL"] - resumen.loc[idx, "HONORARIOS"]
    
    # Ordenar por ahorro total descendente
    resumen = resumen.sort_values("AHORRO_TOTAL", ascending=False)
    
    # Mostrar KPIs en cards
    cols = st.columns(len(resumen))
    
    for idx, (_, row) in enumerate(resumen.iterrows()):
        with cols[idx]:
            taller = row["TALLER"]
            
            # Buscar color del taller
            color = "#0066CC"
            for tid, tconf in TALLERES_CONFIG.items():
                if tconf["nombre"] == taller and "color" in tconf:
                    color = tconf["color"]
                    break
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {color}22 0%, {color}11 100%); 
                        border-left: 4px solid {color}; 
                        border-radius: 12px; padding: 1rem;">
                <div style="font-size: 1rem; font-weight: 700; color: {color}; margin-bottom: 0.5rem;">
                    {taller}
                </div>
                <div style="font-size: 1.5rem; font-weight: 800; color: #1E293B;">
                    ${row["AHORRO_TOTAL"]:,.0f}
                </div>
                <div style="font-size: 0.8rem; color: #64748B; margin-top: 0.25rem;">
                    💰 Ahorro Total
                </div>
                <div style="margin-top: 0.75rem; border-top: 1px solid #E2E8F0; padding-top: 0.5rem;">
                    <div style="font-size: 0.8rem; color: #475569;">
                        📊 {row["TOTAL_REPARACIONES"]} reparaciones<br>
                        🚗 {row["VEHICULOS_UNICOS"]} vehículos<br>
                        💵 ${row["UTILIDAD"]:,.0f} utilidad
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_ranking_talleres(df):
    """
    Muestra un ranking visual de talleres por diferentes métricas.
    """
    if df is None or df.empty or "TALLER_ORIGEN" not in df.columns:
        return
    
    talleres = df["TALLER_ORIGEN"].unique()
    if len(talleres) <= 1:
        return
    
    st.divider()
    st.subheader("🏆 Ranking de Talleres")
    
    # Calcular métricas
    resumen = df.groupby("TALLER_ORIGEN").agg({
        "DIFERENCIA": ["sum", "mean"],
        "PLACA": "count"
    }).reset_index()
    
    resumen.columns = ["TALLER", "AHORRO_TOTAL", "AHORRO_PROMEDIO", "REPARACIONES"]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**💰 Por Ahorro Total**")
        top_ahorro = resumen.nlargest(3, "AHORRO_TOTAL")
        for i, (_, row) in enumerate(top_ahorro.iterrows(), 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            st.markdown(f"{emoji} **{row['TALLER']}**<br>${row['AHORRO_TOTAL']:,.0f}", unsafe_allow_html=True)
    
    with col2:
        st.markdown("**📊 Por Reparaciones**")
        top_rep = resumen.nlargest(3, "REPARACIONES")
        for i, (_, row) in enumerate(top_rep.iterrows(), 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            st.markdown(f"{emoji} **{row['TALLER']}**<br>{row['REPARACIONES']} reparaciones", unsafe_allow_html=True)
    
    with col3:
        st.markdown("**📈 Por Promedio**")
        top_prom = resumen.nlargest(3, "AHORRO_PROMEDIO")
        for i, (_, row) in enumerate(top_prom.iterrows(), 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            st.markdown(f"{emoji} **{row['TALLER']}**<br>${row['AHORRO_PROMEDIO']:,.0f}/rep", unsafe_allow_html=True)


# ============================================================================
# GRÁFICOS COMPARATIVOS MULTITALLER
# ============================================================================

def render_grafico_comparativo_ahorro(df):
    """
    Gráfico de barras comparando ahorro por taller.
    """
    if df is None or df.empty or "TALLER_ORIGEN" not in df.columns:
        return
    
    talleres = df["TALLER_ORIGEN"].unique()
    if len(talleres) <= 1:
        return
    
    # Preparar datos
    resumen = df.groupby("TALLER_ORIGEN").agg({
        "DIFERENCIA": "sum",
        "PLACA": "count"
    }).reset_index()
    resumen.columns = ["TALLER", "AHORRO", "REPARACIONES"]
    
    # Crear gráfico
    fig = px.bar(
        resumen,
        x="TALLER",
        y="AHORRO",
        color="TALLER",
        text=resumen["AHORRO"].apply(lambda x: f"${x:,.0f}"),
        title="💰 Comparativa de Ahorro por Taller",
        labels={"AHORRO": "Ahorro Total ($)", "TALLER": ""}
    )
    
    fig.update_traces(textposition="outside")
    fig.update_layout(
        showlegend=False,
        height=400,
        yaxis_tickformat="$,.0f"
    )
    
    st.plotly_chart(fig, width='stretch')


def render_grafico_tendencia_por_taller(df):
    """
    Gráfico de líneas mostrando la tendencia de ahorro por taller a lo largo del tiempo.
    """
    if df is None or df.empty:
        return
    
    if "TALLER_ORIGEN" not in df.columns or "AÑO" not in df.columns or "MES" not in df.columns:
        return
    
    talleres = df["TALLER_ORIGEN"].unique()
    if len(talleres) <= 1:
        return
    
    # Filtrar datos válidos
    df_valid = df[(df['AÑO'].notna()) & (df['MES'].notna()) & 
                  (df['AÑO'] > 2000) & (df['MES'] >= 1) & (df['MES'] <= 12)]
    
    if df_valid.empty:
        return
    
    # Agrupar por taller, año y mes
    df_mes = df_valid.groupby(["TALLER_ORIGEN", "AÑO", "MES"]).agg({
        "DIFERENCIA": "sum"
    }).reset_index()
    
    # Crear fecha
    df_mes["FECHA"] = pd.to_datetime(
        df_mes["AÑO"].astype(str) + "-" + df_mes["MES"].astype(str) + "-01",
        errors="coerce"
    )
    df_mes = df_mes[df_mes["FECHA"].notna()]
    df_mes = df_mes.sort_values("FECHA")
    df_mes["TEXTO_FECHA"] = df_mes["FECHA"].dt.strftime("%b %Y")
    
    # Crear gráfico
    fig = go.Figure()
    
    for taller in talleres:
        df_taller = df_mes[df_mes["TALLER_ORIGEN"] == taller]
        if not df_taller.empty:
            # Buscar color
            color = "#0066CC"
            for tid, tconf in TALLERES_CONFIG.items():
                if tconf["nombre"] == taller and "color" in tconf:
                    color = tconf["color"]
                    break
            
            fig.add_trace(go.Scatter(
                x=df_taller["TEXTO_FECHA"],
                y=df_taller["DIFERENCIA"],
                mode="lines+markers",
                name=taller,
                line=dict(color=color, width=2),
                marker=dict(size=6)
            ))
    
    fig.update_layout(
        title="📈 Evolución de Ahorros por Taller",
        xaxis_title="Mes",
        yaxis_title="Ahorro ($)",
        height=450,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis_tickformat="$,.0f"
    )
    
    st.plotly_chart(fig, width='stretch')


def render_heatmap_talleres_meses(df):
    """
    Heatmap de ahorro por taller y mes.
    """
    if df is None or df.empty:
        return
    
    if "TALLER_ORIGEN" not in df.columns or "AÑO" not in df.columns or "MES" not in df.columns:
        return
    
    talleres = df["TALLER_ORIGEN"].unique()
    if len(talleres) <= 1:
        return
    
    # Preparar datos
    df_valid = df[(df['AÑO'].notna()) & (df['MES'].notna())]
    
    if df_valid.empty:
        return
    
    pivot = df_valid.pivot_table(
        values="DIFERENCIA",
        index="TALLER_ORIGEN",
        columns=["AÑO", "MES"],
        aggfunc="sum",
        fill_value=0
    )
    
    # Formatear nombres de columnas
    pivot.columns = [f"{int(año)}-{int(mes):02d}" for año, mes in pivot.columns]
    
    # Crear heatmap
    fig = px.imshow(
        pivot,
        labels=dict(x="Período", y="Taller", color="Ahorro ($)"),
        title="🔥 Mapa de Calor: Ahorro por Taller y Mes",
        color_continuous_scale="Blues",
        aspect="auto"
    )
    
    fig.update_layout(height=400)
    
    st.plotly_chart(fig, width='stretch')


def render_distribucion_por_taller(df):
    """
    Gráfico de pastel/torta mostrando la distribución del ahorro entre talleres.
    """
    if df is None or df.empty or "TALLER_ORIGEN" not in df.columns:
        return
    
    talleres = df["TALLER_ORIGEN"].unique()
    if len(talleres) <= 1:
        return
    
    # Calcular totales por taller
    resumen = df.groupby("TALLER_ORIGEN")["DIFERENCIA"].sum().reset_index()
    resumen = resumen.sort_values("DIFERENCIA", ascending=False)
    
    # Colores personalizados
    colors = []
    for taller in resumen["TALLER_ORIGEN"]:
        color = "#0066CC"
        for tid, tconf in TALLERES_CONFIG.items():
            if tconf["nombre"] == taller and "color" in tconf:
                color = tconf["color"]
                break
        colors.append(color)
    
    # Crear gráfico de dona
    fig = go.Figure(data=[go.Pie(
        labels=resumen["TALLER_ORIGEN"],
        values=resumen["DIFERENCIA"],
        hole=0.5,
        marker_colors=colors,
        textinfo="label+percent",
        textposition="outside",
        hovertemplate="<b>%{label}</b><br>Ahorro: $%{value:,.0f}<br>Porcentaje: %{percent}<extra></extra>"
    )])
    
    # Agregar total en el centro
    total = resumen["DIFERENCIA"].sum()
    fig.add_annotation(
        text=f"<b>Total</b><br>${total:,.0f}",
        showarrow=False,
        font=dict(size=16)
    )
    
    fig.update_layout(
        title="📊 Distribución del Ahorro entre Talleres",
        height=450,
        showlegend=True
    )
    
    st.plotly_chart(fig, width='stretch')


# ============================================================================
# TABLA RESUMEN MULTITALLER
# ============================================================================

def render_tabla_resumen_talleres(df):
    """
    Tabla detallada con métricas por taller.
    """
    if df is None or df.empty or "TALLER_ORIGEN" not in df.columns:
        return
    
    talleres = df["TALLER_ORIGEN"].unique()
    if len(talleres) <= 1:
        return
    
    st.subheader("📋 Resumen Detallado por Taller")

    # Calcular métricas
    resumen = df.groupby("TALLER_ORIGEN").agg({
        "DIFERENCIA": ["sum", "mean", "count"],
        "PLACA": "nunique",
        "M._DE_O._INICIAL": "sum",
        "M._DE_O._FINAL": "sum"
    }).reset_index()

    resumen.columns = ["TALLER", "AHORRO_TOTAL", "AHORRO_PROMEDIO", "REPARACIONES",
                       "VEHICULOS", "MO_INICIAL", "MO_FINAL"]

    # Calcular derivados con regla de umbral por taller
    fee_config = load_fee_config()
    hide_fees = fee_config.get('hide_fees_presentation', False)
    
    # Use per-taller fee calculations
    fee_info = calculate_fees_for_df(df, fee_config)
    
    # Update resumen with per-taller fees
    for idx, row in resumen.iterrows():
        taller = row["TALLER"]
        if taller in fee_info['by_taller']:
            resumen.loc[idx, "HONORARIOS"] = fee_info['by_taller'][taller]['fee_amount']
            resumen.loc[idx, "UTILIDAD"] = row["AHORRO_TOTAL"] - fee_info['by_taller'][taller]['fee_amount']
        else:
            # Fallback
            resumen.loc[idx, "HONORARIOS"] = row["AHORRO_TOTAL"] * fee_config['global_defaults']['base_percentage']
            resumen.loc[idx, "UTILIDAD"] = row["AHORRO_TOTAL"] - resumen.loc[idx, "HONORARIOS"]
    
    resumen["EFICIENCIA"] = ((resumen["MO_INICIAL"] - resumen["MO_FINAL"]) / resumen["MO_INICIAL"] * 100).round(1)

    # Formatear para display
    display = resumen.copy()
    cols_moneda = ["AHORRO_TOTAL", "AHORRO_PROMEDIO", "MO_INICIAL", "MO_FINAL", "HONORARIOS", "UTILIDAD"]
    for col in cols_moneda:
        display[col] = display[col].apply(lambda x: f"${x:,.0f}")

    display["EFICIENCIA"] = display["EFICIENCIA"].apply(lambda x: f"{x}%")

    # Reordenar columnas
    if hide_fees:
        display = display[["TALLER", "REPARACIONES", "VEHICULOS", "AHORRO_TOTAL",
                           "AHORRO_PROMEDIO", "UTILIDAD", "EFICIENCIA"]]
        display.columns = ["Taller", "Reparaciones", "Vehículos", "Ahorro Total",
                           "Promedio", "Utilidad", "Eficiencia"]
        st.info("🔒 Modo presentación activo - Columnas de honorarios ocultas")
    else:
        display = display[["TALLER", "REPARACIONES", "VEHICULOS", "AHORRO_TOTAL",
                           "AHORRO_PROMEDIO", "HONORARIOS", "UTILIDAD", "EFICIENCIA"]]
        display.columns = ["Taller", "Reparaciones", "Vehículos", "Ahorro Total",
                           "Promedio", "Honorarios", "Utilidad", "Eficiencia"]

    st.dataframe(display, width='stretch', hide_index=True)
    
    # Botón de exportación
    col1, col2 = st.columns([1, 4])
    with col1:
        csv = resumen.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar CSV",
            data=csv,
            file_name="resumen_talleres.csv",
            mime="text/csv"
        )


# ============================================================================
# PESTAÑAS DE VISTA MULTITALLER
# ============================================================================

def render_vista_multitaller(df, key_suffix=""):
    """
    Renderiza la vista completa de análisis multitaller con pestañas.
    
    Args:
        df: DataFrame consolidado con columna TALLER_ORIGEN
        key_suffix: Sufijo para keys únicos de Streamlit
    """
    if df is None or df.empty or "TALLER_ORIGEN" not in df.columns:
        return
    
    talleres = df["TALLER_ORIGEN"].unique()
    if len(talleres) <= 1:
        return
    
    # Crear pestañas
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Comparativa", 
        "📈 Tendencias", 
        "🔥 Heatmap",
        "📋 Detalle"
    ])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            render_grafico_comparativo_ahorro(df)
        with col2:
            render_distribucion_por_taller(df)
    
    with tab2:
        render_grafico_tendencia_por_taller(df)
    
    with tab3:
        render_heatmap_talleres_meses(df)
    
    with tab4:
        render_tabla_resumen_talleres(df)
