# M&A Market Intelligence Tool

A comprehensive market intelligence platform for M&A boutiques, enabling deal sourcing, target identification, and due diligence through consolidated data from multiple sources.

## Features

### 🎯 Core Capabilities
- **Data Ingestion**: Import CSV/Excel files from Mergermarket, Preqin, SEC filings, and index constituents
- **Deal Sourcing**: Keyword-driven deal detection with configurable alerts
- **Target Screening**: Multi-criteria search and filtering with company tagging
- **Watchlist**: Bookmark and track companies and deals of interest
- **Due Diligence**: Red flag detection and deal fact extraction
- **Market Analysis**: Activity heatmaps, sector trends, and regional distribution
- **Export & Reports**: Generate CSV, Excel, and PDF reports

### 📊 Dashboard Features
- Real-time deal metrics and KPIs
- Interactive charts and visualizations
- Recent deal activity tracking
- Alert summary and notifications

### 🔍 Advanced Search
- Industry, geography, and financial threshold filters
- Index membership screening (S&P 500, FTSE 100, etc.)
- Company tagging system (potential target, active acquirer, etc.)
- Transaction history analysis

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Setup
1. Download the project files to your local machine

2. Navigate to the project directory:
```bash
cd "MARKET INTELLIGENCE TOOL"
```

3. Run the setup script:
```bash
python3 setup.py
```

4. Start the application:
```bash
# Option 1: One-command start (recommended)
python run.py

# Option 2: Manual start
streamlit run main_app.py
```

5. Open your web browser and navigate to `http://localhost:8501`

### Manual Installation (Alternative)
If the setup script doesn't work:
```bash
pip install streamlit pandas plotly openpyxl xlsxwriter python-dateutil requests beautifulsoup4 tqdm
streamlit run main_app.py
```

## Usage

### Data Import
1. Navigate to **Data Management** section
2. Select your data source (Mergermarket, Preqin, etc.)
3. Upload CSV or Excel files
4. Review data preview and validation
5. Import to database

### Setting Up Alerts
1. Go to **Deal Sourcing & Alerts**
2. Create new alert with:
   - Alert name
   - Keywords (acquisition, merger, etc.)
   - Industry and geography filters
   - Deal size thresholds
   - Email notification settings
3. Test and activate alerts

### Target Screening
1. Access **Target Screening** module
2. Set multi-criteria filters:
   - Industries and geographies
   - Financial thresholds
   - Index membership
   - Company tags
3. Search and review results
4. Tag companies of interest

### Watchlist Management
1. Add companies or deals to watchlist
2. Include notes and observations
3. Monitor watchlist items from dashboard

### Due Diligence
1. Enter company name for analysis
2. Review recent filings and red flags
3. Analyze deal facts and transaction history

### Export Reports
1. Select report type and date range
2. Choose export format (CSV, Excel, PDF)
3. Generate and download reports

## Data Sources

### Supported Import Formats
- **Mergermarket**: Deal data with target/acquirer information
- **Preqin**: Private equity and venture capital transactions
- **SEC Filings**: Regulatory filings with red flag detection
- **Index Constituents**: S&P 500, FTSE 100, DAX, etc.
- **Press Releases**: Company announcements and news

### Data Templates
Use the built-in template generator to ensure proper data formatting:
1. Go to Data Management
2. Select data source
3. Click "Download Template"
4. Format your data according to template

## Configuration

### Database
The application uses SQLite database (`market_intelligence.db`) for data storage. The database is automatically created on first run.

### Email Alerts
To enable email notifications:
1. Configure SMTP settings in the alerts system
2. Add email addresses to alert configurations
3. Test email delivery

## Troubleshooting

### Common Issues

**Database Errors**
- Ensure SQLite database file is not locked
- Check file permissions in project directory

**Import Failures**
- Verify CSV/Excel file format matches expected schema
- Check for special characters in company names
- Ensure date columns are properly formatted

**Missing Dependencies**
```bash
pip install --upgrade -r requirements.txt
```

**Port Already in Use**
```bash
streamlit run main_app.py --server.port 8502
```

## Development

### Project Structure
```
MARKET INTELLIGENCE TOOL/
├── main_app.py                    # Main Streamlit application
├── enhanced_data_ingestion.py     # Data import and processing
├── deal_sourcing_alerts.py        # Alert system and deal detection
├── requirements.txt               # Python dependencies
├── README.md                      # This file
├── MVP.prd                        # Product requirements document
└── market_intelligence.db         # SQLite database (auto-created)
```

### Adding New Features
1. Follow the modular structure
2. Add new functions to appropriate modules
3. Update requirements.txt if new dependencies are needed
4. Test thoroughly with sample data

### Data Schema
The application uses these main database tables:
- `deals`: M&A transactions and deal information
- `companies`: Company profiles and financial data
- `filings`: SEC and regulatory filings
- `alerts`: User-configured alert settings
- `watchlist`: Bookmarked items and notes

## License

This is a proprietary tool developed for M&A market intelligence purposes.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review error messages in the Streamlit interface
3. Verify data format compatibility
4. Ensure all dependencies are properly installed

## Version History

### v1.0.0 (MVP)
- Initial release with core features
- Data ingestion for major sources
- Basic alert system
- Target screening and watchlist
- Export capabilities
- Due diligence light features