"""
================================================================================
VALIDACIONES - Distrikia Dashboard
================================================================================
Funciones de validación de calidad de datos.
RF-005: Validaciones de calidad de datos
"""

import pandas as pd


def run_validations(df):
    """
    RF-005: Validaciones de calidad de datos
    Retorna lista de alertas con severidad
    """
    alerts = []
    
    if df is None or df.empty:
        return [("error", "No hay datos para validar")]
    
    # RF-005.1: Validar que el ahorro no sea negativo sin justificación
    if 'DIFERENCIA' in df.columns:
        negativos = df[df['DIFERENCIA'] < 0]
        if len(negativos) > 0:
            # Verificar si tienen justificación en observaciones
            sin_justificacion = negativos[
                negativos.get('OBSERVACION', '').str.len() < 10
            ]
            if len(sin_justificacion) > 0:
                alerts.append(("warning", 
                    f"RF-005.1: {len(sin_justificacion)} registros con ahorro negativo sin justificación clara"))
    
    # RF-005.3: Control de duplicados por placa/siniestro
    if 'PLACA' in df.columns and 'SINIESTRO' in df.columns:
        duplicados = df.groupby(['PLACA', 'SINIESTRO']).size()
        duplicados = duplicados[duplicados > 1]
        if len(duplicados) > 0:
            alerts.append(("warning", 
                f"RF-005.3: {len(duplicados)} combinaciones placa/siniestro duplicadas"))
    
    # RF-005.4: Validación de fechas (no futuras, no muy antiguas)
    if 'FECHA_INGR' in df.columns:
        hoy = pd.Timestamp.now()
        futuras = df[df['FECHA_INGR'] > hoy + pd.Timedelta(days=1)]
        if len(futuras) > 0:
            alerts.append(("error", 
                f"RF-005.4: {len(futuras)} registros con fecha futura"))
        
        muy_antiguas = df[df['FECHA_INGR'] < hoy - pd.Timedelta(days=365*2)]
        if len(muy_antiguas) > 0:
            alerts.append(("warning", 
                f"RF-005.4: {len(muy_antiguas)} registros con fecha mayor a 2 años"))
    
    # Validar valores nulos críticos
    campos_criticos = ['PLACA', 'COMPAÑIA_DE_SEGUROS', 'DIFERENCIA']
    for campo in campos_criticos:
        if campo in df.columns:
            nulos = df[campo].isna().sum() + (df[campo] == '').sum()
            if nulos > 0:
                alerts.append(("warning", 
                    f"{campo}: {nulos} valores nulos o vacíos"))
    
    if not alerts:
        alerts.append(("success", "✅ Todas las validaciones pasaron correctamente"))
    
    return alerts
