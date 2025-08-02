#!/usr/bin/env python3
"""
Ultra-fast simplified M&A Market Intelligence Tool
Minimal loading time with essential features only
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Configure Streamlit page
st.set_page_config(
    page_title="Market Intelligence Tool - Fast",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

@st.cache_data(persist=True)
def generate_fast_sample_data():
    """Generate sample data with persistent caching"""
    np.random.seed(42)
    
    # Quick sample data generation
    industries = ['Technology', 'Healthcare', 'Finance', 'Energy']
    n_deals = 30
    
    deals = pd.DataFrame({
        'target': [f"Target {i}" for i in range(1, n_deals + 1)],
        'acquirer': [f"Acquirer {i}" for i in range(1, n_deals + 1)],
        'industry': np.random.choice(industries, n_deals),
        'value_m': np.random.uniform(10, 500, n_deals).round(1),
        'date': pd.date_range(start='2024-01-01', periods=n_deals, freq='10D'),
        'status': np.random.choice(['Announced', 'Pending', 'Completed'], n_deals)
    })
    
    return deals

def main():
    """Ultra-fast main application"""
    
    # Header
    st.title("⚡ M&A Intelligence Tool - Fast Mode")
    st.caption("Optimized for speed • Essential features only")
    
    # Load data (cached)
    data = generate_fast_sample_data()
    
    # Quick metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Deals", len(data))
    with col2:
        st.metric("Avg Value", f"${data['value_m'].mean():.1f}M")
    with col3:
        st.metric("This Month", len(data[data['date'] >= '2024-11-01']))
    with col4:
        st.metric("Active", len(data[data['status'].isin(['Announced', 'Pending'])]))
    
    # Quick filters
    st.subheader("🔍 Quick Filters")
    col1, col2 = st.columns(2)
    
    with col1:
        selected_industry = st.selectbox("Industry", ['All'] + list(data['industry'].unique()))
    with col2:
        min_value = st.slider("Min Deal Value ($M)", 0, 500, 0)
    
    # Apply filters
    filtered_data = data.copy()
    if selected_industry != 'All':
        filtered_data = filtered_data[filtered_data['industry'] == selected_industry]
    filtered_data = filtered_data[filtered_data['value_m'] >= min_value]
    
    # Results
    st.subheader(f"📊 Results ({len(filtered_data)} deals)")
    
    if len(filtered_data) > 0:
        # Quick chart (only if plotly is available)
        try:
            import plotly.express as px
            fig = px.bar(
                filtered_data.groupby('industry').size().reset_index(name='count'),
                x='industry', y='count', title='Deals by Industry'
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            st.info("Install plotly for charts: pip install plotly")
        
        # Data table
        display_data = filtered_data[['target', 'acquirer', 'industry', 'value_m', 'status']].copy()
        display_data['value_m'] = display_data['value_m'].apply(lambda x: f"${x:.1f}M")
        
        st.dataframe(
            display_data, 
            use_container_width=True,
            column_config={
                'target': 'Target',
                'acquirer': 'Acquirer',
                'industry': 'Industry', 
                'value_m': 'Value',
                'status': 'Status'
            }
        )
    else:
        st.info("No deals match your criteria")
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
    
    with col2:
        if st.button("💾 Download CSV"):
            csv = filtered_data.to_csv(index=False)
            st.download_button("Download", csv, "deals.csv", "text/csv")
    
    with col3:
        if st.button("🚀 Full App"):
            st.info("Run: python run.py")

if __name__ == "__main__":
    main()