#!/usr/bin/env python3
"""
Test script to verify the M&A Market Intelligence Tool is ready for deployment
"""

import sys
import os
import sqlite3
import pandas as pd
from datetime import datetime

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import plotly.express as px
        print("✅ Plotly imported successfully")
    except ImportError as e:
        print(f"❌ Plotly import failed: {e}")
        return False
    
    try:
        from enhanced_data_ingestion import EnhancedDataIngestion
        print("✅ Enhanced data ingestion module imported successfully")
    except ImportError as e:
        print(f"❌ Enhanced data ingestion import failed: {e}")
        return False
    
    try:
        from deal_sourcing_alerts import DealSourcingAlerts
        print("✅ Deal sourcing alerts module imported successfully")
    except ImportError as e:
        print(f"❌ Deal sourcing alerts import failed: {e}")
        return False
    
    return True

def test_database_setup():
    """Test database initialization"""
    print("\nTesting database setup...")
    
    try:
        from enhanced_data_ingestion import EnhancedDataIngestion
        data_ingestion = EnhancedDataIngestion()
        print("✅ Database initialized successfully")
        
        # Check if tables exist
        conn = sqlite3.connect("market_intelligence.db")
        cursor = conn.cursor()
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        required_tables = ['deals', 'companies', 'filings', 'alerts', 'watchlist']
        missing_tables = [table for table in required_tables if table not in table_names]
        
        if not missing_tables:
            print("✅ All required database tables created")
        else:
            print(f"❌ Missing tables: {missing_tables}")
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def test_sample_data():
    """Test adding and retrieving sample data"""
    print("\nTesting sample data operations...")
    
    try:
        # Add sample deal
        conn = sqlite3.connect("market_intelligence.db")
        cursor = conn.cursor()
        
        sample_deal = {
            'deal_id': 'TEST001',
            'target_name': 'Test Company A',
            'acquirer_name': 'Test Company B',
            'deal_value': 100.0,
            'announcement_date': datetime.now().date(),
            'industry': 'Technology',
            'status': 'Test',
            'source': 'Test Data'
        }
        
        cursor.execute('''
            INSERT OR REPLACE INTO deals 
            (deal_id, target_name, acquirer_name, deal_value, announcement_date, industry, status, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', tuple(sample_deal.values()))
        
        conn.commit()
        
        # Retrieve sample data
        df = pd.read_sql("SELECT * FROM deals WHERE deal_id = 'TEST001'", conn)
        
        if not df.empty:
            print("✅ Sample data added and retrieved successfully")
        else:
            print("❌ Failed to retrieve sample data")
            return False
        
        # Clean up test data
        cursor.execute("DELETE FROM deals WHERE deal_id = 'TEST001'")
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Sample data test failed: {e}")
        return False

def test_alerts_system():
    """Test alerts system initialization"""
    print("\nTesting alerts system...")
    
    try:
        from deal_sourcing_alerts import DealSourcingAlerts
        alerts = DealSourcingAlerts()
        
        # Test getting user alerts (should return empty list for new user)
        user_alerts = alerts.get_user_alerts("test_user")
        print("✅ Alerts system initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Alerts system test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🧪 M&A Market Intelligence Tool - Deployment Test Suite")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("Database Setup", test_database_setup),
        ("Sample Data Operations", test_sample_data),
        ("Alerts System", test_alerts_system)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        if test_func():
            print(f"✅ {test_name} PASSED")
            passed += 1
        else:
            print(f"❌ {test_name} FAILED")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The application is ready for deployment.")
        print("\n🚀 To start the application, run:")
        print("   streamlit run main_app.py")
        return True
    else:
        print("⚠️  Some tests failed. Please fix the issues before deployment.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)