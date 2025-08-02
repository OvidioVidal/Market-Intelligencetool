# 🚀 M&A Market Intelligence Tool - Startup Guide

## Quick Start Options

### ⚡ Option 1: One-Command Start (Recommended)
```bash
python3 run.py
```
This will:
- Check and install dependencies
- Initialize the database
- Start the Streamlit application
- Open browser to http://localhost:8501

### 🔧 Option 2: Manual Setup
```bash
# 1. Install dependencies
python3 setup.py

# 2. Start application
streamlit run main_app.py
```

### 📱 Option 3: Simple Demo Version
```bash
streamlit run app.py
```
Use this for a simplified version with sample data.

## File Structure

### Main Applications
- **`main_app.py`** - Full-featured application (recommended)
- **`app.py`** - Simplified demo version
- **`run.py`** - Unified startup script

### Supporting Files
- **`enhanced_data_ingestion.py`** - Advanced data import/processing
- **`deal_sourcing_alerts.py`** - Alert system and keyword detection
- **`data_ingestion.py`** - Simple data generation for app.py
- **`requirements.txt`** - Python dependencies
- **`.streamlit/config.toml`** - Streamlit configuration

## First Run Setup

1. **Install Python 3.8+** (if not already installed)
2. **Navigate to project directory**
3. **Run:** `python3 run.py`
4. **Wait for initialization** (first run creates database)
5. **Access application** at http://localhost:8501

## Troubleshooting

### "Command not found: python"
Use `python3` instead of `python`:
```bash
python3 run.py
```

### "Module not found" errors
Install dependencies manually:
```bash
pip3 install streamlit pandas plotly openpyxl xlsxwriter
```

### Port already in use
Start on different port:
```bash
streamlit run main_app.py --server.port 8502
```

### Database errors
Delete database and restart:
```bash
rm market_intelligence.db
python3 run.py
```

## Features Available on First Run

✅ **Dashboard** - Key metrics and visualizations
✅ **Data Management** - File upload and data viewing
✅ **Deal Sourcing** - Alert creation and keyword monitoring
✅ **Target Screening** - Multi-criteria company search
✅ **Watchlist** - Bookmark companies and deals
✅ **Due Diligence** - Red flag detection
✅ **Market Analysis** - Industry trends and regional activity
✅ **Export/Reports** - Generate reports in multiple formats

## Next Steps After Installation

1. **Upload Data** - Go to "Data Management" and upload CSV/Excel files
2. **Configure Alerts** - Set up keyword-based deal monitoring
3. **Screen Targets** - Use filters to find relevant companies
4. **Build Watchlist** - Add companies/deals to track
5. **Generate Reports** - Export data for analysis

## Support

For issues:
1. Check this guide
2. Review `DEPLOYMENT_CHECKLIST.md`
3. Verify Python 3.8+ is installed
4. Ensure internet connection for package installation

---
*Ready to start? Run: `python3 run.py`*