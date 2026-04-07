"""
================================================================================
EXPORTACIÓN - Distrikia Dashboard
================================================================================
Funciones para exportar reportes en diferentes formatos.
RF-004: Exportación de datos
"""

import pandas as pd
import io
from datetime import datetime


def generate_excel_report(df, filtros_aplicados):
    """
    RF-004.1: Generar informe mensual automático en Excel
    Incluye múltiples hojas: Datos, Resumen, Gráficos
    """
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Hoja 1: Datos filtrados
        df_export = df.copy()
        # Formatear monedas para Excel
        for col in ['M._DE_O._INICIAL', 'M._DE_O._FINAL', 'DIFERENCIA']:
            if col in df_export.columns:
                df_export[col] = df_export[col].apply(lambda x: f"${x:,.0f}" if x != 0 else "")
        
        df_export.to_excel(writer, sheet_name='Datos Detallados', index=False)
        
        # Hoja 2: Resumen por mes
        if 'AÑO' in df.columns and 'MES' in df.columns:
            resumen_mes = df.groupby(['AÑO', 'MES']).agg({
                'DIFERENCIA': ['sum', 'mean', 'count'],
                'PLACA': 'nunique'
            }).round(0)
            resumen_mes.columns = ['Ahorro Total', 'Promedio', 'Cantidad Reparaciones', 'Vehículos Únicos']
            resumen_mes.to_excel(writer, sheet_name='Resumen Mensual')
        
        # Hoja 3: Resumen por compañía
        if 'COMPAÑIA_DE_SEGUROS' in df.columns:
            resumen_cia = df.groupby('COMPAÑIA_DE_SEGUROS').agg({
                'DIFERENCIA': ['sum', 'count'],
                'PLACA': 'nunique'
            }).round(0)
            resumen_cia.columns = ['Ahorro Total', 'Reparaciones', 'Vehículos']
            resumen_cia.to_excel(writer, sheet_name='Por Compañía')
        
        # Hoja 4: Causales
        if 'CAUSAL' in df.columns:
            resumen_causal = df.groupby('CAUSAL').agg({
                'DIFERENCIA': ['sum', 'count']
            }).round(0)
            resumen_causal.columns = ['Ahorro Total', 'Frecuencia']
            resumen_causal.to_excel(writer, sheet_name='Por Causal')
        
        # Hoja 5: Metadata del reporte
        metadata = pd.DataFrame({
            'Campo': ['Fecha de generación', 'Filtros aplicados', 'Total registros', 
                     'Ahorro total', 'Usuario'],
            'Valor': [
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                str(filtros_aplicados),
                len(df),
                f"${df['DIFERENCIA'].sum():,.0f}" if 'DIFERENCIA' in df.columns else 'N/A',
                'Distrikia Dashboard'
            ]
        })
        metadata.to_excel(writer, sheet_name='Metadata', index=False)
    
    output.seek(0)
    return output


def generate_csv_export(df):
    """RF-004.3, RF-004.4: Exportar datos filtrados"""
    return df.to_csv(index=False).encode('utf-8')
