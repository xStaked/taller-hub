"""
================================================================================
CHART CONFIGURATION - Distrikia Dashboard
================================================================================
Manages chart type preferences (Bar/Line) for presentations.

Supports:
- Global chart type setting
- Per-chart overrides
- Session state persistence
"""

import streamlit as st
from typing import Dict, Optional

# ============================================================================
# CHART TYPE CONSTANTS
# ============================================================================

CHART_TYPE_BAR = "bar"
CHART_TYPE_LINE = "line"

CHART_TYPES = {
    CHART_TYPE_BAR: {"label": "📊 Barras", "icon": "📊"},
    CHART_TYPE_LINE: {"label": "📈 Líneas", "icon": "📈"}
}

# Charts available for type switching
CHART_IDS = {
    "ahorro_mes": "Ahorro por Mes",
    "causales": "Causales de Cambio",
    "tasa_imprevistos": "Tasa de Imprevistos",
    "cambio_repuestos": "Cambio de Repuestos"
}

DEFAULT_CHART_CONFIG = {
    "global_type": CHART_TYPE_LINE,  # Default to line for presentations
    "per_chart": {}  # Per-chart overrides
}


# ============================================================================
# CHART CONFIGURATION MANAGEMENT
# ============================================================================

def get_chart_config() -> Dict:
    """
    Get chart configuration from session state.
    Initializes with defaults if not present.
    """
    if 'chart_config' not in st.session_state:
        st.session_state['chart_config'] = DEFAULT_CHART_CONFIG.copy()
    
    return st.session_state['chart_config']


def save_chart_config(config: Dict):
    """
    Save chart configuration to session state.
    """
    st.session_state['chart_config'] = config


def get_chart_type(chart_id: str) -> str:
    """
    Get the chart type for a specific chart.
    Checks per-chart override first, then falls back to global setting.
    
    Args:
        chart_id: Chart identifier (e.g., 'ahorro_mes', 'causales')
    
    Returns:
        Chart type string ('bar' or 'line')
    """
    config = get_chart_config()
    
    # Check per-chart override
    if chart_id in config.get('per_chart', {}):
        return config['per_chart'][chart_id]
    
    # Fall back to global
    return config.get('global_type', CHART_TYPE_LINE)


def set_global_chart_type(chart_type: str):
    """
    Set the global chart type for all charts.
    
    Args:
        chart_type: 'bar' or 'line'
    """
    config = get_chart_config()
    config['global_type'] = chart_type
    
    # Clear per-chart overrides when setting global
    config['per_chart'] = {}
    
    save_chart_config(config)


def set_per_chart_type(chart_id: str, chart_type: str):
    """
    Set chart type for a specific chart (overrides global).
    
    Args:
        chart_id: Chart identifier
        chart_type: 'bar' or 'line'
    """
    config = get_chart_config()
    
    if 'per_chart' not in config:
        config['per_chart'] = {}
    
    config['per_chart'][chart_id] = chart_type
    save_chart_config(config)


# ============================================================================
# CHART CONFIGURATION UI
# ============================================================================

def render_chart_type_selector():
    """
    Render chart type selector UI in sidebar.
    Allows setting global type or per-chart overrides.
    """
    config = get_chart_config()
    
    st.divider()
    st.markdown("**📊 Tipo de Gráfico**")
    
    # Mode selector: Global or Per-Chart
    mode = st.radio(
        "Modo:",
        options=["global", "individual"],
        format_func=lambda x: "🌐 Global" if x == "global" else "🎨 Por Gráfico",
        index=0 if not config.get('per_chart') else 1,
        label_visibility="collapsed",
        key="chart_mode_selector"
    )
    
    if mode == "global":
        # Clear per-chart overrides
        if config.get('per_chart'):
            config['per_chart'] = {}
            save_chart_config(config)
        
        # Global chart type selector
        selected_type = st.segmented_control(
            "Tipo global:",
            options=[CHART_TYPE_BAR, CHART_TYPE_LINE],
            default=config.get('global_type', CHART_TYPE_LINE),
            format_func=lambda x: CHART_TYPES[x]['label'],
            key="global_chart_type"
        )
        
        # Apply if changed
        if selected_type != config.get('global_type'):
            set_global_chart_type(selected_type)
            st.rerun()
            
    else:
        # Per-chart selector
        st.caption("Selecciona tipo para cada gráfico:")
        
        for chart_id, chart_name in CHART_IDS.items():
            col1, col2 = st.columns([0.7, 0.3])
            
            with col1:
                st.markdown(f"<span style='font-size: 0.85rem;'>{chart_name}</span>", unsafe_allow_html=True)
            
            with col2:
                current_type = get_chart_type(chart_id)
                new_type = st.segmented_control(
                    f"chart_type_{chart_id}",
                    options=[CHART_TYPE_BAR, CHART_TYPE_LINE],
                    default=current_type,
                    format_func=lambda x: CHART_TYPES[x]['icon'],
                    label_visibility="collapsed",
                    key=f"per_chart_{chart_id}"
                )
                
                if new_type != current_type:
                    set_per_chart_type(chart_id, new_type)
                    st.rerun()
        
        # Reset button
        if st.button("🔄 Resetear a global", use_container_width=True, type="secondary"):
            config['per_chart'] = {}
            save_chart_config(config)
            st.rerun()


def get_chart_type_for_id(chart_id: str) -> str:
    """
    Helper function to get chart type for use in visualization functions.
    
    Args:
        chart_id: Chart identifier
    
    Returns:
        Chart type string ('bar' or 'line')
    """
    return get_chart_type(chart_id)
