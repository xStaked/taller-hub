# 🚗 Taller Hub - Dashboard de Gestión de Ahorros y Análisis de Talleres Automotrices

Dashboard ejecutivo para el análisis y seguimiento de métricas de ahorro en talleres automotrices. Sistema de visualización de datos con integración a Google Sheets, diseñado para stakeholders operativos y gerenciales.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-Private-blue)

---

## 📋 Características Principales

- **📊 KPIs en Tiempo Real**: Visualización de métricas clave de ahorro y rendimiento
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

1. Colocar el archivo `credentials.json` en `.streamlit/credentials.json`
2. Configurar el `sheet_url` en la barra lateral de la aplicación

### Paso 4: Ejecutar la aplicación

```bash
streamlit run app.py
```

La aplicación estará disponible en `http://localhost:8501`

---

## 📁 Estructura del Proyecto

```
taller-hub/
├── app.py                    # Punto de entrada principal
├── requirements.txt          # Dependencias del proyecto
├── modules/                  # Lógica modular del dashboard
│   ├── config.py            # Configuración de página y estilos
│   ├── data_loader.py       # Carga de datos desde Google Sheets
│   ├── data_processor.py    # Procesamiento y transformación
│   ├── validators.py        # Validaciones y alertas
│   ├── visualizations.py    # Gráficos y KPIs
│   ├── sidebar.py           # Barra lateral y filtros
│   ├── components.py        # Componentes UI reutilizables
│   └── exporters.py         # Exportación a Excel
├── .streamlit/
│   ├── config.toml          # Configuración de Streamlit
│   ├── credentials.json     # Credenciales Google Sheets (no versionar)
│   └── secrets.toml         # Secretos de la aplicación
└── README.md                # Este archivo
```

---

## 📊 Funcionalidades del Dashboard

### 1. Panel de KPIs
- Ahorro total acumulado
- Tasa de cumplimiento de metas
- Promedio de ahorro por taller
- Distribución de causales

### 2. Visualizaciones
- **Gráfico de Ahorro por Mes**: Evolución temporal del ahorro
- **Gráfico de Causales**: Distribución de causas de imprevistos
- **Tasa de Imprevistos**: Porcentaje de imprevistos vs. operaciones
- **Cambio de Repuestos**: Análisis de frecuencia de reemplazos

### 3. Tabla Detallada
- Vista completa de registros con filtros
- Ordenamiento y búsqueda
- Paginación de resultados

### 4. Exportación
- Exportación a formato Excel (.xlsx)
- Filtros aplicables antes de exportar
- Formato profesional con tablas formateadas

---

## 🔧 Configuración Avanzada

### Variables de Entorno

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `GOOGLE_SHEET_URL` | URL del Google Sheet de datos | Configurable en UI |
| `AUTO_REFRESH` | Habilitar auto-refresh | `true` |

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
| RF-003.1 | Visualización de KPIs | ✅ Implementado |
| RF-003.2 | Gráfico de cambio de repuestos | ✅ Implementado |
| RF-003.3 | Gráfico de tasa de imprevistos | ✅ Implementado |
| RF-003.4 | Gráfico de ahorro por mes | ✅ Implementado |
| RF-003.5 | Gráfico de causales | ✅ Implementado |
| RF-003.6 | Tabla detallada | ✅ Implementado |
| RF-003.7 | Recuperación mensual | ✅ Implementado |
| RF-004 | Exportación a Excel | ✅ Implementado |
| RF-005 | Validaciones y alertas | ✅ Implementado |

---

## 🐛 Solución de Problemas

### Error de conexión a Google Sheets
1. Verificar que `credentials.json` esté en `.streamlit/`
2. Confirmar que la API de Google Sheets esté habilitada
3. Revisar permisos de acceso al spreadsheet

### Datos no se actualizan
1. Verificar la URL del sheet en la barra lateral
2. Revisar conexión a internet
3. Verificar panel de debug en la UI

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

---

## 📄 Licencia

Proyecto privado - Taller Hub © 2026

---

## 📞 Soporte

Para reportar problemas o solicitar funcionalidades, contactar al equipo de desarrollo.

---

<p align="center">
  <strong>Taller Hub Dashboard v1.0.0</strong><br>
  <em>Abril 2026</em>
</p>
