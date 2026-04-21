# 🚗 Taller Hub - Dashboard de Gestión de Ahorros y Análisis de Talleres Automotrices

Dashboard ejecutivo para el análisis y seguimiento de métricas de ahorro en talleres automotrices. Sistema de visualización de datos con integración a Google Sheets, diseñado para stakeholders operativos y gerenciales.

**✨ NUEVO: Soporte Multitaller** - Ahora el dashboard puede consolidar datos de múltiples talleres en una sola vista.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-Private-blue)
![Multitaller](https://img.shields.io/badge/Multitaller-Soportado-success)

---

## 📋 Características Principales

- **📊 KPIs en Tiempo Real**: Visualización de métricas clave de ahorro y rendimiento
- **🏪 Soporte Multitaller**: Consolidación de datos de múltiples talleres
- **📈 Gráficos Interactivos**: Análisis visual con filtros dinámicos
- **🔄 Auto-refresh**: Actualización automática de datos desde Google Sheets
- **📁 Exportación Excel**: Descarga de reportes personalizados
- **🔔 Alertas y Validaciones**: Notificaciones de inconsistencias en datos
- **🎨 Tema Oscuro**: Interfaz moderna con modo dark theme

---

## 🚀 Instalación y Configuración

### Prerrequisitos

- Python 3.9 o superior
- Acceso a Google Sheets API
- Virtual environment (recomendado)

### Paso 1: Clonar y preparar entorno

```bash
cd distrikia-dashboard
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

### Paso 2: Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 3: Configurar credenciales de Google Sheets

#### Opción A: Desarrollo Local
1. Colocar el archivo `credentials.json` en `.streamlit/credentials.json`
2. O usar `.streamlit/secrets.toml` (ya configurado en el proyecto)

#### Opción B: Streamlit Cloud (Producción)
1. Ve a tu app en [share.streamlit.io](https://share.streamlit.io)
2. Click en **"⋮"** → **Settings** → **Secrets**
3. Pega el siguiente formato TOML (reemplaza con tus credenciales reales):

```toml
[gcp_service_account]
type = "service_account"
project_id = "tu-project-id"
private_key_id = "tu-private-key-id"
private_key = """-----BEGIN PRIVATE KEY-----
TU_PRIVATE_KEY_AQUI_CON_SALTOS_DE_LINEA
-----END PRIVATE KEY-----"""
client_email = "tu-service@project.iam.gserviceaccount.com"
client_id = "tu-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
universe_domain = "googleapis.com"
```

4. **Importante**: La clave privada debe ir entre triples comillas `"""` y conservar los saltos de línea
5. Guarda y reinicia la app

### Paso 4: Ejecutar la aplicación

```bash
streamlit run app.py
```

La aplicación estará disponible en `http://localhost:8501`

---

## 🏪 Configuración Multitaller

El sistema ahora soporta múltiples talleres. Cada taller debe tener su propio Google Sheet con la misma estructura de columnas.

### Paso 1: Configurar Talleres

Edita el archivo `modules/taller_config.py`:

```python
TALLERES_CONFIG = {
    "taller_1": {
        "id": "taller_1",
        "nombre": "Taller Principal",
        "sheet_url": "https://docs.google.com/spreadsheets/d/TU_ID_1/edit",
        "activo": True,
        "color": "#0066CC",
        "descripcion": "Taller principal de operaciones",
    },
    "taller_2": {
        "id": "taller_2",
        "nombre": "Taller Norte",
        "sheet_url": "https://docs.google.com/spreadsheets/d/TU_ID_2/edit",
        "activo": True,
        "color": "#00A8E8",
        "descripcion": "Sucursal Norte",
    },
    "taller_3": {
        "id": "taller_3",
        "nombre": "Taller Sur",
        "sheet_url": "https://docs.google.com/spreadsheets/d/TU_ID_3/edit",
        "activo": True,
        "color": "#00CC66",
        "descripcion": "Sucursal Sur",
    },
    "taller_4": {
        "id": "taller_4",
        "nombre": "Taller Oriente",
        "sheet_url": "https://docs.google.com/spreadsheets/d/TU_ID_4/edit",
        "activo": True,
        "color": "#F59E0B",
        "descripcion": "Sucursal Oriente",
    },
}
```

### Paso 2: Estructura de Google Sheets

Cada taller debe tener un Google Sheet con:
- **Misma estructura de columnas** que el taller principal
- **Hoja llamada** `BASE DE DATOS` (o `Hoja1` como fallback)
- **Permisos** compartidos con la cuenta de servicio de Google Cloud

### Paso 3: Usar el Dashboard Multitaller

1. En el **sidebar**, selecciona los talleres que deseas visualizar
2. El dashboard automáticamente:
   - Carga datos de todos los talleres seleccionados
   - Consolida los datos en un solo DataFrame
   - Agrega la columna `TALLER_ORIGEN` para identificar el origen
   - Muestra KPIs comparativos entre talleres

---

## 📁 Estructura del Proyecto

```
taller-hub/
├── app.py                          # Punto de entrada principal (multitaller)
├── requirements.txt                # Dependencias del proyecto
├── modules/                        # Lógica modular del dashboard
│   ├── __init__.py
│   ├── config.py                   # Configuración de página y estilos
│   ├── data_loader.py              # Carga de datos (soporte multitaller)
│   ├── data_processor.py           # Procesamiento y transformación
│   ├── validators.py               # Validaciones y alertas
│   ├── visualizations.py           # Gráficos y KPIs
│   ├── visualizations_multitaller.py  # Visualizaciones comparativas
│   ├── taller_config.py            # Configuración de talleres ⭐ NUEVO
│   ├── sidebar.py                  # Barra lateral y filtros
│   ├── components.py               # Componentes UI reutilizables
│   └── exporters.py                # Exportación a Excel
├── .streamlit/
│   ├── config.toml                 # Configuración de Streamlit
│   ├── credentials.json            # Credenciales Google Sheets (no versionar)
│   └── secrets.toml                # Secretos de la aplicación
└── README.md                       # Este archivo
```

---

## 📊 Funcionalidades del Dashboard

### 1. Panel de KPIs
- Ahorro total acumulado (consolidado o por taller)
- Tasa de cumplimiento de metas
- Promedio de ahorro por taller
- Distribución de causales

### 2. Visualizaciones Multitaller
- **Comparativa de Talleres**: KPIs lado a lado
- **Ranking de Talleres**: Top performers por diferentes métricas
- **Tendencias por Taller**: Evolución temporal comparativa
- **Heatmap**: Ahorro por taller y mes
- **Distribución**: Participación de cada taller en el total

### 3. Visualizaciones Consolidadas
- **Gráfico de Ahorro por Mes**: Evolución temporal del ahorro
- **Gráfico de Causales**: Distribución de causas de imprevistos
- **Tasa de Imprevistos**: Porcentaje de imprevistos vs. operaciones
- **Cambio de Repuestos**: Análisis de frecuencia de reemplazos

### 4. Tabla Detallada
- Vista completa de registros con filtros
- Columna `TALLER_ORIGEN` para identificar el origen
- Ordenamiento y búsqueda
- Paginación de resultados

### 5. Exportación
- Exportación a formato Excel (.xlsx)
- Exportación a CSV
- Filtros aplicables antes de exportar

---

## 🔧 Configuración Avanzada

### Variables de Entorno

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `GOOGLE_SHEET_URL` | URL del Google Sheet (modo legacy) | - |
| `AUTO_REFRESH` | Habilitar auto-refresh | `false` |

### Personalización del Tema

Editar `.streamlit/config.toml`:

```toml
[theme]
base = "dark"
primaryColor = "#0066CC"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
font = "sans serif"
```

---

## 👥 Stakeholders

| Rol | Nombre | Responsabilidad |
|-----|--------|-----------------|
| Analista/Gerente | Alexander Cano | Toma de decisiones estratégicas |
| Operativo | Sergio Romero | Gestión operativa diaria |

---

## 📝 Requisitos Funcionales

| ID | Requisito | Estado |
|----|-----------|--------|
| RF-001 | Conexión a Google Sheets | ✅ Implementado |
| RF-002 | Limpieza de datos | ✅ Implementado |
| RF-003.1 | Visualización de KPIs | ✅ Implementado |
| RF-003.2 | Gráfico de cambio de repuestos | ✅ Implementado |
| RF-003.3 | Gráfico de tasa de imprevistos | ✅ Implementado |
| RF-003.4 | Gráfico de ahorro por mes | ✅ Implementado |
| RF-003.5 | Gráfico de causales | ✅ Implementado |
| RF-003.6 | Tabla detallada | ✅ Implementado |
| RF-003.7 | Recuperación mensual | ✅ Implementado |
| RF-004 | Exportación a Excel | ✅ Implementado |
| RF-005 | Validaciones y alertas | ✅ Implementado |
| **RF-MT** | **Soporte Multitaller** | ✅ **Implementado** |

---

## 🐛 Solución de Problemas

### Error de conexión a Google Sheets
1. Verificar que `credentials.json` esté en `.streamlit/`
2. Confirmar que la API de Google Sheets esté habilitada
3. Revisar permisos de acceso al spreadsheet
4. Verificar que la URL del sheet sea correcta

### Taller no aparece en el selector
1. Verificar que esté marcado como `"activo": True` en `taller_config.py`
2. Confirmar que la URL del sheet sea válida
3. Revisar el panel de debug para ver errores específicos

### Datos no se actualizan
1. Verificar que los talleres seleccionados estén activos
2. Revisar conexión a internet
3. Verificar panel de debug en la UI
4. Limpiar caché con el botón "Limpiar Caché y Recargar"

### Errores de dependencias
```bash
pip install --upgrade -r requirements.txt
```

---

## 📦 Dependencias Principales

| Paquete | Versión | Uso |
|---------|---------|-----|
| streamlit | >=1.28.0 | Framework de UI |
| pandas | >=2.0.0 | Manipulación de datos |
| plotly | >=5.15.0 | Visualizaciones |
| gspread | >=5.10.0 | Integración Google Sheets |
| openpyxl | >=3.1.0 | Exportación Excel |

---

## 🔒 Seguridad

- **No versionar** el archivo `credentials.json`
- El archivo está incluido en `.gitignore`
- Las credenciales deben gestionarse de forma segura
- Cada taller controla su propio Google Sheet

---

## 📄 Licencia

Proyecto privado - Taller Hub © 2026

---

## 📞 Soporte

Para reportar problemas o solicitar funcionalidades, contactar al equipo de desarrollo.

---

<p align="center">
  <strong>Taller Hub v2.0 - Multitaller</strong><br>
  <em>Abril 2026</em>
</p>
