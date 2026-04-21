"""
================================================================================
CARGA DE DATOS - Taller Hub
================================================================================
Funciones para cargar datos desde Google Sheets y archivos Excel locales.
Soporte multitaller - RF-MT: Múltiples fuentes de datos
"""

import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from .data_processor import procesar_dataframe
from .config import EXCEL_FILENAME, SHEET_NAME
from .taller_config import (
    get_taller_config, 
    get_url_taller, 
    consolidar_dataframes,
    get_nombre_taller
)


# ============================================================================
# CONEXIÓN A GOOGLE SHEETS
# ============================================================================

@st.cache_resource(ttl=3600)
def get_google_sheets_client():
    """
    RF-001: Conexión a Google Sheets API
    Soporta tanto desarrollo local (archivo JSON) como producción (secrets)
    """
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly"
    ]
    
    try:
        # Intentar cargar desde secrets de Streamlit Cloud
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
        st.sidebar.success("✅ Conectado via Streamlit Secrets")
    except Exception:
        try:
            # Fallback: archivo local credentials.json
            creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
            st.sidebar.success("✅ Conectado via archivo local")
        except Exception:
            try:
                # Segundo fallback: archivo en .streamlit/credentials.json
                creds = Credentials.from_service_account_file(".streamlit/credentials.json", scopes=scopes)
                st.sidebar.success("✅ Conectado via archivo local (.streamlit)")
            except Exception as e3:
                st.sidebar.error(f"❌ Error de conexión: {e3}")
                return None
    
    return gspread.authorize(creds)


# ============================================================================
# CARGA DESDE EXCEL (Fallback)
# ============================================================================

@st.cache_data(ttl=30)
def load_data_from_excel(excel_path=None, taller_id: str = "default") -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Carga datos desde archivo Excel local
    Útil para pruebas o cuando Google Sheets no está disponible
    
    Args:
        excel_path: Ruta al archivo Excel
        taller_id: ID del taller para taggear los datos
    """
    if excel_path is None:
        excel_path = EXCEL_FILENAME
        
    try:
        if not Path(excel_path).exists():
            return None, f"Archivo no encontrado: {excel_path}"
        
        df = pd.read_excel(excel_path, sheet_name=SHEET_NAME)
        
        # Aplicar procesamiento de datos
        df = procesar_dataframe(df, fuente="Excel")
        
        # Agregar metadatos de taller
        df["TALLER_ORIGEN"] = get_nombre_taller(taller_id) if taller_id != "default" else "Taller Excel"
        df["TALLER_ID"] = taller_id
        
        return df, None
    except Exception as e:
        return None, f"Error cargando Excel: {str(e)}"


# ============================================================================
# CARGA DESDE GOOGLE SHEETS (Single Taller)
# ============================================================================

@st.cache_data(ttl=30)
def load_data_from_sheets_single(sheet_url: str, taller_id: str = "default") -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Carga datos desde un solo Google Sheet.
    Versión base usada por la función multitaller.
    
    Args:
        sheet_url: URL del Google Sheet
        taller_id: ID del taller para identificación
    
    Returns:
        Tuple (DataFrame, error_message)
    """
    try:
        client = get_google_sheets_client()
        if not client:
            # Fallback a Excel si hay error de autenticación
            return load_data_from_excel(taller_id=taller_id)
        
        # Abrir spreadsheet
        spreadsheet = client.open_by_url(sheet_url)
        
        # Cargar hoja BASE DE DATOS
        try:
            worksheet = spreadsheet.worksheet(SHEET_NAME)
        except:
            # Intentar con nombre alternativo
            try:
                worksheet = spreadsheet.worksheet("Hoja1")
            except:
                # Usar la primera hoja disponible
                available_sheets = [ws.title for ws in spreadsheet.worksheets()]
                if available_sheets:
                    worksheet = spreadsheet.worksheet(available_sheets[0])
                else:
                    return None, f"No se encontraron hojas en el spreadsheet"
        
        data = worksheet.get_all_records()
        
        if not data:
            return None, "La hoja no tiene datos (solo encabezados o vacía)"
        
        df = pd.DataFrame(data)
        
        if df.empty:
            return None, "La hoja está vacía"
        
        # Aplicar procesamiento de datos
        df = procesar_dataframe(df, fuente="Google Sheets")
        
        return df, None
        
    except Exception as e:
        return None, f"Error cargando datos: {str(e)}"


# ============================================================================
# CARGA MULTITALLER (Nueva funcionalidad)
# ============================================================================

def load_data_multitaller(
    talleres_ids: List[str],
    progress_bar=None
) -> Tuple[Optional[pd.DataFrame], Dict[str, str]]:
    """
    RF-MT: Carga datos de múltiples talleres y los consolida.
    
    Args:
        talleres_ids: Lista de IDs de talleres a cargar
        progress_bar: Opcional - st.progress() para mostrar avance
    
    Returns:
        Tuple (DataFrame_consolidado, dict_errores)
        - DataFrame_consolidado: DataFrame con todos los datos + columna TALLER_ORIGEN
        - dict_errores: {taller_id: mensaje_error} para los talleres con problemas
    """
    if not talleres_ids:
        return None, {"general": "No se seleccionaron talleres"}
    
    dfs_por_taller = {}
    errores = {}
    total = len(talleres_ids)
    
    for idx, taller_id in enumerate(talleres_ids):
        # Actualizar progreso si se proporcionó barra
        if progress_bar is not None:
            progress = (idx + 1) / total
            progress_bar.progress(progress, text=f"Cargando {get_nombre_taller(taller_id)}...")
        
        # Obtener configuración del taller
        config = get_taller_config(taller_id)
        if not config:
            errores[taller_id] = "Taller no encontrado en configuración"
            continue
        
        if not config.get("activo", False):
            errores[taller_id] = "Taller desactivado"
            continue
        
        sheet_url = config.get("sheet_url")
        if not sheet_url:
            errores[taller_id] = "URL no configurada"
            continue
        
        # Cargar datos del taller
        df, error = load_data_from_sheets_single(sheet_url, taller_id)
        
        if error:
            errores[taller_id] = error
            continue
        
        if df is not None and not df.empty:
            dfs_por_taller[taller_id] = df
        else:
            errores[taller_id] = "No se encontraron datos"
    
    # Consolidar todos los DataFrames
    if dfs_por_taller:
        df_consolidado = consolidar_dataframes(dfs_por_taller)
        
        # Guardar info de debug en session state
        st.session_state["talleres_cargados"] = list(dfs_por_taller.keys())
        st.session_state["talleres_con_error"] = errores
        
        return df_consolidado, errores
    
    return None, errores


# ============================================================================
# CARGA DESDE GOOGLE SHEETS (Compatibilidad hacia atrás)
# ============================================================================

@st.cache_data(ttl=30)
def load_data_from_sheets(sheet_url: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    RF-001: Carga y limpieza de datos desde Google Sheets
    Mantiene compatibilidad con versión anterior (monotaller).
    
    Nota: Para multitaller, usar load_data_multitaller()
    """
    return load_data_from_sheets_single(sheet_url, taller_id="single")


# ============================================================================
# FUNCIONES DE RESUMEN Y ESTADÍSTICAS
# ============================================================================

def get_estadisticas_carga(errores: Dict[str, str], total_talleres: int) -> dict:
    """
    Genera estadísticas del proceso de carga multitaller.
    
    Returns:
        Dict con estadísticas
    """
    exitosos = total_talleres - len(errores)
    
    return {
        "total_talleres": total_talleres,
        "exitosos": exitosos,
        "con_error": len(errores),
        "porcentaje_exito": (exitosos / total_talleres * 100) if total_talleres > 0 else 0,
        "detalle_errores": errores,
    }


def render_resumen_carga(stats: dict):
    """Renderiza un resumen visual del estado de carga"""
    if stats["con_error"] == 0:
        st.sidebar.success(f"✅ Todos los talleres cargados ({stats['exitosos']})")
    else:
        st.sidebar.warning(
            f"⚠️ Carga parcial: {stats['exitosos']} exitosos, "
            f"{stats['con_error']} con errores"
        )
        
        with st.sidebar.expander("Ver detalle de errores"):
            for taller_id, error in stats["detalle_errores"].items():
                st.caption(f"**{get_nombre_taller(taller_id)}:** {error}")
