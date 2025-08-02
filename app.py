import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from data_ingestion import MarketDataIngestion, data_cache

st.set_page_config(
    page_title="Market Intelligence Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    """Load and cache market data"""
    data_ingestion = MarketDataIngestion()
    return data_ingestion.load_sample_data()

def main():
    st.title("🏢 Market Intelligence Tool")
    st.subheader("M&A Boutique Market Analysis Dashboard")
    
    # Load data
    if 'data' not in st.session_state:
        st.session_state.data = load_data()
    
    # Sidebar for navigation and filters
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Page",
        ["Dashboard", "Deal Tracker", "Market Analysis", "Company Research", "Data Management"]
    )
    
    # Global filters in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Global Filters")
    
    # Industry filter
    all_industries = ['All'] + list(st.session_state.data['deals']['industry'].unique())
    selected_industry = st.sidebar.selectbox("Industry", all_industries)
    
    # Date range filter
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(datetime.now() - timedelta(days=365), datetime.now()),
        key="date_filter"
    )
    
    # Deal value filter
    min_value, max_value = st.sidebar.slider(
        "Deal Value Range ($M)",
        min_value=0,
        max_value=int(st.session_state.data['deals']['deal_value_m'].max()),
        value=(0, int(st.session_state.data['deals']['deal_value_m'].max())),
        step=10
    )
    
    # Apply filters to data
    filtered_data = apply_filters(
        st.session_state.data, 
        selected_industry, 
        date_range, 
        min_value, 
        max_value
    )
    
    if page == "Dashboard":
        show_dashboard(filtered_data)
    elif page == "Deal Tracker":
        show_deal_tracker(filtered_data)
    elif page == "Market Analysis":
        show_market_analysis(filtered_data)
    elif page == "Company Research":
        show_company_research(filtered_data)
    elif page == "Data Management":
        show_data_management(filtered_data)

def apply_filters(data, industry, date_range, min_value, max_value):
    """Apply global filters to the data"""
    filtered_data = data.copy()
    
    # Industry filter
    if industry != 'All':
        filtered_data['deals'] = filtered_data['deals'][
            filtered_data['deals']['industry'] == industry
        ]
        filtered_data['companies'] = filtered_data['companies'][
            filtered_data['companies']['industry'] == industry
        ]
    
    # Date range filter (for deals)
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_data['deals'] = filtered_data['deals'][
            (filtered_data['deals']['announced_date'] >= pd.Timestamp(start_date)) &
            (filtered_data['deals']['announced_date'] <= pd.Timestamp(end_date))
        ]
    
    # Deal value filter
    filtered_data['deals'] = filtered_data['deals'][
        (filtered_data['deals']['deal_value_m'] >= min_value) &
        (filtered_data['deals']['deal_value_m'] <= max_value)
    ]
    
    return filtered_data

def show_dashboard(data):
    st.header("📈 Market Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Deals", "24", "↑ +3")
    with col2:
        st.metric("Market Cap ($B)", "145.7", "↑ +2.3%")
    with col3:
        st.metric("Avg Deal Size ($M)", "12.4", "↓ -1.2%")
    with col4:
        st.metric("Success Rate", "73%", "↑ +5%")
    
    st.subheader("Recent Market Activity")
    
    # Sample data for demonstration
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
    deal_volume = np.random.randint(5, 25, len(dates))
    deal_value = np.random.uniform(50, 200, len(dates))
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.line(
            x=dates, 
            y=deal_volume,
            title="Monthly Deal Volume",
            labels={'x': 'Date', 'y': 'Number of Deals'}
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = px.bar(
            x=dates, 
            y=deal_value,
            title="Monthly Deal Value ($M)",
            labels={'x': 'Date', 'y': 'Deal Value ($M)'}
        )
        st.plotly_chart(fig2, use_container_width=True)

def show_deal_tracker(data):
    st.header("🎯 Deal Tracker")
    
    # Deal input form
    with st.expander("Add New Deal"):
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("Company Name")
            deal_type = st.selectbox("Deal Type", ["Acquisition", "Merger", "IPO", "LBO"])
            deal_value = st.number_input("Deal Value ($M)", min_value=0.0)
        with col2:
            industry = st.selectbox("Industry", ["Technology", "Healthcare", "Finance", "Manufacturing", "Retail"])
            status = st.selectbox("Status", ["Pipeline", "Due Diligence", "Negotiation", "Closed"])
            expected_close = st.date_input("Expected Close Date")
        
        if st.button("Add Deal"):
            st.success(f"Deal for {company_name} added successfully!")
    
    # Sample deals table
    deals_data = {
        "Company": ["TechCorp", "HealthPlus", "FinanceMax", "ManufactureInc"],
        "Industry": ["Technology", "Healthcare", "Finance", "Manufacturing"],
        "Deal Type": ["Acquisition", "Merger", "LBO", "Acquisition"],
        "Value ($M)": [45.2, 78.5, 123.0, 34.7],
        "Status": ["Due Diligence", "Negotiation", "Pipeline", "Closed"],
        "Expected Close": ["2024-03-15", "2024-04-22", "2024-05-10", "2024-02-28"]
    }
    
    df_deals = pd.DataFrame(deals_data)
    st.dataframe(df_deals, use_container_width=True)

def show_market_analysis(data):
    st.header("📊 Market Analysis")
    
    # Industry analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Deal Distribution by Industry")
        industry_data = ["Technology", "Healthcare", "Finance", "Manufacturing", "Retail"]
        industry_values = [35, 25, 20, 15, 5]
        
        fig = px.pie(
            values=industry_values,
            names=industry_data,
            title="M&A Activity by Industry"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Deal Size Distribution")
        size_ranges = ["<$10M", "$10-50M", "$50-100M", "$100M+"]
        size_counts = [12, 18, 8, 6]
        
        fig2 = px.bar(
            x=size_ranges,
            y=size_counts,
            title="Deals by Size Range"
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Market trends
    st.subheader("Market Trends")
    
    trend_options = st.multiselect(
        "Select Metrics to Display",
        ["Deal Volume", "Average Deal Size", "Market Valuation", "Success Rate"],
        default=["Deal Volume", "Average Deal Size"]
    )
    
    if trend_options:
        dates = pd.date_range(start='2024-01-01', periods=12, freq='M')
        fig = go.Figure()
        
        for metric in trend_options:
            if metric == "Deal Volume":
                values = np.random.randint(15, 30, 12)
            elif metric == "Average Deal Size":
                values = np.random.uniform(40, 80, 12)
            elif metric == "Market Valuation":
                values = np.random.uniform(100, 200, 12)
            else:  # Success Rate
                values = np.random.uniform(60, 85, 12)
            
            fig.add_trace(go.Scatter(x=dates, y=values, name=metric, mode='lines+markers'))
        
        fig.update_layout(title="Market Trends Over Time")
        st.plotly_chart(fig, use_container_width=True)

def show_company_research(data):
    st.header("🔍 Company Research")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        company_search = st.text_input("Search Company", placeholder="Enter company name...")
        
        if company_search:
            st.subheader(f"Research Results for: {company_search}")
            
            # Company profile tabs
            tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Financials", "Market Position", "M&A History"])
            
            with tab1:
                st.write("**Industry:** Technology")
                st.write("**Founded:** 2010")
                st.write("**Employees:** 1,200")
                st.write("**Revenue:** $85M (2023)")
                st.write("**Headquarters:** San Francisco, CA")
            
            with tab2:
                financial_data = {
                    "Year": [2021, 2022, 2023],
                    "Revenue ($M)": [65, 75, 85],
                    "EBITDA ($M)": [12, 18, 22],
                    "Growth Rate (%)": [15, 15.4, 13.3]
                }
                st.dataframe(pd.DataFrame(financial_data))
            
            with tab3:
                st.write("**Market Share:** 8.5%")
                st.write("**Key Competitors:** CompetitorA, CompetitorB")
                st.write("**Competitive Advantages:** Strong IP portfolio, established customer base")
            
            with tab4:
                st.write("**Previous M&A Activity:**")
                st.write("- 2022: Acquired StartupXYZ for $5M")
                st.write("- 2021: Merged with TechPartner")
    
    with col2:
        st.subheader("Quick Actions")
        st.button("📊 Generate Valuation Model")
        st.button("📈 Market Comparison")
        st.button("💼 Create Deal Profile")
        st.button("📄 Export Report")
        
        st.subheader("Watchlist")
        watchlist = ["TechCorp", "HealthPlus", "FinanceMax"]
        for company in watchlist:
            st.write(f"• {company}")

def show_data_management(data):
    """Simple data management interface"""
    st.header("📁 Data Management")
    
    st.subheader("📊 Current Data Overview")
    
    # Display data summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Deals", len(data.get('deals', [])))
    with col2:
        st.metric("Total Companies", len(data.get('companies', [])))
    with col3:
        st.metric("Data Sources", "Sample Data")
    
    # Show data tables
    st.subheader("📋 Data Tables")
    
    tab1, tab2 = st.tabs(["Deals", "Companies"])
    
    with tab1:
        if 'deals' in data and not data['deals'].empty:
            st.dataframe(data['deals'].head(20), use_container_width=True)
        else:
            st.info("No deals data available")
    
    with tab2:
        if 'companies' in data and not data['companies'].empty:
            st.dataframe(data['companies'].head(20), use_container_width=True)
        else:
            st.info("No companies data available")
    
    # File upload interface
    st.subheader("📤 Upload Data")
    uploaded_file = st.file_uploader(
        "Upload CSV/Excel file",
        type=['csv', 'xlsx'],
        help="Upload deal data, company information, or other relevant files"
    )
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success(f"Successfully loaded {len(df)} rows")
            st.dataframe(df.head(), use_container_width=True)
            
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")

if __name__ == "__main__":
    main()