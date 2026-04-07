"""
================================================================================
VISUALIZACIONES - Distrikia Dashboard
================================================================================
Funciones para renderizar gráficos, KPIs y tablas.
RF-003: Componentes de visualización
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .config import PORCENTAJE_HONORARIOS
from .data_processor import add_log


# ============================================================================
# KPIs PRINCIPALES
# ============================================================================

def render_kpis(df):
    """
    RF-003.1: KPIs principales
    - Ahorro acumulado
    - Valor honorarios (18%)
    - Utilidad taller
    - Promedio por reparación
    """
    add_log("render_kpis: Iniciando")
    
    if 'DIFERENCIA' not in df.columns:
        st.warning("No se encontró columna de DIFERENCIA/AHORRO")
        return
    
    total_ahorro = df['DIFERENCIA'].sum()
    total_registros = len(df)
    reparaciones_con_ahorro = len(df[df['DIFERENCIA'] > 0])
    promedio_ahorro = df[df['DIFERENCIA'] > 0]['DIFERENCIA'].mean() if reparaciones_con_ahorro > 0 else 0
    
    # Cálculo de honorarios según documento (18% o 20%)
    honorarios = total_ahorro * PORCENTAJE_HONORARIOS
    utilidad = total_ahorro - honorarios
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-container kpi-ahorro">
            <div class="kpi-value">${total_ahorro:,.0f}</div>
            <div class="kpi-label">💰 Ahorro Acumulado</div>
            <div class="kpi-delta">{reparaciones_con_ahorro} reparaciones con ahorro</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-container kpi-honorarios">
            <div class="kpi-value">${honorarios:,.0f}</div>
            <div class="kpi-label">📊 Valor Honorarios (18%)</div>
            <div class="kpi-delta">Del ahorro total generado</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-container kpi-utilidad">
            <div class="kpi-value">${utilidad:,.0f}</div>
            <div class="kpi-label">🏆 Utilidad Taller</div>
            <div class="kpi-delta">Ahorro - Honorarios</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="kpi-container kpi-promedio">
            <div class="kpi-value">${promedio_ahorro:,.0f}</div>
            <div class="kpi-label">📈 Promedio/Reparación</div>
            <div class="kpi-delta">Solo reparaciones con ahorro positivo</div>
        </div>
        """, unsafe_allow_html=True)


# ============================================================================
# GRÁFICO DE AHORRO POR MES
# ============================================================================

def render_grafico_ahorro_mes(df):
    """
    RF-003.4: Gráfico de ahorro por mes (línea de tendencia)
    """
    add_log("render_grafico_ahorro_mes: Iniciando")
    
    if 'AÑO' not in df.columns or 'MES' not in df.columns:
        st.warning("Datos de fecha incompletos para gráfico mensual")
        return
    
    # Filtrar solo registros con AÑO y MES válidos
    df_valid = df[(df['AÑO'].notna()) & (df['MES'].notna()) & 
                  (df['AÑO'] > 2000) & (df['MES'] >= 1) & (df['MES'] <= 12)]
    
    if df_valid.empty:
        st.warning("No hay datos con fechas válidas para el gráfico")
        return
    
    df_mes = df_valid.groupby(['AÑO', 'MES']).agg({
        'DIFERENCIA': 'sum',
        'PLACA': 'nunique'
    }).reset_index()
    
    # Asegurar que AÑO y MES sean enteros válidos
    df_mes['AÑO'] = df_mes['AÑO'].astype(int)
    df_mes['MES'] = df_mes['MES'].astype(int)
    
    # Crear fecha con manejo de errores
    try:
        df_mes['FECHA'] = pd.to_datetime(
            df_mes['AÑO'].astype(str) + '-' + df_mes['MES'].astype(str) + '-01',
            format='%Y-%m-%d',
            errors='coerce'
        )
    except Exception as e:
        st.error(f"Error creando fechas: {e}")
        st.write(f"Valores de AÑO: {df_mes['AÑO'].tolist()}")
        st.write(f"Valores de MES: {df_mes['MES'].tolist()}")
        return
    
    # Filtrar fechas que no se pudieron crear
    df_mes = df_mes[df_mes['FECHA'].notna()]
    df_mes = df_mes.sort_values('FECHA')
    df_mes['TEXTO_FECHA'] = df_mes['FECHA'].dt.strftime('%b %Y')
    
    fig = go.Figure()
    
    # Línea principal
    fig.add_trace(go.Scatter(
        x=df_mes['TEXTO_FECHA'],
        y=df_mes['DIFERENCIA'],
        mode='lines+markers',
        name='Ahorro Mensual',
        line=dict(color='#0066CC', width=3),
        marker=dict(size=8, color='#00A8E8', line=dict(width=2, color='white')),
        fill='tozeroy',
        fillcolor='rgba(0, 102, 204, 0.1)'
    ))
    
    # Línea de tendencia
    if len(df_mes) > 2:
        fig.add_trace(go.Scatter(
            x=df_mes['TEXTO_FECHA'],
            y=df_mes['DIFERENCIA'].rolling(window=3, min_periods=1).mean(),
            mode='lines',
            name='Tendencia (media móvil)',
            line=dict(color='#00CC66', width=2, dash='dash')
        ))
    
    fig.update_layout(
        title='📈 Evolución de Ahorros por Mes',
        xaxis_title='Mes',
        yaxis_title='Ahorro ($)',
        height=400,
        hovermode='x unified',
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    
    # Formato de eje Y como moneda
    fig.update_yaxes(tickformat='$,.0f')
    
    st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# GRÁFICO DE CAUSALES
# ============================================================================

def render_grafico_causales(df):
    """
    RF-003.5: Gráfico de causales de cambio (barras/categorías)
    """
    if 'CAUSAL' not in df.columns:
        st.warning("No se encontró columna de CAUSAL")
        return
    
    df_causal = df[df['CAUSAL'].notna() & (df['CAUSAL'] != '')].groupby('CAUSAL').agg({
        'DIFERENCIA': ['sum', 'count']
    }).reset_index()
    df_causal.columns = ['CAUSAL', 'AHORRO_TOTAL', 'CANTIDAD']
    df_causal = df_causal.sort_values('AHORRO_TOTAL', ascending=True).tail(10)
    
    fig = px.bar(
        df_causal,
        y='CAUSAL',
        x='AHORRO_TOTAL',
        orientation='h',
        color='CANTIDAD',
        color_continuous_scale='Blues',
        title='📊 Top Causales de Cambio por Valor de Ahorro',
        labels={'AHORRO_TOTAL': 'Ahorro Total ($)', 'CAUSAL': 'Causal', 'CANTIDAD': 'Frecuencia'},
        height=400
    )
    
    fig.update_traces(
        texttemplate='${x:,.0f}',
        textposition='outside'
    )
    
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        coloraxis_colorbar=dict(title="Cantidad")
    )
    
    st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# GRÁFICO DE TASA DE IMPREVISTOS
# ============================================================================

def render_grafico_tasa_imprevistos(df):
    """
    RF-003.3: Gráfico de tasa de imprevistos mensual (%)
    Un imprevisto se define como un registro con ACCION = 'CAMBIO'
    """
    if 'AÑO' not in df.columns or 'MES' not in df.columns:
        return
    
    # Filtrar solo registros con AÑO y MES válidos
    df_valid = df[(df['AÑO'].notna()) & (df['MES'].notna()) & 
                  (df['AÑO'] > 2000) & (df['MES'] >= 1) & (df['MES'] <= 12)]
    
    if df_valid.empty:
        st.warning("No hay datos con fechas válidas")
        return
    
    # Calcular tasa de imprevistos (ACCION = 'CAMBIO' indica un imprevisto con cambio de repuesto)
    df_mes = df_valid.groupby(['AÑO', 'MES']).agg({
        'ACCION': lambda x: (x.str.contains('CAMBIO', na=False)).sum(),
        'PLACA': 'count'
    }).reset_index()
    df_mes.columns = ['AÑO', 'MES', 'CON_IMPREVISTO', 'TOTAL']
    df_mes['TASA'] = (df_mes['CON_IMPREVISTO'] / df_mes['TOTAL']) * 100
    
    # Asegurar que AÑO y MES sean enteros válidos
    df_mes['AÑO'] = df_mes['AÑO'].astype(int)
    df_mes['MES'] = df_mes['MES'].astype(int)
    
    # Crear fecha
    df_mes['FECHA'] = pd.to_datetime(
        df_mes['AÑO'].astype(str) + '-' + df_mes['MES'].astype(str) + '-01',
        format='%Y-%m-%d',
        errors='coerce'
    )
    df_mes = df_mes[df_mes['FECHA'].notna()]
    df_mes = df_mes.sort_values('FECHA')
    df_mes['TEXTO_FECHA'] = df_mes['FECHA'].dt.strftime('%b %Y')
    
    # Color basado en meta de < 50%
    df_mes['COLOR'] = df_mes['TASA'].apply(lambda x: '#00CC66' if x < 50 else '#F59E0B' if x < 70 else '#DC2626')
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_mes['TEXTO_FECHA'],
        y=df_mes['TASA'],
        marker_color=df_mes['COLOR'],
        text=df_mes['TASA'].round(1).astype(str) + '%',
        textposition='outside',
        name='Tasa de Imprevistos'
    ))
    
    # Línea de meta del 50%
    fig.add_hline(y=50, line_dash="dash", line_color="#DC2626", 
                  annotation_text="Meta: < 50%", annotation_position="right")
    
    fig.update_layout(
        title='⚠️ Tasa de Imprevistos Mensual (%)',
        xaxis_title='Mes',
        yaxis_title='% de Reparaciones con Imprevistos',
        height=400,
        showlegend=False,
        yaxis=dict(range=[0, max(100, df_mes['TASA'].max() * 1.2)])
    )
    
    st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# GRÁFICO DE CAMBIO DE REPUESTOS
# ============================================================================

def render_grafico_cambio_repuestos(df):
    """
    RF-003.2: Gráfico de imprevistos con cambio de repuestos (tendencia mensual)
    """
    if 'ACCION' not in df.columns or 'AÑO' not in df.columns:
        return
    
    # Filtrar solo registros con AÑO y MES válidos
    df_valid = df[(df['AÑO'].notna()) & (df['MES'].notna()) & 
                  (df['AÑO'] > 2000) & (df['MES'] >= 1) & (df['MES'] <= 12)]
    
    # Filtrar solo cambios de repuestos
    df_cambios = df_valid[df_valid['ACCION'].str.contains('CAMBIO', na=False)].copy()
    
    if df_cambios.empty:
        st.info("No se encontraron registros con acción de CAMBIO")
        return
    
    df_mes = df_cambios.groupby(['AÑO', 'MES']).agg({
        'DIFERENCIA': 'sum',
        'PLACA': 'count'
    }).reset_index()
    
    # Asegurar que AÑO y MES sean enteros válidos
    df_mes['AÑO'] = df_mes['AÑO'].astype(int)
    df_mes['MES'] = df_mes['MES'].astype(int)
    
    # Crear fecha
    df_mes['FECHA'] = pd.to_datetime(
        df_mes['AÑO'].astype(str) + '-' + df_mes['MES'].astype(str) + '-01',
        format='%Y-%m-%d',
        errors='coerce'
    )
    df_mes = df_mes[df_mes['FECHA'].notna()]
    df_mes = df_mes.sort_values('FECHA')
    df_mes['TEXTO_FECHA'] = df_mes['FECHA'].dt.strftime('%b %Y')
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Barras: Cantidad de cambios
    fig.add_trace(
        go.Bar(
            x=df_mes['TEXTO_FECHA'],
            y=df_mes['PLACA'],
            name='Cantidad de Cambios',
            marker_color='rgba(0, 168, 232, 0.6)'
        ),
        secondary_y=False
    )
    
    # Línea: Valor de ahorro
    fig.add_trace(
        go.Scatter(
            x=df_mes['TEXTO_FECHA'],
            y=df_mes['DIFERENCIA'],
            name='Ahorro por Cambios',
            mode='lines+markers',
            line=dict(color='#00CC66', width=3),
            marker=dict(size=8)
        ),
        secondary_y=True
    )
    
    fig.update_layout(
        title='🔧 Imprevistos con Cambio de Repuestos - Tendencia',
        height=400,
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    
    fig.update_yaxes(title_text="Cantidad de Cambios", secondary_y=False)
    fig.update_yaxes(title_text="Ahorro ($)", secondary_y=True, tickformat='$,.0f')
    
    st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# TABLA DE DETALLE
# ============================================================================

def render_tabla_detalle(df):
    """
    RF-003.6: Tabla de ahorro por día con filtro de fechas
    """
    st.subheader("📋 Detalle de Reparaciones")
    
    # Seleccionar columnas para mostrar
    columnas_display = []
    columnas_posibles = ['FECHA_INGR', 'PLACA', 'MARCA', 'LINEA', 'COMPAÑIA_DE_SEGUROS',
                        'IMPREVISTO', 'ACCION', 'CAUSAL', 'M._DE_O._INICIAL', 
                        'M._DE_O._FINAL', 'DIFERENCIA', 'ESTATUS', 'OBSERVACION']
    
    for col in columnas_posibles:
        if col in df.columns:
            columnas_display.append(col)
    
    df_display = df[columnas_display].copy()
    
    # Ordenar por ahorro descendente
    if 'DIFERENCIA' in df_display.columns:
        df_display = df_display.sort_values('DIFERENCIA', ascending=False)
    
    # Formatear monedas
    for col in ['M._DE_O._INICIAL', 'M._DE_O._FINAL', 'DIFERENCIA']:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(lambda x: f"${x:,.0f}" if pd.notna(x) and x != 0 else "")
    
    # Formatear fechas
    if 'FECHA_INGR' in df_display.columns:
        df_display['FECHA_INGR'] = pd.to_datetime(df_display['FECHA_INGR'], errors='coerce').dt.strftime('%d/%m/%Y')
    
    # Badge para estatus
    if 'ESTATUS' in df_display.columns:
        def badge_status(status):
            if pd.isna(status):
                return ""
            status = str(status).upper()
            if 'AUTORIZ' in status:
                return '<span class="badge-autorizado">AUTORIZADO</span>'
            elif 'RECHAZ' in status:
                return '<span class="badge-rechazado">RECHAZADO</span>'
            else:
                return '<span class="badge-pendiente">PENDIENTE</span>'
        
        df_display['ESTATUS'] = df_display['ESTATUS'].apply(badge_status)
    
    # Paginación simple
    items_por_pagina = 50
    total_paginas = max(1, (len(df_display) + items_por_pagina - 1) // items_por_pagina)
    
    col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
    with col_pag2:
        pagina = st.number_input(f"Página (1-{total_paginas})", min_value=1, max_value=total_paginas, value=1)
    
    inicio = (pagina - 1) * items_por_pagina
    fin = min(inicio + items_por_pagina, len(df_display))
    
    st.caption(f"Mostrando {inicio+1}-{fin} de {len(df_display)} registros")
    
    # Mostrar tabla
    st.dataframe(
        df_display.iloc[inicio:fin],
        use_container_width=True,
        height=500,
        hide_index=True
    )


# ============================================================================
# RECUPERACIÓN MENSUAL
# ============================================================================

def render_recuperacion_mensual(df):
    """
    RF-003.7: Tabla de recuperación mensual con % de honorarios
    """
    st.subheader("📊 Recuperación Mensual con % de Honorarios")
    
    if 'AÑO' not in df.columns or 'MES' not in df.columns:
        return
    
    # Filtrar solo registros con AÑO y MES válidos
    df_valid = df[(df['AÑO'].notna()) & (df['MES'].notna()) & 
                  (df['AÑO'] > 2000) & (df['MES'] >= 1) & (df['MES'] <= 12)]
    
    if df_valid.empty:
        st.warning("No hay datos con fechas válidas")
        return
    
    resumen = df_valid.groupby(['AÑO', 'MES']).agg({
        'DIFERENCIA': ['sum', 'count'],
        'PLACA': 'nunique'
    }).reset_index()
    
    resumen.columns = ['AÑO', 'MES', 'RECUPERACION', 'CANTIDAD', 'VEHICULOS']
    resumen['%_HONORARIOS'] = 18.0  # Porcentaje fijo según documento
    resumen['VALOR_HONORARIOS'] = resumen['RECUPERACION'] * 0.18
    resumen['PAGOS'] = resumen['RECUPERACION'] - resumen['VALOR_HONORARIOS']
    
    # Formatear para display
    resumen_display = resumen.copy()
    for col in ['RECUPERACION', 'VALOR_HONORARIOS', 'PAGOS']:
        resumen_display[col] = resumen_display[col].apply(lambda x: f"${x:,.0f}")
    resumen_display['%_HONORARIOS'] = resumen_display['%_HONORARIOS'].apply(lambda x: f"{x:.0f}%")
    
    resumen_display['PERIODO'] = resumen_display.apply(lambda x: f"{x['MES']:02d}/{x['AÑO']}", axis=1)
    
    # Mostrar como tabla estilo Excel
    st.dataframe(
        resumen_display[['PERIODO', 'VEHICULOS', 'CANTIDAD', 'RECUPERACION', 
                        '%_HONORARIOS', 'VALOR_HONORARIOS', 'PAGOS']],
        use_container_width=True,
        hide_index=True,
        height=400
    )
