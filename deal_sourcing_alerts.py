import pandas as pd
import numpy as np
import streamlit as st
import sqlite3
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from dataclasses import dataclass

@dataclass
class Alert:
    id: int
    user_id: str
    alert_name: str
    keywords: List[str]
    filters: Dict
    email_notifications: bool
    created_date: datetime
    last_triggered: Optional[datetime] = None

class DealSourcingAlerts:
    """
    Deal sourcing and alert system for keyword-driven detection
    """
    
    def __init__(self, db_path: str = "market_intelligence.db"):
        self.db_path = db_path
        
        # Extended deal keywords with categories
        self.deal_keywords = {
            'acquisition': ['acquisition', 'acquire', 'acquired', 'acquiring', 'takeover', 'buyout'],
            'merger': ['merger', 'merge', 'merging', 'merged', 'combination', 'consolidation'],
            'investment': ['investment', 'invest', 'funding', 'capital', 'round', 'financing'],
            'partnership': ['partnership', 'strategic alliance', 'joint venture', 'collaboration'],
            'divestiture': ['divestiture', 'divest', 'spin-off', 'carve-out', 'disposal', 'sell'],
            'ipo': ['IPO', 'initial public offering', 'going public', 'public listing'],
            'private_equity': ['private equity', 'PE', 'LBO', 'leveraged buyout', 'management buyout'],
            'restructuring': ['restructuring', 'reorganization', 'bankruptcy', 'chapter 11', 'administration']
        }
        
        # Industry-specific keywords
        self.industry_keywords = {
            'technology': ['software', 'AI', 'artificial intelligence', 'fintech', 'saas', 'cloud', 'data'],
            'healthcare': ['pharmaceutical', 'biotech', 'medical device', 'healthcare', 'drug', 'therapy'],
            'finance': ['bank', 'insurance', 'asset management', 'financial services', 'payments'],
            'energy': ['oil', 'gas', 'renewable', 'energy', 'power', 'utilities', 'solar', 'wind'],
            'manufacturing': ['manufacturing', 'industrial', 'automotive', 'aerospace', 'chemicals'],
            'retail': ['retail', 'e-commerce', 'consumer', 'brand', 'fashion', 'food']
        }
        
        # Geography keywords
        self.geography_keywords = {
            'north_america': ['US', 'USA', 'United States', 'Canada', 'Mexico', 'North America'],
            'europe': ['UK', 'Germany', 'France', 'Italy', 'Spain', 'Netherlands', 'Europe', 'EU'],
            'asia_pacific': ['China', 'Japan', 'India', 'Singapore', 'Australia', 'Korea', 'APAC'],
            'emerging_markets': ['Brazil', 'Russia', 'Turkey', 'South Africa', 'emerging']
        }
    
    def create_alert_interface(self):
        """Streamlit interface for creating and managing alerts"""
        st.subheader("🚨 Deal Sourcing Alerts")
        
        # Create new alert section
        with st.expander("Create New Alert", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                alert_name = st.text_input("Alert Name", placeholder="e.g., Tech Acquisitions > $100M")
                
                # Keywords selection
                st.write("**Deal Type Keywords:**")
                selected_deal_types = []
                for deal_type, keywords in self.deal_keywords.items():
                    if st.checkbox(f"{deal_type.replace('_', ' ').title()}", key=f"deal_{deal_type}"):
                        selected_deal_types.extend(keywords)
                
                custom_keywords = st.text_area(
                    "Custom Keywords (one per line)",
                    placeholder="Enter additional keywords..."
                ).split('\n')
                custom_keywords = [kw.strip() for kw in custom_keywords if kw.strip()]
                
                all_keywords = selected_deal_types + custom_keywords
            
            with col2:
                # Filters
                st.write("**Filters:**")
                
                # Industry filter
                selected_industries = st.multiselect(
                    "Industries",
                    list(self.industry_keywords.keys()),
                    format_func=lambda x: x.replace('_', ' ').title()
                )
                
                # Geography filter
                selected_geographies = st.multiselect(
                    "Geographies",
                    list(self.geography_keywords.keys()),
                    format_func=lambda x: x.replace('_', ' ').title()
                )
                
                # Deal size filter
                min_deal_size = st.number_input("Min Deal Size ($M)", min_value=0, value=0)
                max_deal_size = st.number_input("Max Deal Size ($M)", min_value=0, value=1000)
                
                # Notification settings
                email_notifications = st.checkbox("Email Notifications")
                if email_notifications:
                    email_address = st.text_input("Email Address")
            
            # Alert preview
            if all_keywords:
                st.write("**Alert Preview:**")
                st.write(f"Keywords: {', '.join(all_keywords[:10])}{'...' if len(all_keywords) > 10 else ''}")
                st.write(f"Industries: {', '.join(selected_industries) if selected_industries else 'All'}")
                st.write(f"Geographies: {', '.join(selected_geographies) if selected_geographies else 'All'}")
                st.write(f"Deal Size: ${min_deal_size}M - ${max_deal_size}M")
            
            # Create alert button
            if st.button("Create Alert"):
                if alert_name and all_keywords:
                    alert_filters = {
                        'industries': selected_industries,
                        'geographies': selected_geographies,
                        'min_deal_size': min_deal_size,
                        'max_deal_size': max_deal_size,
                        'email_address': email_address if email_notifications else None
                    }
                    
                    result = self.create_alert(
                        user_id="default_user",  # In production, use actual user ID
                        alert_name=alert_name,
                        keywords=all_keywords,
                        filters=alert_filters,
                        email_notifications=email_notifications
                    )
                    
                    if result['success']:
                        st.success("Alert created successfully!")
                    else:
                        st.error(f"Failed to create alert: {result['error']}")
                else:
                    st.error("Please provide alert name and at least one keyword")
        
        # Existing alerts management
        self.display_existing_alerts()
        
        # Test alerts
        self.test_alerts_interface()
    
    def display_existing_alerts(self):
        """Display and manage existing alerts"""
        st.subheader("📋 Existing Alerts")
        
        alerts = self.get_user_alerts("default_user")
        
        if not alerts:
            st.info("No alerts created yet.")
            return
        
        for alert in alerts:
            with st.expander(f"🔔 {alert.alert_name}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Keywords:** {', '.join(alert.keywords[:5])}{'...' if len(alert.keywords) > 5 else ''}")
                    st.write(f"**Created:** {alert.created_date.strftime('%Y-%m-%d')}")
                    st.write(f"**Last Triggered:** {alert.last_triggered.strftime('%Y-%m-%d %H:%M') if alert.last_triggered else 'Never'}")
                
                with col2:
                    filters = alert.filters
                    st.write(f"**Industries:** {', '.join(filters.get('industries', [])) or 'All'}")
                    st.write(f"**Geographies:** {', '.join(filters.get('geographies', [])) or 'All'}")
                    st.write(f"**Deal Size:** ${filters.get('min_deal_size', 0)}M - ${filters.get('max_deal_size', 'Unlimited')}M")
                
                with col3:
                    st.write(f"**Email Notifications:** {'Yes' if alert.email_notifications else 'No'}")
                    
                    col_test, col_delete = st.columns(2)
                    with col_test:
                        if st.button(f"Test Alert", key=f"test_{alert.id}"):
                            matches = self.test_alert(alert)
                            st.success(f"Found {len(matches)} matches!")
                            if matches:
                                st.dataframe(matches[['target_name', 'deal_value', 'announcement_date']].head())
                    
                    with col_delete:
                        if st.button(f"Delete", key=f"delete_{alert.id}"):
                            if self.delete_alert(alert.id):
                                st.success("Alert deleted!")
                                st.rerun()
    
    def test_alerts_interface(self):
        """Interface for testing alerts manually"""
        st.subheader("🧪 Test Alert System")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Run All Alerts"):
                results = self.run_all_alerts()
                st.write("**Alert Results:**")
                for alert_name, matches in results.items():
                    st.write(f"- {alert_name}: {len(matches)} matches")
        
        with col2:
            if st.button("Check Recent Data"):
                recent_deals = self.get_recent_deals(days=7)
                st.write(f"**Recent Deals (Last 7 days):** {len(recent_deals)} deals")
                if len(recent_deals) > 0:
                    st.dataframe(recent_deals[['target_name', 'acquirer_name', 'deal_value', 'announcement_date']].head())
    
    def create_alert(self, user_id: str, alert_name: str, keywords: List[str], 
                    filters: Dict, email_notifications: bool) -> Dict:
        """Create a new alert"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alerts (user_id, alert_name, keywords, filters, email_notifications)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                user_id,
                alert_name,
                json.dumps(keywords),
                json.dumps(filters),
                email_notifications
            ))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'message': 'Alert created successfully'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_user_alerts(self, user_id: str) -> List[Alert]:
        """Get all alerts for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
                SELECT id, user_id, alert_name, keywords, filters, email_notifications,
                       created_date, last_triggered
                FROM alerts
                WHERE user_id = ?
                ORDER BY created_date DESC
            '''
            
            df = pd.read_sql(query, conn, params=[user_id])
            conn.close()
            
            alerts = []
            for _, row in df.iterrows():
                alert = Alert(
                    id=row['id'],
                    user_id=row['user_id'],
                    alert_name=row['alert_name'],
                    keywords=json.loads(row['keywords']),
                    filters=json.loads(row['filters']),
                    email_notifications=bool(row['email_notifications']),
                    created_date=datetime.fromisoformat(row['created_date']),
                    last_triggered=datetime.fromisoformat(row['last_triggered']) if row['last_triggered'] else None
                )
                alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            st.error(f"Error retrieving alerts: {str(e)}")
            return []
    
    def delete_alert(self, alert_id: int) -> bool:
        """Delete an alert"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM alerts WHERE id = ?', (alert_id,))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            st.error(f"Error deleting alert: {str(e)}")
            return False
    
    def test_alert(self, alert: Alert) -> pd.DataFrame:
        """Test an alert against current data"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Base query
            query = '''
                SELECT * FROM deals
                WHERE (
            '''
            
            # Add keyword conditions
            keyword_conditions = []
            for keyword in alert.keywords:
                keyword_conditions.append(f"target_name LIKE '%{keyword}%' OR acquirer_name LIKE '%{keyword}%'")
            
            query += ' OR '.join(keyword_conditions) + ')'
            
            # Add filters
            filters = alert.filters
            
            if filters.get('industries'):
                industry_conditions = [f"industry = '{industry}'" for industry in filters['industries']]
                query += f" AND ({' OR '.join(industry_conditions)})"
            
            if filters.get('min_deal_size', 0) > 0:
                query += f" AND deal_value >= {filters['min_deal_size']}"
            
            if filters.get('max_deal_size'):
                query += f" AND deal_value <= {filters['max_deal_size']}"
            
            # Only recent deals (last 30 days)
            query += " AND announcement_date >= date('now', '-30 days')"
            
            df = pd.read_sql(query, conn)
            conn.close()
            
            return df
            
        except Exception as e:
            st.error(f"Error testing alert: {str(e)}")
            return pd.DataFrame()
    
    def run_all_alerts(self) -> Dict[str, pd.DataFrame]:
        """Run all alerts and return results"""
        results = {}
        
        try:
            # Get all alerts
            conn = sqlite3.connect(self.db_path)
            alerts_df = pd.read_sql('SELECT * FROM alerts', conn)
            conn.close()
            
            for _, alert_row in alerts_df.iterrows():
                alert = Alert(
                    id=alert_row['id'],
                    user_id=alert_row['user_id'],
                    alert_name=alert_row['alert_name'],
                    keywords=json.loads(alert_row['keywords']),
                    filters=json.loads(alert_row['filters']),
                    email_notifications=bool(alert_row['email_notifications']),
                    created_date=datetime.fromisoformat(alert_row['created_date'])
                )
                
                matches = self.test_alert(alert)
                results[alert.alert_name] = matches
                
                # Update last triggered time if matches found
                if len(matches) > 0:
                    self.update_alert_triggered(alert.id)
                    
                    # Send email notification if enabled
                    if alert.email_notifications and alert.filters.get('email_address'):
                        self.send_email_alert(alert, matches)
            
            return results
            
        except Exception as e:
            st.error(f"Error running alerts: {str(e)}")
            return {}
    
    def update_alert_triggered(self, alert_id: int):
        """Update the last triggered timestamp for an alert"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE alerts 
                SET last_triggered = ? 
                WHERE id = ?
            ''', (datetime.now().isoformat(), alert_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Error updating alert timestamp: {str(e)}")
    
    def send_email_alert(self, alert: Alert, matches: pd.DataFrame):
        """Send email notification for alert (placeholder implementation)"""
        # This is a placeholder implementation
        # In production, you would configure SMTP settings and send actual emails
        
        email_address = alert.filters.get('email_address')
        if not email_address:
            return
        
        subject = f"Market Intelligence Alert: {alert.alert_name}"
        
        body = f"""
        Your alert "{alert.alert_name}" has found {len(matches)} new matches:
        
        """
        
        for _, match in matches.head(5).iterrows():
            body += f"• {match.get('target_name', 'N/A')} - {match.get('acquirer_name', 'N/A')} (${match.get('deal_value', 'N/A')}M)\n"
        
        if len(matches) > 5:
            body += f"\n... and {len(matches) - 5} more matches.\n"
        
        body += f"\nLogin to view full details: [Your App URL]\n"
        
        # Log the email (in production, actually send it)
        st.info(f"Email alert would be sent to {email_address}: {subject}")
    
    def get_recent_deals(self, days: int = 7) -> pd.DataFrame:
        """Get deals from the last N days"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = f'''
                SELECT * FROM deals
                WHERE announcement_date >= date('now', '-{days} days')
                ORDER BY announcement_date DESC
            '''
            
            df = pd.read_sql(query, conn)
            conn.close()
            
            return df
            
        except Exception as e:
            st.error(f"Error retrieving recent deals: {str(e)}")
            return pd.DataFrame()
    
    def search_deals_by_keywords(self, keywords: List[str], filters: Dict = None) -> pd.DataFrame:
        """Search deals by keywords with optional filters"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Build search query
            query = 'SELECT * FROM deals WHERE ('
            
            keyword_conditions = []
            for keyword in keywords:
                keyword_conditions.append(f"target_name LIKE '%{keyword}%' OR acquirer_name LIKE '%{keyword}%'")
            
            query += ' OR '.join(keyword_conditions) + ')'
            
            # Apply filters if provided
            if filters:
                if filters.get('industries'):
                    industry_conditions = [f"industry = '{industry}'" for industry in filters['industries']]
                    query += f" AND ({' OR '.join(industry_conditions)})"
                
                if filters.get('min_deal_size', 0) > 0:
                    query += f" AND deal_value >= {filters['min_deal_size']}"
                
                if filters.get('max_deal_size'):
                    query += f" AND deal_value <= {filters['max_deal_size']}"
                
                if filters.get('date_from'):
                    query += f" AND announcement_date >= '{filters['date_from']}'"
                
                if filters.get('date_to'):
                    query += f" AND announcement_date <= '{filters['date_to']}'"
            
            query += ' ORDER BY announcement_date DESC'
            
            df = pd.read_sql(query, conn)
            conn.close()
            
            return df
            
        except Exception as e:
            st.error(f"Error searching deals: {str(e)}")
            return pd.DataFrame()
    
    def get_trending_keywords(self, days: int = 30) -> Dict[str, int]:
        """Get trending keywords from recent deals"""
        try:
            recent_deals = self.get_recent_deals(days)
            
            if recent_deals.empty:
                return {}
            
            # Combine target and acquirer names
            all_text = ' '.join(recent_deals['target_name'].fillna('').astype(str) + ' ' + 
                              recent_deals['acquirer_name'].fillna('').astype(str))
            
            # Count keyword occurrences
            keyword_counts = {}
            all_keywords = []
            
            for category, keywords in self.deal_keywords.items():
                all_keywords.extend(keywords)
            
            for keyword in all_keywords:
                count = len(re.findall(keyword.lower(), all_text.lower()))
                if count > 0:
                    keyword_counts[keyword] = count
            
            # Sort by frequency
            return dict(sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True))
            
        except Exception as e:
            st.error(f"Error getting trending keywords: {str(e)}")
            return {}