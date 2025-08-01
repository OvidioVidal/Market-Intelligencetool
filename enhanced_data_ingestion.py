import pandas as pd
import numpy as np
import streamlit as st
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import re
from pathlib import Path
import sqlite3
from io import BytesIO

class EnhancedDataIngestion:
    """
    Enhanced data ingestion module for M&A market intelligence tool
    Supports manual imports from Mergermarket, Preqin, SEC filings, and index data
    """
    
    def __init__(self, db_path: str = "market_intelligence.db"):
        self.db_path = db_path
        self.init_database()
        
        # Predefined schemas for different data sources
        self.data_schemas = {
            'mergermarket': {
                'required_columns': ['deal_id', 'target_name', 'acquirer_name', 'deal_value', 'announcement_date'],
                'optional_columns': ['industry', 'sector', 'geography', 'deal_type', 'status', 'completion_date']
            },
            'preqin': {
                'required_columns': ['fund_name', 'target_company', 'investment_amount', 'investment_date'],
                'optional_columns': ['fund_type', 'industry', 'geography', 'stage', 'exit_date', 'exit_value']
            },
            'sec_filings': {
                'required_columns': ['company_name', 'filing_type', 'filing_date', 'content'],
                'optional_columns': ['cik', 'ticker', 'form_type', 'url']
            },
            'index_constituents': {
                'required_columns': ['company_name', 'ticker', 'index_name'],
                'optional_columns': ['sector', 'industry', 'market_cap', 'weight', 'country']
            },
            'press_releases': {
                'required_columns': ['company_name', 'title', 'date', 'content'],
                'optional_columns': ['source', 'url', 'sentiment', 'keywords']
            }
        }
        
        # Red flag keywords for due diligence
        self.red_flag_keywords = [
            'litigation', 'lawsuit', 'investigation', 'fraud', 'bankruptcy',
            'regulatory action', 'penalty', 'fine', 'violation', 'compliance',
            'SEC investigation', 'management turnover', 'resignation', 'fired',
            'accounting irregularities', 'restatement', 'audit', 'whistle'
        ]
        
        # Deal event keywords
        self.deal_keywords = [
            'acquisition', 'merger', 'takeover', 'buyout', 'investment',
            'strategic partnership', 'joint venture', 'divestiture', 'spin-off',
            'IPO', 'going private', 'tender offer', 'bid', 'purchase'
        ]
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Deals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deal_id TEXT UNIQUE,
                target_name TEXT,
                acquirer_name TEXT,
                deal_value REAL,
                announcement_date DATE,
                completion_date DATE,
                industry TEXT,
                sector TEXT,
                geography TEXT,
                deal_type TEXT,
                status TEXT,
                source TEXT,
                import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tags TEXT,
                notes TEXT
            )
        ''')
        
        # Companies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT,
                ticker TEXT,
                industry TEXT,
                sector TEXT,
                geography TEXT,
                market_cap REAL,
                revenue REAL,
                ebitda REAL,
                employees INTEGER,
                index_membership TEXT,
                tags TEXT,
                watchlist BOOLEAN DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Filings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS filings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT,
                cik TEXT,
                ticker TEXT,
                filing_type TEXT,
                filing_date DATE,
                content TEXT,
                red_flags TEXT,
                deal_mentions TEXT,
                source TEXT,
                url TEXT,
                import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                alert_name TEXT,
                keywords TEXT,
                filters TEXT,
                email_notifications BOOLEAN DEFAULT 0,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_triggered TIMESTAMP
            )
        ''')
        
        # Watchlist table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                entity_type TEXT,
                entity_id TEXT,
                entity_name TEXT,
                notes TEXT,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def upload_file_interface(self):
        """Streamlit interface for file uploads"""
        st.subheader("📁 Data Upload & Import")
        
        # File upload section
        col1, col2 = st.columns(2)
        
        with col1:
            data_source = st.selectbox(
                "Select Data Source",
                ["Mergermarket", "Preqin", "SEC Filings", "Index Constituents", "Press Releases", "Custom"]
            )
        
        with col2:
            file_format = st.selectbox(
                "File Format",
                ["CSV", "Excel (.xlsx)", "JSON"]
            )
        
        uploaded_file = st.file_uploader(
            f"Upload {data_source} {file_format} file",
            type=['csv', 'xlsx', 'json'],
            help=f"Upload {file_format} file containing {data_source} data"
        )
        
        if uploaded_file is not None:
            try:
                # Process the uploaded file
                df = self.process_uploaded_file(uploaded_file, data_source.lower().replace(' ', '_'), file_format)
                
                if df is not None and not df.empty:
                    st.success(f"File uploaded successfully! {len(df)} records found.")
                    
                    # Show preview
                    st.subheader("Data Preview")
                    st.dataframe(df.head(10))
                    
                    # Validation
                    validation_result = self.validate_data_schema(df, data_source.lower().replace(' ', '_'))
                    
                    if validation_result['valid']:
                        st.success("✅ Data schema validation passed")
                    else:
                        st.warning("⚠️ Data schema validation issues:")
                        for issue in validation_result['issues']:
                            st.write(f"- {issue}")
                    
                    # Import options
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("Import Data"):
                            result = self.import_to_database(df, data_source.lower().replace(' ', '_'))
                            if result['success']:
                                st.success(f"✅ Imported {result['records']} records successfully!")
                            else:
                                st.error(f"❌ Import failed: {result['error']}")
                    
                    with col2:
                        if st.button("Download Template"):
                            template = self.get_data_template(data_source.lower().replace(' ', '_'))
                            st.download_button(
                                label="Download CSV Template",
                                data=template.to_csv(index=False),
                                file_name=f"{data_source.lower()}_template.csv",
                                mime="text/csv"
                            )
                    
                    with col3:
                        # Export processed data
                        csv_data = df.to_csv(index=False)
                        st.download_button(
                            label="Export Processed Data",
                            data=csv_data,
                            file_name=f"processed_{data_source.lower()}_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
        
        # Manual data entry section
        self.manual_data_entry_interface(data_source.lower().replace(' ', '_'))
    
    def process_uploaded_file(self, uploaded_file, data_source: str, file_format: str) -> pd.DataFrame:
        """Process uploaded file based on format and source"""
        try:
            if file_format == "CSV":
                df = pd.read_csv(uploaded_file)
            elif file_format == "Excel (.xlsx)":
                df = pd.read_excel(uploaded_file)
            elif file_format == "JSON":
                df = pd.read_json(uploaded_file)
            
            # Clean and standardize column names
            df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('-', '_')
            
            # Data source specific processing
            if data_source == 'mergermarket':
                df = self.process_mergermarket_data(df)
            elif data_source == 'preqin':
                df = self.process_preqin_data(df)
            elif data_source == 'sec_filings':
                df = self.process_sec_filings(df)
            elif data_source == 'index_constituents':
                df = self.process_index_data(df)
            elif data_source == 'press_releases':
                df = self.process_press_releases(df)
            
            return df
            
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            return None
    
    def process_mergermarket_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process Mergermarket specific data"""
        # Standardize date columns
        date_columns = ['announcement_date', 'completion_date', 'expected_completion']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Clean deal values
        if 'deal_value' in df.columns:
            df['deal_value'] = df['deal_value'].astype(str).str.replace('$', '').str.replace(',', '')
            df['deal_value'] = pd.to_numeric(df['deal_value'], errors='coerce')
        
        # Add metadata
        df['source'] = 'Mergermarket'
        df['import_date'] = datetime.now()
        
        return df
    
    def process_preqin_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process Preqin specific data"""
        # Standardize date columns
        date_columns = ['investment_date', 'exit_date', 'fund_vintage']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Clean investment amounts
        amount_columns = ['investment_amount', 'exit_value', 'fund_size']
        for col in amount_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace('$', '').str.replace(',', '')
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df['source'] = 'Preqin'
        df['import_date'] = datetime.now()
        
        return df
    
    def process_sec_filings(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process SEC filings data"""
        if 'filing_date' in df.columns:
            df['filing_date'] = pd.to_datetime(df['filing_date'], errors='coerce')
        
        # Extract red flags and deal mentions from content
        if 'content' in df.columns:
            df['red_flags'] = df['content'].apply(self.extract_red_flags)
            df['deal_mentions'] = df['content'].apply(self.extract_deal_mentions)
        
        df['source'] = 'SEC EDGAR'
        df['import_date'] = datetime.now()
        
        return df
    
    def process_index_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process index constituent data"""
        # Clean market cap values
        if 'market_cap' in df.columns:
            df['market_cap'] = df['market_cap'].astype(str).str.replace('$', '').str.replace('B', '000000000').str.replace('M', '000000')
            df['market_cap'] = pd.to_numeric(df['market_cap'], errors='coerce')
        
        df['source'] = 'Index Data'
        df['import_date'] = datetime.now()
        
        return df
    
    def process_press_releases(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process press release data"""
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Extract keywords and sentiment
        if 'content' in df.columns:
            df['deal_mentions'] = df['content'].apply(self.extract_deal_mentions)
            df['red_flags'] = df['content'].apply(self.extract_red_flags)
            df['sentiment'] = df['content'].apply(self.analyze_sentiment)
        
        df['source'] = 'Press Release'
        df['import_date'] = datetime.now()
        
        return df
    
    def extract_red_flags(self, text: str) -> str:
        """Extract red flag keywords from text"""
        if pd.isna(text):
            return ""
        
        text_lower = text.lower()
        found_flags = [flag for flag in self.red_flag_keywords if flag in text_lower]
        return ", ".join(found_flags)
    
    def extract_deal_mentions(self, text: str) -> str:
        """Extract deal-related keywords from text"""
        if pd.isna(text):
            return ""
        
        text_lower = text.lower()
        found_deals = [keyword for keyword in self.deal_keywords if keyword in text_lower]
        return ", ".join(found_deals)
    
    def analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis (placeholder for more sophisticated analysis)"""
        if pd.isna(text):
            return "Neutral"
        
        positive_words = ['growth', 'expansion', 'success', 'strong', 'positive', 'good']
        negative_words = ['decline', 'loss', 'weak', 'negative', 'poor', 'difficult']
        
        text_lower = text.lower()
        positive_score = sum(1 for word in positive_words if word in text_lower)
        negative_score = sum(1 for word in negative_words if word in text_lower)
        
        if positive_score > negative_score:
            return "Positive"
        elif negative_score > positive_score:
            return "Negative"
        else:
            return "Neutral"
    
    def validate_data_schema(self, df: pd.DataFrame, data_source: str) -> Dict:
        """Validate data against expected schema"""
        if data_source not in self.data_schemas:
            return {'valid': True, 'issues': []}
        
        schema = self.data_schemas[data_source]
        issues = []
        
        # Check required columns
        missing_required = set(schema['required_columns']) - set(df.columns)
        if missing_required:
            issues.append(f"Missing required columns: {', '.join(missing_required)}")
        
        # Check data types and quality
        if 'deal_value' in df.columns:
            null_values = df['deal_value'].isna().sum()
            if null_values > len(df) * 0.5:
                issues.append(f"High percentage of missing deal values: {null_values}/{len(df)}")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }
    
    def get_data_template(self, data_source: str) -> pd.DataFrame:
        """Generate template DataFrame for data source"""
        if data_source not in self.data_schemas:
            return pd.DataFrame()
        
        schema = self.data_schemas[data_source]
        all_columns = schema['required_columns'] + schema.get('optional_columns', [])
        
        # Create empty template with column headers
        template_data = {col: [] for col in all_columns}
        return pd.DataFrame(template_data)
    
    def import_to_database(self, df: pd.DataFrame, data_source: str) -> Dict:
        """Import processed data to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            if data_source in ['mergermarket', 'preqin']:
                # Import to deals table
                df.to_sql('deals', conn, if_exists='append', index=False)
            elif data_source == 'index_constituents':
                # Import to companies table
                df.to_sql('companies', conn, if_exists='append', index=False)
            elif data_source == 'sec_filings':
                # Import to filings table
                df.to_sql('filings', conn, if_exists='append', index=False)
            
            conn.close()
            
            return {
                'success': True,
                'records': len(df),
                'message': f'Successfully imported {len(df)} records'
            }
            
        except Exception as e:
            return {
                'success': False,
                'records': 0,
                'error': str(e)
            }
    
    def manual_data_entry_interface(self, data_source: str):
        """Interface for manual data entry"""
        st.subheader("✏️ Manual Data Entry")
        
        with st.expander("Add Single Record"):
            if data_source == 'mergermarket':
                self.manual_deal_entry()
            elif data_source == 'index_constituents':
                self.manual_company_entry()
    
    def manual_deal_entry(self):
        """Manual deal entry form"""
        col1, col2 = st.columns(2)
        
        with col1:
            target_name = st.text_input("Target Company")
            acquirer_name = st.text_input("Acquirer")
            deal_value = st.number_input("Deal Value ($M)", min_value=0.0)
            deal_type = st.selectbox("Deal Type", ["Acquisition", "Merger", "LBO", "IPO", "Joint Venture"])
        
        with col2:
            announcement_date = st.date_input("Announcement Date")
            industry = st.selectbox("Industry", ["Technology", "Healthcare", "Finance", "Manufacturing", "Energy", "Other"])
            geography = st.text_input("Geography")
            status = st.selectbox("Status", ["Rumored", "Announced", "Pending", "Complete", "Terminated"])
        
        notes = st.text_area("Notes")
        
        if st.button("Add Deal"):
            deal_data = {
                'target_name': target_name,
                'acquirer_name': acquirer_name,
                'deal_value': deal_value,
                'announcement_date': announcement_date,
                'deal_type': deal_type,
                'industry': industry,
                'geography': geography,
                'status': status,
                'notes': notes,
                'source': 'Manual Entry',
                'import_date': datetime.now()
            }
            
            # Save to database
            if self.save_manual_entry(deal_data, 'deals'):
                st.success("Deal added successfully!")
            else:
                st.error("Failed to add deal")
    
    def manual_company_entry(self):
        """Manual company entry form"""
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Company Name")
            ticker = st.text_input("Ticker Symbol")
            industry = st.selectbox("Industry", ["Technology", "Healthcare", "Finance", "Manufacturing", "Energy", "Other"])
            market_cap = st.number_input("Market Cap ($M)", min_value=0.0)
        
        with col2:
            geography = st.text_input("Geography")
            employees = st.number_input("Employees", min_value=0)
            index_membership = st.text_input("Index Membership (e.g., S&P 500)")
            watchlist = st.checkbox("Add to Watchlist")
        
        if st.button("Add Company"):
            company_data = {
                'company_name': company_name,
                'ticker': ticker,
                'industry': industry,
                'geography': geography,
                'market_cap': market_cap,
                'employees': employees,
                'index_membership': index_membership,
                'watchlist': watchlist,
                'source': 'Manual Entry',
                'last_updated': datetime.now()
            }
            
            if self.save_manual_entry(company_data, 'companies'):
                st.success("Company added successfully!")
            else:
                st.error("Failed to add company")
    
    def save_manual_entry(self, data: Dict, table: str) -> bool:
        """Save manual entry to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.DataFrame([data])
            df.to_sql(table, conn, if_exists='append', index=False)
            conn.close()
            return True
        except Exception as e:
            st.error(f"Database error: {str(e)}")
            return False
    
    def get_data_status(self) -> Dict:
        """Get current data status and statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get record counts
            deals_count = pd.read_sql("SELECT COUNT(*) as count FROM deals", conn).iloc[0]['count']
            companies_count = pd.read_sql("SELECT COUNT(*) as count FROM companies", conn).iloc[0]['count']
            filings_count = pd.read_sql("SELECT COUNT(*) as count FROM filings", conn).iloc[0]['count']
            
            # Get latest import dates
            latest_deal = pd.read_sql("SELECT MAX(import_date) as latest FROM deals", conn).iloc[0]['latest']
            latest_company = pd.read_sql("SELECT MAX(last_updated) as latest FROM companies", conn).iloc[0]['latest']
            
            conn.close()
            
            return {
                'deals': deals_count,
                'companies': companies_count,
                'filings': filings_count,
                'latest_deal_import': latest_deal,
                'latest_company_update': latest_company
            }
            
        except Exception as e:
            return {
                'error': str(e)
            }