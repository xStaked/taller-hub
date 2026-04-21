"""
================================================================================
CONFIGURACIÓN Y CONSTANTES - Taller Hub
================================================================================
Configuración de página, estilos CSS y constantes del sistema.
"""

import streamlit as st

# ============================================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================================

def setup_page_config():
    """Configura la página de Streamlit con los colores corporativos"""
    st.set_page_config(
        page_title="Taller Hub | Dashboard de Ahorros",
        page_icon="🚗",
        layout="wide",
        initial_sidebar_state="expanded"
    )


# ============================================================================
# CSS PERSONALIZADO - Paleta Corporativa (Verde/Agua/Marino)
# ============================================================================

CUSTOM_CSS = """
<style>
    /* Header principal */
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #0066CC 0%, #00A8E8 50%, #00CC66 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    /* Subheader */
    .sub-header {
        font-size: 1.1rem;
        color: #64748B;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Cards de KPI */
    .kpi-container {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border-left: 4px solid;
        transition: transform 0.2s;
    }
    
    .kpi-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    .kpi-ahorro { border-left-color: #0066CC; }
    .kpi-honorarios { border-left-color: #00A8E8; }
    .kpi-utilidad { border-left-color: #00CC66; }
    .kpi-promedio { border-left-color: #0891B2; }
    
    .kpi-value {
        font-size: 1.9rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.25rem;
    }
    
    .kpi-label {
        font-size: 0.85rem;
        color: #64748B;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .kpi-delta {
        font-size: 0.8rem;
        color: #00CC66;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    /* Sidebar styling - FONDO OSCURO PARA MEJOR CONTRASTE */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%) !important;
        border-right: 1px solid #334155;
    }
    
    /* Texto del sidebar en color claro */
    [data-testid="stSidebar"] * {
        color: #F1F5F9 !important;
    }
    
    /* Labels y textos específicos del sidebar */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stCaption {
        color: #F1F5F9 !important;
    }
    
    /* Headers del sidebar */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {
        color: #FFFFFF !important;
    }
    
    /* Inputs del sidebar */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea,
    [data-testid="stSidebar"] select {
        color: #1E293B !important;
        background-color: #FFFFFF !important;
    }
    
    /* Botones */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3);
    }
    
    /* Tablas */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Alertas de validación */
    .validation-error {
        background: #FEE2E2;
        border-left: 4px solid #DC2626;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .validation-warning {
        background: #FEF3C7;
        border-left: 4px solid #F59E0B;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .validation-success {
        background: #D1FAE5;
        border-left: 4px solid #10B981;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    /* Status badges */
    .badge-autorizado {
        background: #D1FAE5;
        color: #065F46;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .badge-rechazado {
        background: #FEE2E2;
        color: #991B1B;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .badge-pendiente {
        background: #FEF3C7;
        color: #92400E;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
</style>
"""


def apply_custom_css():
    """Aplica el CSS personalizado al dashboard"""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ============================================================================
# MAPEO DE COLUMNAS
# ============================================================================

COLUMN_MAPPING = {
    'PLACA': ['PLACA'],
    'MARCA': ['MARCA'],
    'LINEA': ['LINEA'],
    'COMPAÑIA_DE_SEGUROS': ['COMPAÑIA', 'SEGURO', 'ASEGURADORA'],
    'SINIESTRO': ['SINIESTRO'],
    'IMPREVISTO': ['IMPREVISTO'],
    'ACCION': ['ACCION'],
    'CAUSAL': ['CAUSAL'],
    'ESTATUS': ['ESTATUS', 'ESTADO'],
    'OBSERVACION': ['OBSERVACION', 'OBSERVACIÓN', 'OBS'],
    'M._DE_O._INICIAL': ['INICIAL', 'M.O.INICIAL', 'MANO_OBRA_INICIAL', 'VALOR_INICIAL'],
    'M._DE_O._FINAL': ['FINAL', 'M.O.FINAL', 'MANO_OBRA_FINAL', 'VALOR_FINAL'],
    'DIFERENCIA': ['DIFERENCIA', 'AHORRO', 'RECUPERACION', 'RECUPERADO'],
    'FECHA_INGR': ['FECHA_INGR', 'FECHA_INGRESO', 'FECHA', 'INGRESO'],
    'FECHA_AUTO': ['FECHA_AUTO', 'FECHA_AUTORIZACION'],
    'AÑO': ['AÑO', 'ANIO', 'YEAR', 'S'],
    'MES': ['MES', 'MONTH', 'R'],
    'DIA': ['DIA', 'DAY', 'Q']
}


# ============================================================================
# CONSTANTES DE NEGOCIO
# ============================================================================

PORCENTAJE_HONORARIOS = 0.18  # 18% del ahorro
EXCEL_FILENAME = "ENSAYO DISTRIKIA INFORME PARA FEBRERO 2026.xlsx"
SHEET_NAME = "BASE DE DATOS"
