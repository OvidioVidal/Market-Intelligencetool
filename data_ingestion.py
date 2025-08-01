import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import streamlit as st

class MarketDataIngestion:
    def __init__(self):
        self.data_sources = {
            'deals': [],
            'companies': [],
            'market_data': [],
            'news': []
        }
    
    def load_sample_data(self) -> Dict:
        """Load sample data for demonstration purposes"""
        
        # Sample deals data
        deals_data = {
            'deal_id': range(1, 26),
            'company_name': [f'Company_{i}' for i in range(1, 26)],
            'target_company': [f'Target_{i}' for i in range(1, 26)],
            'industry': np.random.choice(['Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Energy'], 25),
            'deal_type': np.random.choice(['Acquisition', 'Merger', 'LBO', 'IPO'], 25),
            'deal_value_m': np.random.uniform(10, 500, 25).round(1),
            'status': np.random.choice(['Pipeline', 'Due Diligence', 'Negotiation', 'Closed', 'Terminated'], 25),
            'announced_date': pd.date_range(start='2023-01-01', periods=25, freq='2W'),
            'expected_close': pd.date_range(start='2024-01-01', periods=25, freq='3W'),
            'probability': np.random.uniform(0.3, 0.95, 25).round(2)
        }
        
        # Sample companies data
        companies_data = {
            'company_id': range(1, 51),
            'company_name': [f'Company_{i}' for i in range(1, 51)],
            'industry': np.random.choice(['Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Energy'], 50),
            'revenue_m': np.random.uniform(5, 1000, 50).round(1),
            'ebitda_m': np.random.uniform(1, 200, 50).round(1),
            'employees': np.random.randint(50, 5000, 50),
            'founded_year': np.random.randint(1990, 2020, 50),
            'headquarters': np.random.choice(['New York', 'San Francisco', 'London', 'Frankfurt', 'Tokyo'], 50),
            'market_cap_m': np.random.uniform(50, 5000, 50).round(1),
            'public_private': np.random.choice(['Public', 'Private'], 50, p=[0.3, 0.7])
        }
        
        # Sample market data
        dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
        market_data = {
            'date': dates,
            'market_index': 1000 + np.cumsum(np.random.normal(0, 10, len(dates))),
            'deal_volume': np.random.poisson(5, len(dates)),
            'avg_deal_size': np.random.uniform(20, 100, len(dates)),
            'volatility': np.random.uniform(0.1, 0.4, len(dates))
        }
        
        return {
            'deals': pd.DataFrame(deals_data),
            'companies': pd.DataFrame(companies_data),
            'market_data': pd.DataFrame(market_data)
        }
    
    def load_from_csv(self, file_path: str, data_type: str) -> pd.DataFrame:
        """Load data from CSV file"""
        try:
            df = pd.read_csv(file_path)
            self.data_sources[data_type] = df
            return df
        except Exception as e:
            st.error(f"Error loading CSV file: {e}")
            return pd.DataFrame()
    
    def load_from_excel(self, file_path: str, sheet_name: str, data_type: str) -> pd.DataFrame:
        """Load data from Excel file"""
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            self.data_sources[data_type] = df
            return df
        except Exception as e:
            st.error(f"Error loading Excel file: {e}")
            return pd.DataFrame()
    
    def fetch_market_news(self, query: str = "mergers acquisitions", limit: int = 10) -> List[Dict]:
        """Fetch market news (placeholder for API integration)"""
        # This is a placeholder - in production, you'd integrate with news APIs
        sample_news = []
        for i in range(limit):
            news_item = {
                'title': f'Market News Item {i+1}: {query}',
                'summary': f'Summary of news item {i+1} related to {query}',
                'source': f'Source {i+1}',
                'published_date': datetime.now() - timedelta(days=i),
                'url': f'https://example.com/news/{i+1}',
                'sentiment': np.random.choice(['Positive', 'Neutral', 'Negative'])
            }
            sample_news.append(news_item)
        
        return sample_news
    
    def validate_data(self, df: pd.DataFrame, data_type: str) -> bool:
        """Validate data based on type"""
        if df.empty:
            return False
        
        required_columns = {
            'deals': ['company_name', 'deal_value_m', 'industry'],
            'companies': ['company_name', 'industry', 'revenue_m'],
            'market_data': ['date']
        }
        
        if data_type in required_columns:
            missing_cols = set(required_columns[data_type]) - set(df.columns)
            if missing_cols:
                st.error(f"Missing required columns for {data_type}: {missing_cols}")
                return False
        
        return True
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess data"""
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Handle missing values
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())
        
        categorical_columns = df.select_dtypes(include=['object']).columns
        df[categorical_columns] = df[categorical_columns].fillna('Unknown')
        
        return df
    
    def get_industry_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate industry-specific metrics"""
        if 'industry' not in df.columns:
            return {}
        
        metrics = {}
        for industry in df['industry'].unique():
            industry_data = df[df['industry'] == industry]
            
            metrics[industry] = {
                'count': len(industry_data),
                'avg_deal_value': industry_data.get('deal_value_m', pd.Series()).mean(),
                'total_value': industry_data.get('deal_value_m', pd.Series()).sum(),
                'avg_revenue': industry_data.get('revenue_m', pd.Series()).mean()
            }
        
        return metrics
    
    def export_data(self, df: pd.DataFrame, filename: str, format_type: str = 'csv'):
        """Export data to file"""
        try:
            if format_type.lower() == 'csv':
                df.to_csv(filename, index=False)
            elif format_type.lower() == 'excel':
                df.to_excel(filename, index=False)
            
            st.success(f"Data exported to {filename}")
        except Exception as e:
            st.error(f"Error exporting data: {e}")

class DataCache:
    """Simple caching mechanism for data"""
    
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
    
    def get(self, key: str, max_age_hours: int = 24):
        """Get cached data if it's still fresh"""
        if key in self._cache:
            age = datetime.now() - self._timestamps[key]
            if age.total_seconds() < max_age_hours * 3600:
                return self._cache[key]
        return None
    
    def set(self, key: str, data):
        """Cache data with timestamp"""
        self._cache[key] = data
        self._timestamps[key] = datetime.now()
    
    def clear(self):
        """Clear all cached data"""
        self._cache.clear()
        self._timestamps.clear()

# Global cache instance
data_cache = DataCache()