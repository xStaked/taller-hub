"""
================================================================================
PROCESAMIENTO DE DATOS - Distrikia Dashboard
================================================================================
Funciones para limpiar, transformar y procesar los datos.
RF-002: Limpieza y transformación de datos
"""

import pandas as pd
from datetime import datetime
from .config import COLUMN_MAPPING


# Variable global para logs de debug
debug_logs = []


def add_log(msg):
    """Agrega un mensaje al log de debug"""
    debug_logs.append(f"{datetime.now().strftime('%H:%M:%S')} - {msg}")


def get_debug_logs():
    """Retorna los logs de debug acumulados"""
    return debug_logs.copy()


def clear_debug_logs():
    """Limpia los logs de debug"""
    global debug_logs
    debug_logs = []


def procesar_dataframe(df, fuente="Google Sheets"):
    """
    Procesa y limpia el DataFrame con las transformaciones necesarias
    """
    global debug_logs
    debug_logs = []  # Limpiar logs anteriores
    
    add_log(f"Iniciando procesamiento desde: {fuente}")
    add_log(f"Filas originales: {len(df)}")
    add_log(f"Columnas originales: {list(df.columns)}")
    
    # =========================================================================
    # LIMPIEZA Y TRANSFORMACIÓN DE DATOS (RF-001, RF-002)
    # =========================================================================
    
    # Normalizar nombres de columnas (quitar espacios, mayúsculas, tildes)
    df.columns = df.columns.str.strip().str.upper().str.replace(' ', '_')
    # Quitar tildes de nombres de columnas
    df.columns = df.columns.str.replace('Í', 'I').str.replace('Ó', 'O').str.replace('Á', 'A').str.replace('É', 'E').str.replace('Ú', 'U')
    
    add_log(f"Columnas normalizadas: {list(df.columns)}")
    
    # Encontrar columnas reales y renombrar
    actual_columns = {}
    for standard_name, possible_names in COLUMN_MAPPING.items():
        for col in df.columns:
            if any(possible in col for possible in possible_names):
                actual_columns[standard_name] = col
                break
    
    add_log(f"Columnas mapeadas: {actual_columns}")
    
    # Renombrar columnas encontradas
    rename_map = {v: k for k, v in actual_columns.items() if v in df.columns}
    df = df.rename(columns=rename_map)
    
    add_log(f"Columnas finales: {list(df.columns)}")
    
    # =========================================================================
    # CONVERSIÓN DE TIPOS DE DATOS (RF-002)
    # =========================================================================
    
    # Campos numéricos - limpiar formato de moneda ($, comas, espacios)
    numeric_cols = ['M._DE_O._INICIAL', 'M._DE_O._FINAL', 'DIFERENCIA']
    for col in numeric_cols:
        if col in df.columns:
            add_log(f"Procesando columna numérica: {col}")
            # Limpiar: quitar $, comas, espacios, y convertir a número
            df[col] = df[col].astype(str).str.replace(r'[\$,\s]', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            add_log(f"  {col} suma: {df[col].sum()}")
    
    # Fechas
    date_cols = ['FECHA_INGR', 'FECHA_AUTO']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
            add_log(f"Columna fecha procesada: {col}")
    
    # Extraer AÑO y MES si no existen
    if 'AÑO' not in df.columns or df['AÑO'].isna().all():
        if 'FECHA_INGR' in df.columns:
            df['AÑO'] = df['FECHA_INGR'].dt.year
            df['MES'] = df['FECHA_INGR'].dt.month
            add_log("AÑO y MES extraídos de FECHA_INGR")
    
    # Asegurar que AÑO y MES sean numéricos (mantener NaN en lugar de 0 para fechas inválidas)
    if 'AÑO' in df.columns:
        df['AÑO'] = pd.to_numeric(df['AÑO'], errors='coerce')
    if 'MES' in df.columns:
        df['MES'] = pd.to_numeric(df['MES'], errors='coerce')
    
    # Calcular DIFERENCIA si no existe o es cero
    if 'DIFERENCIA' not in df.columns or df['DIFERENCIA'].sum() == 0:
        if 'M._DE_O._INICIAL' in df.columns and 'M._DE_O._FINAL' in df.columns:
            df['DIFERENCIA'] = df['M._DE_O._FINAL'] - df['M._DE_O._INICIAL']
            add_log("DIFERENCIA calculada de INICIAL/FINAL")
    
    add_log(f"render_kpis: DIFERENCIA existe={('DIFERENCIA' in df.columns)}, suma={df.get('DIFERENCIA', pd.Series([0])).sum()}")
    
    # Crear campo de fecha completo para gráficos
    if 'FECHA_INGR' in df.columns:
        df['FECHA_COMPLETA'] = df['FECHA_INGR']
    else:
        # Construir fecha desde AÑO, MES, DIA
        if all(col in df.columns for col in ['AÑO', 'MES', 'DIA']):
            df['FECHA_COMPLETA'] = pd.to_datetime(
                df[['AÑO', 'MES', 'DIA']].rename(columns={'AÑO': 'year', 'MES': 'month', 'DIA': 'day'}),
                errors='coerce'
            )
    
    # Campos de texto - limpiar
    text_cols = ['PLACA', 'MARCA', 'LINEA', 'COMPAÑIA_DE_SEGUROS', 
                 'SINIESTRO', 'IMPREVISTO', 'ACCION', 'CAUSAL', 'ESTATUS']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()
            df[col] = df[col].replace('NAN', '').replace('NONE', '').replace('NAT', '')
    
    add_log(f"Procesamiento completado. Filas: {len(df)}, Columnas: {len(df.columns)}")
    return df
