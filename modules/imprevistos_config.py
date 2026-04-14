"""
================================================================================
IMPREVISTOS CONFIGURATION - Distrikia Dashboard
================================================================================
Configuration for the Tasa de Imprevistos (Unforeseen Events Rate) module.

Defines:
- Imprevisto types (con cambio de repuestos, de mano de obra)
- Causes list for mano de obra actions
- Talleres fault classification rules
- Data persistence for imprevistos entries
"""

import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# ============================================================================
# IMPREVISTOS DATA FILE
# ============================================================================

IMPREVISTOS_DATA_FILE = Path(__file__).parent.parent / "data" / "imprevistos_data.json"

# ============================================================================
# IMPREVISTO TYPES
# ============================================================================

IMPREVISTO_TIPOS = {
    "CAMBIO_REPUESTOS": {
        "label": "Con cambio de repuestos (frena el carro)",
        "description": "Imprevisto que requiere cambio de piezas y detiene el vehículo",
        "es_culpa_taller": False,  # Default: not workshop's fault
    },
    "MANO_OBRA": {
        "label": "De mano de obra (acción = cambio)",
        "description": "Imprevisto relacionado con acción de cambio en mano de obra",
        "es_culpa_taller": None,  # Depends on causal
    }
}

# ============================================================================
# CAUSAS DE MANO DE OBRA (Lista completa de datos reales)
# ============================================================================

CAUSAS_MANO_OBRA = [
    "Ajuste mano de obra",
    "No cotizado",
    "Eliminación cia.",
    "Digitación",
    "No visible",
    "Pretensión asegurado",
    "Predesarme",
    "No es reparable",
    "Recuperación de pieza",
    "Sin fotos claras",
    "TOT",
    "Daño en proceso",
    "Normal del proceso",
    "Sin diagnóstico",
    "No es del siniestro",
    "Otro",
]

# Classification: which causes are workshop's fault
# Regla: Si ACCION = "CAMBIO" y CAUSAL está en esta lista, aplicar clasificación
CAUSAS_CULPA_TALLER = {
    # ❌ CULPA DEL TALLER (solo si ACCION = CAMBIO)
    "Digitación": True,
    "No cotizado": True,
    "Predesarme": True,
    "Sin fotos claras": True,
    "Sin diagnóstico": True,
    "No es reparable": True,
    "Daño en proceso": True,
    
    # ✅ NO ES CULPA DEL TALLER
    "No visible": False,
    "Normal del proceso": False,
    "Recuperación de pieza": False,
    "Pretensión asegurado": False,
    "Eliminación cia.": False,
    "TOT": False,
    "No es del siniestro": False,  # No es culpa del taller si no es CAMBIO
    "Ajuste mano de obra": False,  # Si la acción es CAMBIO, esto sí es culpa del taller
    "Otro": None,
}


def es_culpa_taller(tipo: str, causal: str = None, accion: str = None) -> bool:
    """
    Determine if an imprevisto is the workshop's fault.
    
    Rules:
    1. If ACCION = "CAMBIO":
       - And CAUSAL = "No visible" → NOT workshop's fault
       - Otherwise → IS workshop's fault (because they should have quoted it properly)
    2. If ACCION != "CAMBIO" (other actions like AJUSTE, BITEC, etc.):
       - Check the causal classification table
    
    Args:
        tipo: Imprevisto type (CAMBIO_REPUESTOS or MANO_OBRA)
        causal: Cause of the imprevisto
        accion: Original action value from the data
    
    Returns:
        bool: True if it's workshop's fault, False otherwise
    """
    # If action is CAMBIO, special rule applies
    if accion and 'CAMBIO' in str(accion).upper():
        if causal is None or causal == '' or str(causal).upper() == 'NAN':
            return True  # CAMBIO without causal = workshop's fault (should have quoted)
        
        causal_upper = str(causal).upper().strip()
        
        # Only "No visible" is NOT workshop's fault when action is CAMBIO
        if causal_upper == 'NO VISIBLE':
            return False
        
        # All other causes with CAMBIO action = workshop's fault
        return True
    
    # For non-CAMBIO actions, use the causal classification table
    if causal is None or causal == '' or str(causal).upper() == 'NAN':
        return False
    
    # Case-insensitive comparison
    causal_upper = str(causal).upper().strip()
    
    for cause, is_fault in CAUSAS_CULPA_TALLER.items():
        if causal_upper == cause.upper():
            return is_fault if is_fault is not None else False
    
    return False


# ============================================================================
# DATA PERSISTENCE
# ============================================================================

def load_imprevistos_data() -> Dict:
    """
    Load imprevistos data from JSON file.
    
    Returns:
        Dict with structure:
        {
            "entries": [
                {
                    "taller_id": "taller_1",
                    "taller_name": "Taller Principal",
                    "periodo": "2024-01",
                    "año": 2024,
                    "mes": 1,
                    "total_vehiculos": 100,
                    "imprevistos": [
                        {
                            "placa": "ABC123",
                            "siniestro": "S001",
                            "tipo": "MANO_OBRA",
                            "causal": "Digitación",
                            "fecha": "2024-01-15",
                            "es_culpa_taller": True
                        }
                    ]
                }
            ]
        }
    """
    if IMPREVISTOS_DATA_FILE.exists():
        try:
            with open(IMPREVISTOS_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading imprevistos data: {e}")
            return {"entries": []}
    return {"entries": []}


def save_imprevistos_data(data: Dict) -> bool:
    """
    Save imprevistos data to JSON file.
    
    Args:
        data: Dictionary with imprevistos entries
    
    Returns:
        bool: True if saved successfully
    """
    try:
        IMPREVISTOS_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(IMPREVISTOS_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving imprevistos data: {e}")
        return False


def add_imprevisto_entry(
    taller_id: str,
    taller_name: str,
    periodo: str,
    año: int,
    mes: int,
    total_vehiculos: int,
    placa: str,
    siniestro: str,
    tipo: str,
    causal: str = None
) -> bool:
    """
    Add a new imprevisto entry with deduplication.
    
    Rule: If placa+siniestro already exists, don't duplicate (count only 1)
    
    Args:
        taller_id: Workshop ID
        taller_name: Workshop name
        periodo: Period string (YYYY-MM)
        año: Year
        mes: Month
        total_vehiculos: Total vehicles delivered
        placa: Vehicle license plate
        siniestro: Claim/siniestro number
        tipo: Imprevisto type
        causal: Cause (for MANO_OBRA type)
    
    Returns:
        bool: True if added, False if duplicate
    """
    data = load_imprevistos_data()
    
    # Find or create entry for this period/taller
    entry = None
    for e in data["entries"]:
        if e["taller_id"] == taller_id and e["periodo"] == periodo:
            entry = e
            break
    
    if entry is None:
        # Create new entry
        entry = {
            "taller_id": taller_id,
            "taller_name": taller_name,
            "periodo": periodo,
            "año": año,
            "mes": mes,
            "total_vehiculos": total_vehiculos,
            "imprevistos": []
        }
        data["entries"].append(entry)
    
    # Update total vehicles (use max or sum)
    entry["total_vehiculos"] = max(entry["total_vehiculos"], total_vehiculos)
    
    # Check for duplicate (placa + siniestro)
    for imp in entry["imprevistos"]:
        if imp["placa"] == placa.upper() and imp["siniestro"] == siniestro.upper():
            # Duplicate found - don't add
            return False
    
    # Add new imprevisto
    nuevo_imprevisto = {
        "placa": placa.upper(),
        "siniestro": siniestro.upper(),
        "tipo": tipo,
        "causal": causal,
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "es_culpa_taller": es_culpa_taller(tipo, causal)
    }
    
    entry["imprevistos"].append(nuevo_imprevisto)
    
    return save_imprevistos_data(data)


def get_imprevistos_by_periodo(taller_id: str = None, año: int = None, mes: int = None) -> List[Dict]:
    """
    Get imprevistos data filtered by criteria.
    
    Args:
        taller_id: Filter by workshop ID (optional)
        año: Filter by year (optional)
        mes: Filter by month (optional)
    
    Returns:
        List of filtered entries
    """
    data = load_imprevistos_data()
    entries = data["entries"]
    
    # Apply filters
    if taller_id:
        entries = [e for e in entries if e["taller_id"] == taller_id]
    
    if año:
        entries = [e for e in entries if e["año"] == año]
    
    if mes:
        entries = [e for e in entries if e["mes"] == mes]
    
    return entries


def get_resumen_mensual(taller_id: str = None, año: int = None) -> List[Dict]:
    """
    Get monthly summary table: mes | cantidad vehículos | cantidad imprevistos | tasa (%)
    
    Returns:
        List of dicts with monthly summary
    """
    entries = get_imprevistos_by_periodo(taller_id=taller_id, año=año)
    
    # Group by month
    monthly_data = {}
    for entry in entries:
        mes_key = entry["mes"]
        
        if mes_key not in monthly_data:
            monthly_data[mes_key] = {
                "mes": mes_key,
                "año": entry["año"],
                "total_vehiculos": 0,
                "total_imprevistos": 0,
                "culpa_taller": 0,
                "no_culpa_taller": 0
            }
        
        # Sum vehicles (avoid double counting)
        monthly_data[mes_key]["total_vehiculos"] = max(
            monthly_data[mes_key]["total_vehiculos"],
            entry["total_vehiculos"]
        )
        
        # Count imprevistos
        monthly_data[mes_key]["total_imprevistos"] += len(entry["imprevistos"])
        
        # Count by fault classification
        for imp in entry["imprevistos"]:
            if imp.get("es_culpa_taller"):
                monthly_data[mes_key]["culpa_taller"] += 1
            else:
                monthly_data[mes_key]["no_culpa_taller"] += 1
    
    # Calculate rates
    resumen = []
    for mes_key in sorted(monthly_data.keys()):
        item = monthly_data[mes_key]
        total_veh = item["total_vehiculos"]
        total_imp = item["total_imprevistos"]
        
        item["tasa"] = (total_imp / total_veh * 100) if total_veh > 0 else 0
        item["tasa_culpa_taller"] = (item["culpa_taller"] / total_veh * 100) if total_veh > 0 else 0
        item["tasa_no_culpa_taller"] = (item["no_culpa_taller"] / total_veh * 100) if total_veh > 0 else 0
        
        resumen.append(item)
    
    return resumen
