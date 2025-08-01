try:
    import streamlit as st
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from datetime import datetime, timedelta
    import numpy as np
    import sqlite3
    import json
    from enhanced_data_ingestion import EnhancedDataIngestion
    from deal_sourcing_alerts import DealSourcingAlerts
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Please run: python3 setup.py")
    print("Or manually install: pip install streamlit pandas plotly openpyxl xlsxwriter")
    exit(1)

# Configure Streamlit page
st.set_page_config(
    page_title="M&A Market Intelligence Tool",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = "demo_user"

def main():
    """Main application entry point"""
    
    # Initialize data ingestion and alerts with error handling
    try:
        data_ingestion = EnhancedDataIngestion()
        alerts_system = DealSourcingAlerts()
    except Exception as e:
        st.error(f"Error initializing application: {str(e)}")
        st.stop()
    
    # Application header
    st.title("🏢 M&A Market Intelligence Tool")
    st.markdown("*Professional deal sourcing, target identification, and due diligence platform*")
    
    # Sidebar navigation
    with st.sidebar:
        st.title("Navigation")
        
        # Main navigation
        page = st.selectbox(
            "Select Module",
            [
                "📊 Dashboard",
                "📁 Data Management", 
                "🚨 Deal Sourcing & Alerts",
                "🎯 Target Screening",
                "📋 Watchlist",
                "🔍 Due Diligence",
                "📈 Market Analysis",
                "📤 Export & Reports"
            ]
        )
        
        st.markdown("---")
        
        # Data status
        st.subheader("📊 Data Status")
        data_status = data_ingestion.get_data_status()
        
        if 'error' not in data_status:
            st.metric("Deals", data_status.get('deals', 0))
            st.metric("Companies", data_status.get('companies', 0))
            st.metric("Filings", data_status.get('filings', 0))
            
            if data_status.get('latest_deal_import'):
                st.caption(f"Last import: {data_status['latest_deal_import'][:10]}")
        else:
            st.error("Database connection error")
        
        st.markdown("---")
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
        if st.button("🚨 Run Alerts"):
            results = alerts_system.run_all_alerts()
            total_matches = sum(len(matches) for matches in results.values())
            st.success(f"Found {total_matches} total matches across all alerts")
    
    # Main content area
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "📁 Data Management":
        show_data_management(data_ingestion)
    elif page == "🚨 Deal Sourcing & Alerts":
        show_deal_sourcing(alerts_system)
    elif page == "🎯 Target Screening":
        show_target_screening()
    elif page == "📋 Watchlist":
        show_watchlist()
    elif page == "🔍 Due Diligence":
        show_due_diligence()
    elif page == "📈 Market Analysis":
        show_market_analysis()
    elif page == "📤 Export & Reports":
        show_export_reports()

def show_dashboard():
    """Main dashboard with key metrics and visualizations"""
    st.header("📊 Market Intelligence Dashboard")
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        conn = sqlite3.connect("market_intelligence.db")
        
        # Total deals
        total_deals = pd.read_sql("SELECT COUNT(*) as count FROM deals", conn).iloc[0]['count']
        
        # Deals this month
        deals_this_month = pd.read_sql("""
            SELECT COUNT(*) as count FROM deals 
            WHERE announcement_date >= date('now', 'start of month')
        """, conn).iloc[0]['count']
        
        # Average deal size
        avg_deal_size = pd.read_sql("""
            SELECT AVG(deal_value) as avg_size FROM deals 
            WHERE deal_value > 0
        """, conn).iloc[0]['avg_size'] or 0
        
        # Active deals
        active_deals = pd.read_sql("""
            SELECT COUNT(*) as count FROM deals 
            WHERE status IN ('Announced', 'Pending')
        """, conn).iloc[0]['count']
        
        conn.close()
        
        with col1:
            st.metric("Total Deals", f"{total_deals:,}", f"+{deals_this_month} this month")
        with col2:
            st.metric("Avg Deal Size", f"${avg_deal_size:.1f}M", "↑ +5.2%")
        with col3:
            st.metric("Active Deals", f"{active_deals:,}", "↑ +12")
        with col4:
            success_rate = 73  # Placeholder
            st.metric("Success Rate", f"{success_rate}%", "↑ +3%")
            
    except Exception as e:
        st.error(f"Error loading dashboard metrics: {str(e)}")
    
    st.markdown("---")
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        show_deal_volume_chart()
    
    with col2:
        show_industry_distribution()
    
    # Recent activity
    st.subheader("📈 Recent Deal Activity")
    show_recent_deals_table()
    
    # Alert summary
    st.subheader("🚨 Alert Summary")
    show_alert_summary()

def show_deal_volume_chart():
    """Show deal volume over time"""
    try:
        conn = sqlite3.connect("market_intelligence.db")
        
        query = """
            SELECT 
                strftime('%Y-%m', announcement_date) as month,
                COUNT(*) as deal_count,
                SUM(deal_value) as total_value
            FROM deals 
            WHERE announcement_date >= date('now', '-12 months')
            GROUP BY strftime('%Y-%m', announcement_date)
            ORDER BY month
        """
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        if not df.empty:
            fig = px.line(df, x='month', y='deal_count', 
                         title='Monthly Deal Volume',
                         labels={'month': 'Month', 'deal_count': 'Number of Deals'})
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No deal data available for chart")
            
    except Exception as e:
        st.error(f"Error loading deal volume chart: {str(e)}")

def show_industry_distribution():
    """Show industry distribution pie chart"""
    try:
        conn = sqlite3.connect("market_intelligence.db")
        
        query = """
            SELECT industry, COUNT(*) as count
            FROM deals 
            WHERE industry IS NOT NULL
            GROUP BY industry
            ORDER BY count DESC
            LIMIT 10
        """
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        if not df.empty:
            fig = px.pie(df, values='count', names='industry', 
                        title='Deal Distribution by Industry')
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No industry data available")
            
    except Exception as e:
        st.error(f"Error loading industry chart: {str(e)}")

def show_recent_deals_table():
    """Show recent deals in a table"""
    try:
        conn = sqlite3.connect("market_intelligence.db")
        
        query = """
            SELECT target_name, acquirer_name, deal_value, industry, 
                   announcement_date, status
            FROM deals 
            ORDER BY announcement_date DESC
            LIMIT 10
        """
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        if not df.empty:
            # Format deal values
            df['deal_value'] = df['deal_value'].apply(
                lambda x: f"${x:.1f}M" if pd.notna(x) and x > 0 else "Undisclosed"
            )
            
            st.dataframe(
                df,
                column_config={
                    "target_name": "Target",
                    "acquirer_name": "Acquirer", 
                    "deal_value": "Deal Value",
                    "industry": "Industry",
                    "announcement_date": "Date",
                    "status": "Status"
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No recent deals to display")
            
    except Exception as e:
        st.error(f"Error loading recent deals: {str(e)}")

def show_alert_summary():
    """Show alert summary"""
    try:
        conn = sqlite3.connect("market_intelligence.db")
        
        # Get alert count
        alert_count = pd.read_sql("SELECT COUNT(*) as count FROM alerts", conn).iloc[0]['count']
        
        # Get recent triggered alerts
        query = """
            SELECT alert_name, last_triggered
            FROM alerts
            WHERE last_triggered IS NOT NULL
            ORDER BY last_triggered DESC
            LIMIT 5
        """
        
        recent_alerts = pd.read_sql(query, conn)
        conn.close()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Active Alerts", alert_count)
            
        with col2:
            if not recent_alerts.empty:
                st.write("**Recently Triggered:**")
                for _, alert in recent_alerts.iterrows():
                    st.write(f"• {alert['alert_name']}")
            else:
                st.write("No recent alert activity")
                
    except Exception as e:
        st.error(f"Error loading alert summary: {str(e)}")

def show_data_management(data_ingestion):
    """Data management and import interface"""
    st.header("📁 Data Management")
    
    # File upload interface
    data_ingestion.upload_file_interface()
    
    st.markdown("---")
    
    # Data overview
    st.subheader("📊 Data Overview")
    
    tab1, tab2, tab3 = st.tabs(["Deals", "Companies", "Filings"])
    
    with tab1:
        show_data_table("deals", "Deals Database")
    
    with tab2:
        show_data_table("companies", "Companies Database") 
    
    with tab3:
        show_data_table("filings", "Filings Database")

def show_data_table(table_name: str, title: str):
    """Show data table with filtering options"""
    try:
        conn = sqlite3.connect("market_intelligence.db")
        df = pd.read_sql(f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT 100", conn)
        conn.close()
        
        if not df.empty:
            st.write(f"**{title}** ({len(df)} records shown)")
            
            # Add search functionality
            if 'target_name' in df.columns:
                search_term = st.text_input(f"Search {table_name}", key=f"search_{table_name}")
                if search_term:
                    mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
                    df = df[mask]
            
            st.dataframe(df, use_container_width=True, height=400)
        else:
            st.info(f"No data in {table_name} table")
            
    except Exception as e:
        st.error(f"Error loading {table_name} data: {str(e)}")

def show_deal_sourcing(alerts_system):
    """Deal sourcing and alerts interface"""
    st.header("🚨 Deal Sourcing & Alerts")
    
    alerts_system.create_alert_interface()

def show_target_screening():
    """Target screening with multi-criteria filtering"""
    st.header("🎯 Target Screening & Identification")
    
    # Multi-criteria search
    st.subheader("🔍 Multi-Criteria Search")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Industry Filters**")
        industries = st.multiselect(
            "Select Industries",
            ["Technology", "Healthcare", "Finance", "Manufacturing", "Energy", "Retail"],
            key="screening_industries"
        )
        
        st.write("**Geography Filters**")
        geographies = st.multiselect(
            "Select Regions", 
            ["North America", "Europe", "Asia Pacific", "Emerging Markets"],
            key="screening_geo"
        )
    
    with col2:
        st.write("**Financial Thresholds**")
        min_revenue = st.number_input("Min Revenue ($M)", min_value=0, value=0)
        max_revenue = st.number_input("Max Revenue ($M)", min_value=0, value=1000)
        
        min_deal_size = st.number_input("Min Deal Size ($M)", min_value=0, value=0)
        max_deal_size = st.number_input("Max Deal Size ($M)", min_value=0, value=500)
    
    with col3:
        st.write("**Other Filters**")
        index_inclusion = st.selectbox(
            "Index Membership",
            ["Any", "S&P 500", "FTSE 100", "DAX", "Nikkei 225"]
        )
        
        company_tags = st.multiselect(
            "Company Tags",
            ["Potential Target", "Active Acquirer", "Recent Transaction"]
        )
    
    # Search button
    if st.button("🔍 Search Targets"):
        results = search_companies_with_filters({
            'industries': industries,
            'geographies': geographies,
            'min_revenue': min_revenue,
            'max_revenue': max_revenue,
            'index_inclusion': index_inclusion,
            'tags': company_tags
        })
        
        if not results.empty:
            st.success(f"Found {len(results)} matching companies")
            
            # Display results
            st.subheader("Search Results")
            
            # Add tagging functionality
            selected_companies = st.multiselect(
                "Select companies to tag:",
                results['company_name'].tolist() if 'company_name' in results.columns else []
            )
            
            if selected_companies:
                col1, col2 = st.columns(2)
                with col1:
                    new_tag = st.selectbox("Add Tag", ["Potential Target", "Active Acquirer", "Watch"])
                with col2:
                    if st.button("Apply Tag"):
                        # Apply tags to selected companies
                        apply_company_tags(selected_companies, new_tag)
                        st.success(f"Tagged {len(selected_companies)} companies as '{new_tag}'")
            
            st.dataframe(results, use_container_width=True)
        else:
            st.info("No companies match the selected criteria")
    
    # Recent transactions for selected companies
    st.subheader("📊 Transaction History")
    company_name = st.text_input("Enter company name to view transaction history")
    
    if company_name:
        history = get_company_transaction_history(company_name)
        if not history.empty:
            st.dataframe(history, use_container_width=True)
        else:
            st.info(f"No transaction history found for {company_name}")

def search_companies_with_filters(filters: dict) -> pd.DataFrame:
    """Search companies with applied filters"""
    try:
        conn = sqlite3.connect("market_intelligence.db")
        
        query = "SELECT * FROM companies WHERE 1=1"
        params = []
        
        if filters.get('industries'):
            placeholders = ','.join(['?' for _ in filters['industries']])
            query += f" AND industry IN ({placeholders})"
            params.extend(filters['industries'])
        
        if filters.get('min_revenue', 0) > 0:
            query += " AND revenue >= ?"
            params.append(filters['min_revenue'])
            
        if filters.get('max_revenue', 0) > 0:
            query += " AND revenue <= ?"
            params.append(filters['max_revenue'])
        
        if filters.get('index_inclusion') and filters['index_inclusion'] != 'Any':
            query += " AND index_membership LIKE ?"
            params.append(f"%{filters['index_inclusion']}%")
        
        query += " ORDER BY market_cap DESC LIMIT 50"
        
        df = pd.read_sql(query, conn, params=params)
        conn.close()
        
        return df
        
    except Exception as e:
        st.error(f"Error searching companies: {str(e)}")
        return pd.DataFrame()

def apply_company_tags(company_names: list, tag: str):
    """Apply tags to selected companies"""
    try:
        conn = sqlite3.connect("market_intelligence.db")
        cursor = conn.cursor()
        
        for company_name in company_names:
            # Get existing tags
            existing_tags = cursor.execute(
                "SELECT tags FROM companies WHERE company_name = ?", 
                (company_name,)
            ).fetchone()
            
            if existing_tags and existing_tags[0]:
                current_tags = existing_tags[0].split(',')
                if tag not in current_tags:
                    new_tags = ','.join(current_tags + [tag])
                else:
                    new_tags = existing_tags[0]
            else:
                new_tags = tag
            
            cursor.execute(
                "UPDATE companies SET tags = ? WHERE company_name = ?",
                (new_tags, company_name)
            )
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        st.error(f"Error applying tags: {str(e)}")

def get_company_transaction_history(company_name: str) -> pd.DataFrame:
    """Get transaction history for a company"""
    try:
        conn = sqlite3.connect("market_intelligence.db")
        
        query = """
            SELECT target_name, acquirer_name, deal_value, deal_type, 
                   announcement_date, status
            FROM deals 
            WHERE target_name LIKE ? OR acquirer_name LIKE ?
            ORDER BY announcement_date DESC
        """
        
        df = pd.read_sql(query, conn, params=[f"%{company_name}%", f"%{company_name}%"])
        conn.close()
        
        return df
        
    except Exception as e:
        st.error(f"Error loading transaction history: {str(e)}")
        return pd.DataFrame()

def show_watchlist():
    """Watchlist functionality"""
    st.header("📋 Watchlist Management")
    
    # Add to watchlist
    st.subheader("➕ Add to Watchlist")
    
    col1, col2 = st.columns(2)
    
    with col1:
        entity_type = st.selectbox("Type", ["Company", "Deal"])
        entity_name = st.text_input("Name")
        
    with col2:
        notes = st.text_area("Notes")
        
        if st.button("Add to Watchlist"):
            if add_to_watchlist(entity_type, entity_name, notes):
                st.success(f"Added {entity_name} to watchlist")
    
    # Display watchlist
    st.subheader("👁️ Current Watchlist")
    display_watchlist()

def add_to_watchlist(entity_type: str, entity_name: str, notes: str) -> bool:
    """Add item to watchlist"""
    try:
        conn = sqlite3.connect("market_intelligence.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO watchlist (user_id, entity_type, entity_name, notes)
            VALUES (?, ?, ?, ?)
        """, ("demo_user", entity_type, entity_name, notes))
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        st.error(f"Error adding to watchlist: {str(e)}")
        return False

def display_watchlist():
    """Display current watchlist"""
    try:
        conn = sqlite3.connect("market_intelligence.db")
        
        df = pd.read_sql("""
            SELECT entity_type, entity_name, notes, added_date
            FROM watchlist
            WHERE user_id = ?
            ORDER BY added_date DESC
        """, conn, params=["demo_user"])
        
        conn.close()
        
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Your watchlist is empty")
            
    except Exception as e:
        st.error(f"Error loading watchlist: {str(e)}")

def show_due_diligence():
    """Due diligence light features"""
    st.header("🔍 Due Diligence Light")
    
    company_name = st.text_input("Enter company name for due diligence check")
    
    if company_name:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📄 Recent Filings")
            show_company_filings(company_name)
        
        with col2:
            st.subheader("🚩 Red Flags")
            show_red_flags(company_name)
        
        st.subheader("📈 Deal Facts")
        show_deal_facts(company_name)

def show_company_filings(company_name: str):
    """Show recent filings for a company"""
    try:
        conn = sqlite3.connect("market_intelligence.db")
        
        df = pd.read_sql("""
            SELECT filing_type, filing_date, red_flags, deal_mentions
            FROM filings
            WHERE company_name LIKE ?
            ORDER BY filing_date DESC
            LIMIT 10
        """, conn, params=[f"%{company_name}%"])
        
        conn.close()
        
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No filings found")
            
    except Exception as e:
        st.error(f"Error loading filings: {str(e)}")

def show_red_flags(company_name: str):
    """Show red flags for a company"""
    try:
        conn = sqlite3.connect("market_intelligence.db")
        
        df = pd.read_sql("""
            SELECT red_flags, filing_date, filing_type
            FROM filings
            WHERE company_name LIKE ? AND red_flags IS NOT NULL AND red_flags != ''
            ORDER BY filing_date DESC
        """, conn, params=[f"%{company_name}%"])
        
        conn.close()
        
        if not df.empty:
            for _, row in df.iterrows():
                st.warning(f"**{row['filing_type']}** ({row['filing_date']}): {row['red_flags']}")
        else:
            st.success("No red flags identified")
            
    except Exception as e:
        st.error(f"Error loading red flags: {str(e)}")

def show_deal_facts(company_name: str):
    """Show deal facts for a company"""
    try:
        conn = sqlite3.connect("market_intelligence.db")
        
        df = pd.read_sql("""
            SELECT target_name, acquirer_name, deal_value, deal_type, 
                   announcement_date, status
            FROM deals
            WHERE target_name LIKE ? OR acquirer_name LIKE ?
            ORDER BY announcement_date DESC
        """, conn, params=[f"%{company_name}%", f"%{company_name}%"])
        
        conn.close()
        
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No deal history found")
            
    except Exception as e:
        st.error(f"Error loading deal facts: {str(e)}")

def show_market_analysis():
    """Market analysis with heatmaps and trends"""
    st.header("📈 Market Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌍 Regional Activity Heatmap")
        show_regional_heatmap()
    
    with col2:
        st.subheader("🏭 Sector Activity")
        show_sector_analysis()
    
    st.subheader("📊 Market Trends")
    show_market_trends()

def show_regional_heatmap():
    """Show regional deal activity heatmap"""
    # Placeholder implementation
    regions = ['North America', 'Europe', 'Asia Pacific', 'Latin America', 'Middle East']
    activity = np.random.randint(5, 50, len(regions))
    
    df = pd.DataFrame({'Region': regions, 'Deal Count': activity})
    
    fig = px.bar(df, x='Region', y='Deal Count', title='Deal Activity by Region')
    st.plotly_chart(fig, use_container_width=True)

def show_sector_analysis():
    """Show sector analysis"""
    sectors = ['Technology', 'Healthcare', 'Finance', 'Energy', 'Manufacturing']
    values = np.random.randint(10, 100, len(sectors))
    
    fig = px.pie(values=values, names=sectors, title='Deal Distribution by Sector')
    st.plotly_chart(fig, use_container_width=True)

def show_market_trends():
    """Show market trends over time"""
    dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='M')
    trend_data = pd.DataFrame({
        'Date': dates,
        'Deal Volume': np.random.randint(20, 80, len(dates)),
        'Average Deal Size': np.random.uniform(50, 150, len(dates))
    })
    
    fig = px.line(trend_data, x='Date', y=['Deal Volume', 'Average Deal Size'],
                  title='Market Trends Over Time')
    st.plotly_chart(fig, use_container_width=True)

def show_export_reports():
    """Export and reporting functionality"""
    st.header("📤 Export & Reports")
    
    st.subheader("📊 Generate Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        report_type = st.selectbox(
            "Report Type",
            ["Deal Summary", "Market Analysis", "Company Profiles", "Alert Summary"]
        )
        
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=30), datetime.now())
        )
    
    with col2:
        export_format = st.selectbox("Export Format", ["CSV", "Excel", "PDF"])
        
        include_charts = st.checkbox("Include Charts")
    
    if st.button("Generate Report"):
        generate_report(report_type, date_range, export_format, include_charts)

def generate_report(report_type: str, date_range: tuple, format_type: str, include_charts: bool):
    """Generate and download report"""
    try:
        conn = sqlite3.connect("market_intelligence.db")
        
        if report_type == "Deal Summary":
            query = """
                SELECT * FROM deals 
                WHERE announcement_date BETWEEN ? AND ?
                ORDER BY announcement_date DESC
            """
            df = pd.read_sql(query, conn, params=[date_range[0], date_range[1]])
        
        elif report_type == "Market Analysis":
            query = """
                SELECT industry, COUNT(*) as deal_count, 
                       AVG(deal_value) as avg_deal_size
                FROM deals 
                WHERE announcement_date BETWEEN ? AND ?
                GROUP BY industry
            """
            df = pd.read_sql(query, conn, params=[date_range[0], date_range[1]])
        
        conn.close()
        
        if not df.empty:
            if format_type == "CSV":
                csv_data = df.to_csv(index=False)
                st.download_button(
                    f"Download {report_type} Report",
                    csv_data,
                    f"{report_type.lower().replace(' ', '_')}_report.csv",
                    "text/csv"
                )
            elif format_type == "Excel":
                # Convert to Excel format
                from io import BytesIO
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, sheet_name='Report', index=False)
                output.seek(0)
                
                st.download_button(
                    f"Download {report_type} Report",
                    output.getvalue(),
                    f"{report_type.lower().replace(' ', '_')}_report.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            st.success(f"Generated {report_type} report with {len(df)} records")
            st.dataframe(df.head(10), use_container_width=True)
        else:
            st.warning("No data available for the selected criteria")
            
    except Exception as e:
        st.error(f"Error generating report: {str(e)}")

if __name__ == "__main__":
    main()