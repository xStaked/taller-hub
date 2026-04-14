# Módulo de Tasa de Imprevistos - DISTRIKIA Dashboard

## Descripción General

Este módulo permite registrar, analizar y visualizar la tasa de imprevistos en las reparaciones automotrices. Proporciona herramientas para:

- Registrar vehículos entregados por período/taller
- Documentar imprevistos con su tipo y causal
- Calcular tasas de imprevistos mensuales
- Clasificar responsabilidades (culpa del taller vs. no culpa)
- Visualizar tendencias con gráficos combinados de barras+línea

## Estructura del Módulo

### Archivos

1. **`imprevistos_config.py`**
   - Configuración de tipos de imprevisto
   - Lista de causas
   - Reglas de clasificación de responsabilidad
   - Persistencia de datos (JSON)

2. **`imprevistos_data.py`**
   - Formularios de entrada de datos
   - Registro de vehículos por período/taller
   - Registro de imprevistos individuales
   - Tabla resumen mensual

3. **`imprevistos_processor.py`**
   - Lógica de deduplicación (placa+siniestro)
   - Clasificación automática de responsabilidad
   - Cálculo de estadísticas
   - Funciones de agregación y análisis

4. **`imprevistos_visualizations.py`**
   - Gráfico combinado barras+línea
   - Tabla resumen mensual
   - Gráficos de clasificación por responsabilidad
   - Estadísticas por tipo y causal

## Tipos de Imprevistos

### 1. Con Cambio de Repuestos
- **Descripción:** Imprevisto que requiere cambio de piezas y frena el carro
- **Responsabilidad:** NO es culpa del taller
- **Ejemplo:** Daño no visible inicialmente que requiere cambio de piezas

### 2. De Mano de Obra (acción = "cambio")
- **Descripción:** Imprevisto relacionado con la acción de cambio en mano de obra
- **Responsabilidad:** Depende de la causal

#### Causas de Mano de Obra:

**Culpa del Taller:**
- Digitación
- No cotizado
- Predesarme
- Sin fotos claras
- Sin diagnóstico
- Error de diagnóstico
- Daño adicional

**NO es Culpa del Taller:**
- No visible

**Pendiente de Clasificación:**
- Otro (caso por caso)

## Regla de Deduplicación

**Importante:** Si una placa+siniestro tiene más de 1 imprevisto, se cuenta solo 1.

Esto evita inflar artificialmente la tasa de imprevistos cuando un mismo vehículo tiene múltiples registros.

## Fórmula de Cálculo

```
Tasa de Imprevistos (%) = (Cantidad de Imprevistos / Cantidad de Vehículos) × 100
```

### Ejemplo:
- Vehículos entregados en enero: 100
- Imprevistos registrados en enero: 15
- Tasa de enero: (15 / 100) × 100 = **15%**

## Uso del Módulo

### 1. Registro de Datos

**Desde el Sidebar:**
1. Haz clic en "📊 Registrar Imprevistos"
2. Selecciona el taller y período (año/mes)
3. Ingresa el total de vehículos entregados
4. Registra cada imprevisto con:
   - Placa del vehículo
   - Número de siniestro
   - Tipo de imprevisto
   - Causal (si aplica)

**Desde el Dashboard:**
- El gráfico de tasa de imprevistos aparece automáticamente en la sección principal
- Los datos se filtran según los filtros aplicados en el dashboard

### 2. Visualización de Resultados

**Gráfico Combinado (Barras + Línea):**
- **Barras azules:** Cantidad de vehículos
- **Barras naranjas:** Cantidad de imprevistos
- **Línea roja:** Tasa de imprevistos (%)
- **Línea verde (opcional):** Tasa de imprevistos culpa del taller (%)

**Tabla Resumen:**
Muestra por mes:
- Cantidad de vehículos
- Cantidad de imprevistos
- Tasa total (%)
- Desglose por responsabilidad

**Gráficos de Clasificación:**
- Distribución culpa del taller vs. no culpa del taller
- Estadísticas por tipo de imprevisto
- Estadísticas por causal (para mano de obra)

## Almacenamiento de Datos

Los datos se guardan en:
```
data/imprevistos_data.json
```

### Estructura del JSON:

```json
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
          "es_culpa_taller": true
        }
      ]
    }
  ]
}
```

## Integración con el Dashboard

El módulo se integra automáticamente en el dashboard principal:

1. **Gráfico en el dashboard:** Se muestra en la sección "Tasa de Imprevistos"
2. **Filtros:** Respeta los filtros de taller, año y mes aplicados en el dashboard
3. **Acceso rápido:** Botones en el sidebar para registro y resumen

## Ejemplos de Uso

### Ejemplo 1: Registro Básico

```
Taller: Taller Principal
Período: Enero 2024
Vehículos entregados: 150

Imprevistos:
1. Placa: ABC123, Siniestro: S001, Tipo: Cambio Repuestos
2. Placa: DEF456, Siniestro: S002, Tipo: Mano de Obra, Causal: No visible
3. Placa: GHI789, Siniestro: S003, Tipo: Mano de Obra, Causal: Digitación

Resultados:
- Total impervistos: 3
- Tasa: (3 / 150) × 100 = 2%
- Culpa del taller: 1 (Digitación)
- No culpa del taller: 2
```

### Ejemplo 2: Deduplicación

```
Intento registrar:
1. Placa: ABC123, Siniestro: S001 → ✅ Registrado
2. Placa: ABC123, Siniestro: S001 → ⚠️ Duplicado (no se cuenta)

Resultado: Solo se cuenta 1 imprevisto
```

## Configuración Avanzada

### Modificar Causas

Edita el archivo `imprevistos_config.py`:

```python
CAUSAS_MANO_OBRA = [
    "No visible",
    "Digitación",
    # Agrega nuevas causas aquí
]

CAUSAS_CULPA_TALLER = {
    "Digitación": True,
    "No visible": False,
    # Agrega clasificación para nuevas causas
}
```

### Modificar Tipos de Imprevisto

```python
IMPREVISTO_TIPOS = {
    "CAMBIO_REPUESTOS": {
        "label": "Con cambio de repuestos",
        "es_culpa_taller": False,
    },
    # Agrega nuevos tipos aquí
}
```

## Troubleshooting

### Problema: "No hay datos disponibles"
- **Solución:** Asegúrate de haber registrado al menos un imprevisto desde el sidebar o el dashboard

### Problema: "Imprevisto duplicado"
- **Solución:** El sistema automáticamente evita duplicados por placa+siniestro. Si necesitas modificar un registro existente, edita el archivo `data/imprevistos_data.json`

### Problema: "La tasa es 0%"
- **Solución:** Verifica que hayas ingresado el total de vehículos entregados para el período

## Próximas Mejoras (Roadmap)

- [ ] Exportación de datos a Excel
- [ ] Gráficos comparativos entre talleres
- [ ] Alertas automáticas cuando la tasa supera un umbral
- [ ] Importación masiva desde CSV
- [ ] Dashboard dedicado para análisis de imprevistos
- [ ] Integración con datos de Google Sheets

## Soporte

Para preguntas o problemas con el módulo, contacta al equipo de desarrollo de DISTRIKIA.
