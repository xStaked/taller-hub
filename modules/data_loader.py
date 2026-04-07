"""
================================================================================
CARGA DE DATOS - Distrikia Dashboard
================================================================================
Funciones para cargar datos desde Google Sheets y archivos Excel locales.
RF-001: Conexión a fuentes de datos
"""

import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from pathlib import Path

from .data_processor import procesar_dataframe
from .config import EXCEL_FILENAME, SHEET_NAME


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
# CARGA DESDE EXCEL
# ============================================================================

@st.cache_data(ttl=30)
def load_data_from_excel(excel_path=None):
    """
    Carga datos desde archivo Excel local
    Útil para pruebas o cuando Google Sheets no está disponible
    """
    if excel_path is None:
        excel_path = EXCEL_FILENAME
        
    try:
        if not Path(excel_path).exists():
            return None, f"Archivo no encontrado: {excel_path}"
        
        df = pd.read_excel(excel_path, sheet_name=SHEET_NAME)
        st.sidebar.success(f"✅ Datos cargados desde Excel: {len(df)} filas")
        
        # Aplicar procesamiento de datos
        df = procesar_dataframe(df, fuente="Excel")
        
        return df, None
    except Exception as e:
        return None, f"Error cargando Excel: {str(e)}"


# ============================================================================
# CARGA DESDE GOOGLE SHEETS
# ============================================================================

@st.cache_data(ttl=30)
def load_data_from_sheets(sheet_url):
    """
    RF-001: Carga y limpieza de datos desde Google Sheets
    Incluye validaciones básicas de calidad de datos
    """
    try:
        client = get_google_sheets_client()
        if not client:
            # Fallback a Excel si hay error de autenticación
            st.sidebar.warning("⚠️ No se pudo conectar a Google Sheets, usando Excel local")
            return load_data_from_excel()
        
        # Abrir spreadsheet
        spreadsheet = client.open_by_url(sheet_url)
        
        # DEBUG: Mostrar hojas disponibles
        available_sheets = [ws.title for ws in spreadsheet.worksheets()]
        st.sidebar.info(f"📋 Hojas disponibles: {available_sheets}")
        
        # Cargar hoja BASE DE DATOS
        try:
            worksheet = spreadsheet.worksheet(SHEET_NAME)
        except:
            # Intentar con nombre alternativo
            try:
                worksheet = spreadsheet.worksheet("Hoja1")
            except:
                # Usar la primera hoja disponible
                if available_sheets:
                    worksheet = spreadsheet.worksheet(available_sheets[0])
                    st.sidebar.warning(f"⚠️ Usando hoja: {available_sheets[0]}")
        
        data = worksheet.get_all_records()
        st.sidebar.success(f"✅ Datos cargados desde Google Sheets: {len(data)} filas")
        
        if not data:
            return None, "La hoja no tiene datos (solo encabezados o vacía)"
        
        df = pd.DataFrame(data)
        
        if df.empty:
            return None, "La hoja está vacía"
        
        st.sidebar.success(f"✅ DataFrame creado: {df.shape[0]} filas x {df.shape[1]} columnas")
        
        # Aplicar procesamiento de datos
        df = procesar_dataframe(df, fuente="Google Sheets")
        
        return df, None
        
    except Exception as e:
        return None, f"Error cargando datos: {str(e)}"
