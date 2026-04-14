# 🚀 Quick Start Guide - Tasa de Imprevistos Module

## ✅ Installation Complete!

The new **Tasa de Imprevistos** module has been successfully integrated into your DISTRIKIA Dashboard.

## 📁 New Files Created

```
distrikia-dashboard/
├── modules/
│   ├── imprevistos_config.py          # Configuration & data persistence
│   ├── imprevistos_data.py            # Data entry forms
│   ├── imprevistos_processor.py       # Data processing & deduplication
│   └── imprevistos_visualizations.py  # Charts & tables
└── docs/
    └── IMPREVISTOS_MODULE.md          # Full documentation
```

## 🎯 Key Features Implemented

### 1. **Data Entry Form** (Sidebar button: "📊 Registrar Imprevistos")
- Select workshop and period (year/month)
- Enter total vehicles delivered
- Register each imprevisto with:
  - License plate (placa)
  - Claim number (siniestro)
  - Type (cambio de repuestos / mano de obra)
  - Cause (for mano de obra type)

### 2. **Automatic Deduplication**
- Rule: If same placa+siniestro exists → count only 1
- Prevents inflated rates from duplicate entries

### 3. **Fault Classification**

**Culpa del Taller (Workshop's Fault):**
- Digitación
- No cotizado
- Predesarme
- Sin fotos claras
- Sin diagnóstico
- Error de diagnóstico
- Daño adicional

**NO es Culpa del Taller (Not Workshop's Fault):**
- Con cambio de repuestos (always)
- Mano de obra with causal = "No visible"

### 4. **Combined Bar + Line Chart**
- Blue bars: Total vehicles
- Orange bars: Total imprevistos
- Red line: Imprevistos rate (%)
- Green line (optional): Workshop fault rate (%)

### 5. **Monthly Summary Table**
Columns:
- Mes (Month)
- Cantidad Vehículos (Vehicle count)
- Cantidad Imprevistos (Imprevistos count)
- Tasa (%) (Rate %)
- Breakdown by fault classification

## 🚀 How to Use

### Step 1: Start the Dashboard
```bash
cd /Users/xstaked/Desktop/projects/sn8-projects/distrikia-dashboard
streamlit run app.py
```

### Step 2: Register Imprevistos Data
1. Click **"📊 Registrar Imprevistos"** button in sidebar
2. Select workshop, year, and month
3. Enter total vehicles delivered
4. Add imprevistos one by one:
   - Enter plate number
   - Enter claim number
   - Select type
   - Select cause (if applicable)
   - Click "➕ Agregar Imprevisto"

### Step 3: View Results
- **Chart:** Scroll to "Tasa de Imprevistos" section in dashboard
- **Summary:** Click "📋 Ver Resumen de Imprevistos" in sidebar
- **Details:** Expand any section to see detailed breakdowns

## 📊 Calculation Example

```
January 2024:
- Vehicles delivered: 100
- Imprevistos registered: 15
- Workshop fault: 5
- Not workshop fault: 10

Results:
- Total Rate: (15/100) × 100 = 15%
- Workshop Fault Rate: (5/100) × 100 = 5%
- Not Workshop Fault Rate: (10/100) × 100 = 10%
```

## 💾 Data Storage

All data is saved to: `data/imprevistos_data.json`

The file is created automatically when you register your first imprevisto.

## 🔧 Configuration (Optional)

To customize causes or fault classification rules, edit:
- `modules/imprevistos_config.py`

Look for:
- `CAUSAS_MANO_OBRA` - List of causes
- `CAUSAS_CULPA_TALLER` - Fault classification for each cause

## ⚠️ Important Notes

1. **Deduplication:** Same plate+claim = 1 imprevisto (automatic)
2. **Data Persistence:** Data is saved in JSON format
3. **Multi-workshop Support:** Each workshop tracks its own imprevistos
4. **Dashboard Integration:** Charts respect existing dashboard filters

## 🐛 Troubleshooting

**Problem:** "No hay datos disponibles"
- **Solution:** Register at least one imprevisto first

**Problem:** "Imprevisto duplicado" warning
- **Solution:** This is normal - the system prevents duplicate entries for same plate+claim

**Problem:** Rate shows 0%
- **Solution:** Make sure you entered the total vehicles delivered for the period

## 📚 Full Documentation

See `docs/IMPREVISTOS_MODULE.md` for complete documentation including:
- Advanced configuration
- Data structure details
- API reference
- Future roadmap

## 🎉 You're All Set!

The module is fully integrated and ready to use. Start registering imprevistos data and gain insights into your workshop performance!
