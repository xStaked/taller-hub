"""
================================================================================
CONFIGURACIÓN DE TALLERES - Distrikia Dashboard
================================================================================
Configuración de múltiples talleres para arquitectura multitaller.
RF-MT: Soporte multi-taller
"""

import streamlit as st
from typing import Dict, List, Optional

# ============================================================================
# CONFIGURACIÓN DE TALLERES
# ============================================================================

TALLERES_CONFIG = {
    "taller_1": {
        "id": "taller_1",
        "nombre": "Taller Principal",
        "sheet_url": "https://docs.google.com/spreadsheets/d/13sR-FFPIasaY0xlkpmcZnyLJfCVKGUNNoK4RFO6R6pY/edit",
        "activo": True,
        "color": "#0066CC",  # Azul corporativo
        "descripcion": "Taller principal de operaciones",
    },
    # Template para agregar más talleres:
    # "taller_2": {
    #     "id": "taller_2",
    #     "nombre": "Taller Norte",
    #     "sheet_url": "https://docs.google.com/spreadsheets/d/TU_ID_AQUI/edit",
    #     "activo": False,  # Cambiar a True cuando esté listo
    #     "color": "#00A8E8",
    #     "descripcion": "Sucursal Norte",
    # },
    # "taller_3": {
    #     "id": "taller_3",
    #     "nombre": "Taller Sur",
    #     "sheet_url": "https://docs.google.com/spreadsheets/d/TU_ID_AQUI/edit",
    #     "activo": False,
    #     "color": "#00CC66",
    #     "descripcion": "Sucursal Sur",
    # },
    # "taller_4": {
    #     "id": "taller_4",
    #     "nombre": "Taller Oriente",
    #     "sheet_url": "https://docs.google.com/spreadsheets/d/TU_ID_AQUI/edit",
    #     "activo": False,
    #     "color": "#F59E0B",
    #     "descripcion": "Sucursal Oriente",
    # },
}

# Paleta de colores para talleres adicionales (si se agregan más)
COLORES_TALLERES = [
    "#0066CC",  # Azul
    "#00A8E8",  # Cyan
    "#00CC66",  # Verde
    "#F59E0B",  # Amarillo
    "#DC2626",  # Rojo
    "#8B5CF6",  # Púrpura
    "#EC4899",  # Rosa
    "#14B8A6",  # Teal
]


def get_talleres_activos() -> Dict[str, dict]:
    """Retorna solo los talleres marcados como activos"""
    return {k: v for k, v in TALLERES_CONFIG.items() if v.get("activo", False)}


def get_talleres_disponibles() -> Dict[str, dict]:
    """Retorna todos los talleres configurados"""
    return TALLERES_CONFIG.copy()


def get_taller_config(taller_id: str) -> Optional[dict]:
    """Retorna la configuración de un taller específico"""
    return TALLERES_CONFIG.get(taller_id)


def get_url_taller(taller_id: str) -> Optional[str]:
    """Retorna la URL del sheet de un taller"""
    config = get_taller_config(taller_id)
    return config["sheet_url"] if config else None


def get_nombre_taller(taller_id: str) -> str:
    """Retorna el nombre legible de un taller"""
    config = get_taller_config(taller_id)
    return config["nombre"] if config else taller_id


def get_color_taller(taller_id: str) -> str:
    """Retorna el color asignado a un taller"""
    config = get_taller_config(taller_id)
    if config and "color" in config:
        return config["color"]
    # Asignar color basado en índice si no tiene definido
    talleres = list(TALLERES_CONFIG.keys())
    idx = talleres.index(taller_id) if taller_id in talleres else 0
    return COLORES_TALLERES[idx % len(COLORES_TALLERES)]


def agregar_taller(
    taller_id: str,
    nombre: str,
    sheet_url: str,
    activo: bool = True,
    descripcion: str = "",
) -> bool:
    """
    Agrega un nuevo taller a la configuración.
    Nota: Esto es en runtime, para persistir modificar TALLERES_CONFIG.
    """
    if taller_id in TALLERES_CONFIG:
        return False
    
    idx = len(TALLERES_CONFIG)
    TALLERES_CONFIG[taller_id] = {
        "id": taller_id,
        "nombre": nombre,
        "sheet_url": sheet_url,
        "activo": activo,
        "color": COLORES_TALLERES[idx % len(COLORES_TALLERES)],
        "descripcion": descripcion,
    }
    return True


def toggle_taller_activo(taller_id: str, activo: bool):
    """Activa o desactiva un taller"""
    if taller_id in TALLERES_CONFIG:
        TALLERES_CONFIG[taller_id]["activo"] = activo


# ============================================================================
# FUNCIONES DE UI PARA TALLERES
# ============================================================================

def render_selector_talleres_sidebar() -> List[str]:
    """
    Renderiza el selector de talleres en el sidebar.
    Retorna la lista de IDs de talleres seleccionados.
    """
    st.sidebar.header("🏪 Selección de Talleres")
    
    talleres = get_talleres_disponibles()
    
    if not talleres:
        st.sidebar.warning("⚠️ No hay talleres configurados")
        return []
    
    # Checkbox para ver todos
    ver_todos = st.sidebar.checkbox("📊 Ver todos los talleres", value=True)
    
    seleccionados = []
    
    if ver_todos:
        # Seleccionar todos los activos por defecto
        seleccionados = [tid for tid, tconfig in talleres.items() if tconfig.get("activo", False)]
        st.sidebar.info(f"✅ {len(seleccionados)} taller(es) seleccionado(s)")
    else:
        # Mostrar checkboxes individuales
        st.sidebar.markdown("**Selecciona los talleres:**")
        for taller_id, config in talleres.items():
            if not config.get("activo", False):
                continue
            
            col1, col2 = st.sidebar.columns([0.1, 0.9])
            with col1:
                color = config.get("color", "#0066CC")
                st.markdown(f"<div style='width:12px;height:12px;background:{color};border-radius:50%;margin-top:8px;'></div>", unsafe_allow_html=True)
            with col2:
                if st.checkbox(config["nombre"], value=True, key=f"chk_{taller_id}"):
                    seleccionados.append(taller_id)
    
    # Mostrar resumen
    if seleccionados:
        st.sidebar.caption(f"**Talleres activos:** {len(seleccionados)}")
        for tid in seleccionados:
            nombre = get_nombre_taller(tid)
            st.sidebar.caption(f"  • {nombre}")
    else:
        st.sidebar.warning("⚠️ Selecciona al menos un taller")
    
    st.sidebar.divider()
    
    return seleccionados


def render_gestion_talleres():
    """
    Renderiza panel de gestión de talleres (para modo admin).
    Permite ver y editar configuración de talleres.
    """
    st.subheader("🔧 Gestión de Talleres")
    
    talleres = get_talleres_disponibles()
    
    # Tabla de talleres
    data = []
    for tid, config in talleres.items():
        data.append({
            "ID": tid,
            "Nombre": config["nombre"],
            "URL": config["sheet_url"][:50] + "..." if len(config["sheet_url"]) > 50 else config["sheet_url"],
            "Activo": "✅" if config.get("activo", False) else "❌",
            "Color": config.get("color", "#0066CC"),
        })
    
    if data:
        import pandas as pd
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
    else:
        st.info("No hay talleres configurados. Agrega uno nuevo.")
    
    # Instrucciones para agregar más
    with st.expander("➕ ¿Cómo agregar más talleres?"):
        st.markdown("""
        Para agregar más talleres, edita el archivo `modules/taller_config.py`:
        
        1. Copia el template de `taller_2` dentro de `TALLERES_CONFIG`
        2. Cambia el ID (ej: `taller_5`)
        3. Actualiza el nombre y la URL del Google Sheet
        4. Cambia `"activo": True` para habilitarlo
        5. Reinicia la aplicación
        
        **Nota:** Cada taller debe tener su propio Google Sheet con la misma estructura de columnas.
        """)


# ============================================================================
# FUNCIONES DE PROCESAMIENTO MULTITALLER
# ============================================================================

def consolidar_dataframes(dfs_por_taller: dict) -> Optional:
    """
    Consolida múltiples DataFrames de diferentes talleres en uno solo.
    Agrega la columna TALLER_ORIGEN a cada DataFrame.
    
    Args:
        dfs_por_taller: Dict {taller_id: DataFrame}
    
    Returns:
        DataFrame consolidado o None si no hay datos
    """
    import pandas as pd
    
    if not dfs_por_taller:
        return None
    
    dfs_procesados = []
    
    for taller_id, df in dfs_por_taller.items():
        if df is None or df.empty:
            continue
        
        df_copy = df.copy()
        config = get_taller_config(taller_id)
        
        # Agregar columna de taller
        df_copy["TALLER_ORIGEN"] = config["nombre"] if config else taller_id
        df_copy["TALLER_ID"] = taller_id
        df_copy["TALLER_COLOR"] = get_color_taller(taller_id)
        
        dfs_procesados.append(df_copy)
    
    if not dfs_procesados:
        return None
    
    # Consolidar todos los DataFrames
    df_consolidado = pd.concat(dfs_procesados, ignore_index=True)
    
    return df_consolidado


def get_resumen_por_taller(df_consolidado) -> Optional:
    """
    Genera un resumen de métricas por taller.
    
    Returns:
        DataFrame con resumen por taller
    """
    import pandas as pd
    
    if df_consolidado is None or df_consolidado.empty:
        return None
    
    if "TALLER_ORIGEN" not in df_consolidado.columns:
        return None
    
    resumen = df_consolidado.groupby("TALLER_ORIGEN").agg({
        "DIFERENCIA": ["sum", "mean", "count"],
        "PLACA": "nunique",
    }).reset_index()
    
    # Aplanar columnas multi-index
    resumen.columns = ["TALLER", "AHORRO_TOTAL", "AHORRO_PROMEDIO", "TOTAL_REPARACIONES", "VEHICULOS_UNICOS"]
    
    # Calcular honorarios (18%)
    resumen["HONORARIOS"] = resumen["AHORRO_TOTAL"] * 0.18
    resumen["UTILIDAD"] = resumen["AHORRO_TOTAL"] - resumen["HONORARIOS"]
    
    return resumen
