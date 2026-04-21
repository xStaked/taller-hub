"""
================================================================================
IMPREVISTOS PROCESSOR - Taller Hub
================================================================================
Data processing and analysis for the Tasa de Imprevistos module.

Features:
- Extract imprevistos from existing DataFrame (Google Sheet data)
- Deduplication logic (placa+siniestro)
- Fault classification
- Data aggregation by period
- Statistics calculation
- Merge with manual entries from imprevistos_data.json
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from .imprevistos_config import (
    load_imprevistos_data,
    get_imprevistos_by_periodo,
    get_resumen_mensual,
    es_culpa_taller,
    IMPREVISTO_TIPOS,
    CAUSAS_CULPA_TALLER,
)


# ============================================================================
# DATA EXTRACTION FROM GOOGLE SHEET (DataFrame)
# ============================================================================

def extraer_imprevistos_from_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract imprevistos data from the main DataFrame (Google Sheet).
    
    An imprevisto is identified by:
    - ACCION contains "CAMBIO" OR
    - IMPREVISTO column is not empty
    
    Args:
        df: DataFrame with columns: PLACA, SINIESTRO, IMPREVISTO, ACCION, CAUSAL, etc.
    
    Returns:
        DataFrame with extracted imprevistos
    """
    if df is None or df.empty:
        return pd.DataFrame()
    
    # Check required columns
    required_cols = ['PLACA']
    if not all(col in df.columns for col in required_cols):
        return pd.DataFrame()
    
    # Create a copy to avoid modifying original
    df_work = df.copy()
    
    # Filter rows that have imprevistos:
    # Option 1: ACCION contains "CAMBIO"
    # Option 2: IMPREVISTO column is not empty
    mask_imprevistos = pd.Series(False, index=df_work.index)
    
    if 'ACCION' in df_work.columns:
        mask_imprevistos |= df_work['ACCION'].str.contains('CAMBIO', na=False, case=False)
    
    if 'IMPREVISTO' in df_work.columns:
        mask_imprevistos |= (df_work['IMPREVISTO'].notna()) & (df_work['IMPREVISTO'] != '') & (df_work['IMPREVISTO'] != 'NAN')
    
    df_imprevistos = df_work[mask_imprevistos].copy()
    
    if df_imprevistos.empty:
        return pd.DataFrame()
    
    # Add standardized columns
    df_imprevistos['placa'] = df_imprevistos['PLACA'].str.upper().str.strip()
    df_imprevistos['siniestro'] = df_imprevistos.get('SINIESTRO', pd.Series('', index=df_imprevistos.index)).str.upper().str.strip()
    df_imprevistos['imprevisto_desc'] = df_imprevistos.get('IMPREVISTO', pd.Series('', index=df_imprevistos.index))
    df_imprevistos['accion'] = df_imprevistos.get('ACCION', pd.Series('', index=df_imprevistos.index))
    df_imprevistos['causal'] = df_imprevistos.get('CAUSAL', pd.Series('', index=df_imprevistos.index))
    
    # Classify type based on ACCION
    def classify_tipo(row):
        accion = str(row.get('accion', '')).upper().strip()
        if 'CAMBIO' in accion:
            return 'MANO_OBRA'
        else:
            return 'CAMBIO_REPUESTOS'
    
    df_imprevistos['tipo'] = df_imprevistos.apply(classify_tipo, axis=1)
    
    # Classify fault - using accion + causal combination
    def classify_fault(row):
        tipo = row.get('tipo', '')
        causal = str(row.get('causal', '')).strip()
        accion = str(row.get('accion', '')).strip()
        
        # Handle empty/NaN values
        if not causal or causal == '' or causal.upper() == 'NAN':
            causal = None
        
        # Use the updated classification function
        from .imprevistos_config import es_culpa_taller
        return es_culpa_taller(tipo=tipo, causal=causal, accion=accion)
    
    df_imprevistos['es_culpa_taller'] = df_imprevistos.apply(classify_fault, axis=1)
    
    # Extract date info if available
    if 'AÑO' in df_imprevistos.columns and 'MES' in df_imprevistos.columns:
        df_imprevistos['año'] = pd.to_numeric(df_imprevistos['AÑO'], errors='coerce')
        df_imprevistos['mes'] = pd.to_numeric(df_imprevistos['MES'], errors='coerce')
        df_imprevistos['periodo'] = df_imprevistos['año'].astype(int).astype(str) + '-' + df_imprevistos['mes'].astype(int).astype(str).str.zfill(2)
    
    # Add taller info if available
    if 'TALLER_ORIGEN' in df_imprevistos.columns:
        df_imprevistos['taller_id'] = df_imprevistos['TALLER_ORIGEN']
        df_imprevistos['taller_name'] = df_imprevistos['TALLER_ORIGEN']
    else:
        df_imprevistos['taller_id'] = 'default'
        df_imprevistos['taller_name'] = 'Default'
    
    return df_imprevistos


# ============================================================================
# MERGE DATA SOURCES
# ============================================================================

def merge_imprevistos_data(
    df: pd.DataFrame = None,
    taller_id: Optional[str] = None,
    año: Optional[int] = None,
    mes: Optional[int] = None
) -> pd.DataFrame:
    """
    Merge imprevistos from Google Sheet (DataFrame) and manual entries (JSON).
    
    Priority: Google Sheet data is primary, manual entries are supplementary.
    
    Args:
        df: Main DataFrame from Google Sheet
        taller_id: Filter by workshop
        año: Filter by year
        mes: Filter by month
    
    Returns:
        Merged DataFrame with all imprevistos
    """
    frames = []
    
    # Extract from Google Sheet
    if df is not None and not df.empty:
        df_sheet = extraer_imprevistos_from_dataframe(df)
        
        # Apply filters
        if taller_id and 'taller_id' in df_sheet.columns:
            df_sheet = df_sheet[df_sheet['taller_id'] == taller_id]
        
        if año and 'año' in df_sheet.columns:
            df_sheet = df_sheet[df_sheet['año'] == año]
        
        if mes and 'mes' in df_sheet.columns:
            df_sheet = df_sheet[df_sheet['mes'] == mes]
        
        frames.append(df_sheet)
    
    # Get manual entries from JSON
    entries = get_imprevistos_by_periodo(taller_id=taller_id, año=año, mes=mes)
    
    if entries:
        rows = []
        for entry in entries:
            for imp in entry.get("imprevistos", []):
                rows.append({
                    "taller_id": entry["taller_id"],
                    "taller_name": entry["taller_name"],
                    "periodo": entry["periodo"],
                    "año": entry["año"],
                    "mes": entry["mes"],
                    "placa": imp["placa"],
                    "siniestro": imp.get("siniestro", ""),
                    "tipo": imp["tipo"],
                    "causal": imp.get("causal", ""),
                    "es_culpa_taller": imp.get("es_culpa_taller", False),
                    "source": "manual"
                })
        
        if rows:
            df_manual = pd.DataFrame(rows)
            frames.append(df_manual)
    
    # Merge all sources
    if frames:
        df_merged = pd.concat(frames, ignore_index=True)
        
        # Deduplicate by placa+siniestro across sources
        if 'placa' in df_merged.columns and 'siniestro' in df_merged.columns:
            df_merged = df_merged.drop_duplicates(subset=['placa', 'siniestro'], keep='first')
        
        return df_merged
    
    return pd.DataFrame()


# ============================================================================
# DATA PROCESSING
# ============================================================================

def procesar_datos_imprevistos(
    df: pd.DataFrame = None,
    taller_id: Optional[str] = None,
    año: Optional[int] = None,
    mes: Optional[int] = None
) -> pd.DataFrame:
    """
    Process imprevistos data and return a clean DataFrame.
    Now supports both Google Sheet data and manual entries.
    
    Args:
        df: Main DataFrame from Google Sheet
        taller_id: Filter by workshop
        año: Filter by year
        mes: Filter by month
    
    Returns:
        DataFrame with processed imprevistos data
    """
    # Use merged data source
    df_merged = merge_imprevistos_data(
        df=df,
        taller_id=taller_id,
        año=año,
        mes=mes
    )
    
    if df_merged.empty:
        return df_merged
    
    # Add derived columns if missing
    if "tipo_label" not in df_merged.columns and "tipo" in df_merged.columns:
        df_merged["tipo_label"] = df_merged["tipo"].map(
            lambda x: IMPREVISTO_TIPOS.get(x, {}).get("label", x)
        )
    
    if "culpa_taller_label" not in df_merged.columns and "es_culpa_taller" in df_merged.columns:
        df_merged["culpa_taller_label"] = df_merged["es_culpa_taller"].map(
            lambda x: "Culpa del Taller" if x else "No es Culpa del Taller"
        )
    
    return df_merged


# ============================================================================
# DEDUPLICATION
# ============================================================================

def verificar_duplicados(placa: str, siniestro: str, taller_id: str, periodo: str) -> bool:
    """
    Check if an imprevisto with the same placa+siniestro already exists.
    
    Args:
        placa: Vehicle license plate
        siniestro: Claim number
        taller_id: Workshop ID
        periodo: Period string (YYYY-MM)
    
    Returns:
        bool: True if duplicate exists
    """
    entries = get_imprevistos_by_periodo(taller_id=taller_id)
    
    for entry in entries:
        if entry["periodo"] != periodo:
            continue
        
        for imp in entry.get("imprevistos", []):
            if imp["placa"] == placa.upper() and imp["siniestro"] == siniestro.upper():
                return True
    
    return False


def contar_unicos(df: pd.DataFrame) -> int:
    """
    Count unique imprevistos after deduplication.
    Since deduplication is enforced on entry, this just counts rows.
    
    Args:
        df: DataFrame with imprevistos data
    
    Returns:
        int: Count of unique imprevistos
    """
    if df.empty:
        return 0
    
    # In case we need to deduplicate on-the-fly
    return df.drop_duplicates(subset=["placa", "siniestro"]).shape[0]


# ============================================================================
# STATISTICS
# ============================================================================

def calcular_estadisticas(
    df: pd.DataFrame = None,
    taller_id: Optional[str] = None,
    año: Optional[int] = None
) -> Dict:
    """
    Calculate comprehensive statistics for imprevistos.
    
    Args:
        df: Main DataFrame from Google Sheet
        taller_id: Filter by workshop
        año: Filter by year
    
    Returns:
        Dict with various statistics
    """
    # Get processed data
    df_processed = procesar_datos_imprevistos(df=df, taller_id=taller_id, año=año)
    
    if df_processed.empty:
        return {
            "total_vehiculos": 0,
            "total_imprevistos": 0,
            "tasa_promedio": 0,
            "tasa_max": 0,
            "tasa_min": 0,
            "culpa_taller_total": 0,
            "no_culpa_taller_total": 0,
            "porcentaje_culpa_taller": 0,
            "meses_con_datos": 0
        }
    
    # Calculate statistics from processed data
    total_imprevistos = len(df_processed)
    culpa_taller_total = df_processed["es_culpa_taller"].sum()
    no_culpa_taller_total = (~df_processed["es_culpa_taller"]).sum()
    
    # Get vehicle count per month
    if 'mes' in df_processed.columns:
        monthly_stats = df_processed.groupby(['año', 'mes']).agg(
            imprevistos=('placa', 'count'),
            culpa_taller=('es_culpa_taller', 'sum')
        ).reset_index()
        
        # Calculate rates
        if 'total_vehiculos' in df_processed.columns:
            monthly_stats['total_vehiculos'] = df_processed.groupby(['año', 'mes'])['total_vehiculos'].first().values
        else:
            # Estimate from original df
            monthly_stats['total_vehiculos'] = 0
        
        monthly_stats['tasa'] = (
            (monthly_stats['imprevistos'] / monthly_stats['total_vehiculos'] * 100) 
            if monthly_stats['total_vehiculos'].sum() > 0 else 0
        )
        
        tasa_promedio = monthly_stats['tasa'].mean()
        tasa_max = monthly_stats['tasa'].max()
        tasa_min = monthly_stats['tasa'].min()
        meses_con_datos = len(monthly_stats)
        total_vehiculos = monthly_stats['total_vehiculos'].sum()
    else:
        tasa_promedio = 0
        tasa_max = 0
        tasa_min = 0
        meses_con_datos = 0
        total_vehiculos = 0
    
    return {
        "total_vehiculos": total_vehiculos,
        "total_imprevistos": total_imprevistos,
        "tasa_promedio": tasa_promedio,
        "tasa_max": tasa_max,
        "tasa_min": tasa_min,
        "culpa_taller_total": int(culpa_taller_total),
        "no_culpa_taller_total": int(no_culpa_taller_total),
        "porcentaje_culpa_taller": (
            (culpa_taller_total / total_imprevistos * 100) if total_imprevistos > 0 else 0
        ),
        "meses_con_datos": meses_con_datos
    }


def calcular_estadisticas_por_tipo(
    df: pd.DataFrame = None,
    taller_id: Optional[str] = None,
    año: Optional[int] = None
) -> pd.DataFrame:
    """
    Calculate statistics by imprevisto type.
    
    Returns:
        DataFrame with statistics by type
    """
    df_processed = procesar_datos_imprevistos(df=df, taller_id=taller_id, año=año)
    
    if df_processed.empty or 'tipo' not in df_processed.columns:
        return pd.DataFrame()
    
    # Group by type
    stats = df_processed.groupby("tipo").agg({
        "placa": "count",
        "es_culpa_taller": ["sum", lambda x: (~x).sum()]
    }).reset_index()
    
    stats.columns = ["tipo", "cantidad", "culpa_taller", "no_culpa_taller"]
    
    # Add labels
    stats["tipo_label"] = stats["tipo"].map(
        lambda x: IMPREVISTO_TIPOS.get(x, {}).get("label", x)
    )
    
    # Calculate percentages
    total = stats["cantidad"].sum()
    stats["porcentaje"] = (stats["cantidad"] / total * 100) if total > 0 else 0
    
    return stats


def calcular_estadisticas_por_causal(
    df: pd.DataFrame = None,
    taller_id: Optional[str] = None,
    año: Optional[int] = None
) -> pd.DataFrame:
    """
    Calculate statistics by cause (for MANO_OBRA type).
    
    Returns:
        DataFrame with statistics by cause
    """
    df_processed = procesar_datos_imprevistos(df=df, taller_id=taller_id, año=año)
    
    if df_processed.empty:
        return pd.DataFrame()
    
    # Filter MANO_OBRA type or those with causal info
    df_mano = df_processed[
        (df_processed["tipo"] == "MANO_OBRA") | 
        (df_processed["causal"].notna() & (df_processed["causal"] != ""))
    ].copy()
    
    if df_mano.empty:
        return pd.DataFrame()
    
    # Group by cause
    stats = df_mano.groupby("causal").agg({
        "placa": "count",
        "es_culpa_taller": ["sum", lambda x: (~x).sum()]
    }).reset_index()
    
    stats.columns = ["causal", "cantidad", "culpa_taller", "no_culpa_taller"]
    
    # Calculate percentages
    total = stats["cantidad"].sum()
    stats["porcentaje"] = (stats["cantidad"] / total * 100) if total > 0 else 0
    
    # Sort by quantity
    stats = stats.sort_values("cantidad", ascending=False)
    
    return stats


# ============================================================================
# DATA EXPORT HELPERS
# ============================================================================

def preparar_datos_export(
    taller_id: Optional[str] = None,
    año: Optional[int] = None
) -> pd.DataFrame:
    """
    Prepare data for export to Excel.
    
    Returns:
        DataFrame ready for export
    """
    resumen = get_resumen_mensual(taller_id=taller_id, año=año)
    
    if not resumen:
        return pd.DataFrame()
    
    df = pd.DataFrame(resumen)
    
    # Add month name
    df["mes_nombre"] = df["mes"].map(
        lambda x: datetime(2000, int(x), 1).strftime('%B %Y')
    )
    
    # Reorder and rename
    df_export = df[[
        "mes_nombre", "total_vehiculos", "total_imprevistos",
        "culpa_taller", "no_culpa_taller",
        "tasa", "tasa_culpa_taller", "tasa_no_culpa_taller"
    ]].rename(columns={
        "mes_nombre": "Período",
        "total_vehiculos": "Cantidad Vehículos",
        "total_imprevistos": "Cantidad Imprevistos",
        "culpa_taller": "Culpa del Taller",
        "no_culpa_taller": "No Culpa del Taller",
        "tasa": "Tasa Total (%)",
        "tasa_culpa_taller": "Tasa Culpa Taller (%)",
        "tasa_no_culpa_taller": "Tasa No Culpa Taller (%)"
    })
    
    return df_export


# ============================================================================
# VALIDATION
# ============================================================================

def validar_datos_imprevistos(
    taller_id: str,
    periodo: str,
    total_vehiculos: int,
    imprevistos: List[Dict]
) -> List[str]:
    """
    Validate imprevistos data before saving.
    
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    if not taller_id:
        errors.append("Debes seleccionar un taller")
    
    if not periodo:
        errors.append("Debes especificar un período")
    
    if total_vehiculos < 0:
        errors.append("El total de vehículos no puede ser negativo")
    
    for i, imp in enumerate(imprevistos):
        if not imp.get("placa"):
            errors.append(f"Imprevisto {i+1}: Falta la placa")
        
        if not imp.get("siniestro"):
            errors.append(f"Imprevisto {i+1}: Falta el número de siniestro")
        
        if not imp.get("tipo"):
            errors.append(f"Imprevisto {i+1}: Falta el tipo de imprevisto")
        
        if imp.get("tipo") == "MANO_OBRA" and not imp.get("causal"):
            errors.append(f"Imprevisto {i+1}: Falta la causal para tipo MANO_OBRA")
    
    return errors
