"""
Simple data ingestion module for compatibility with app.py
This is a simplified version for the basic app.py functionality
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class MarketDataIngestion:
    """Simple data ingestion class for basic app.py compatibility"""
    
    def __init__(self):
        pass
    
    def load_sample_data(self):
        """Generate sample data for demonstration"""
        # Generate sample deals data
        np.random.seed(42)
        n_deals = 50
        
        industries = ['Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Energy', 'Retail']
        deal_types = ['Acquisition', 'Merger', 'LBO', 'IPO']
        statuses = ['Announced', 'Pending', 'Completed', 'Terminated']
        
        deals_data = {
            'deal_id': [f"DEAL-{i:04d}" for i in range(1, n_deals + 1)],
            'target_name': [f"Target Corp {i}" for i in range(1, n_deals + 1)],
            'acquirer_name': [f"Acquirer Inc {i}" for i in range(1, n_deals + 1)],
            'industry': np.random.choice(industries, n_deals),
            'deal_type': np.random.choice(deal_types, n_deals),
            'deal_value_m': np.random.uniform(10, 500, n_deals).round(1),
            'announced_date': pd.date_range(
                start=datetime.now() - timedelta(days=365),
                end=datetime.now(),
                periods=n_deals
            ),
            'status': np.random.choice(statuses, n_deals)
        }
        
        # Generate sample companies data
        n_companies = 100
        
        companies_data = {
            'company_id': [f"COMP-{i:04d}" for i in range(1, n_companies + 1)],
            'company_name': [f"Company {i} Ltd" for i in range(1, n_companies + 1)],
            'industry': np.random.choice(industries, n_companies),
            'market_cap': np.random.uniform(100, 10000, n_companies).round(1),
            'revenue': np.random.uniform(50, 2000, n_companies).round(1),
            'geography': np.random.choice(['North America', 'Europe', 'Asia Pacific'], n_companies),
            'employees': np.random.randint(100, 50000, n_companies)
        }
        
        return {
            'deals': pd.DataFrame(deals_data),
            'companies': pd.DataFrame(companies_data)
        }

# Cache for data persistence
data_cache = {}