#!/usr/bin/env python3
"""
Deployment script for M&A Market Intelligence Tool
"""

import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible. Requires Python 3.8+")
        return False

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def run_tests():
    """Run application tests"""
    print("🧪 Running application tests...")
    try:
        result = subprocess.run([sys.executable, "test_app.py"], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Warnings/Errors:")
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False

def create_sample_data():
    """Create some sample data for demonstration"""
    print("📊 Creating sample demonstration data...")
    try:
        import sqlite3
        import pandas as pd
        from datetime import datetime, timedelta
        import numpy as np
        
        conn = sqlite3.connect("market_intelligence.db")
        
        # Sample deals data
        sample_deals = []
        companies = ['TechCorp', 'HealthPlus', 'FinanceMax', 'ManufactureInc', 'EnergyFlow']
        industries = ['Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Energy']
        
        for i in range(20):
            deal = {
                'deal_id': f'DEMO{i+1:03d}',
                'target_name': f"{companies[i % len(companies)]} {i+1}",
                'acquirer_name': f"Acquirer {i+1}",
                'deal_value': round(np.random.uniform(10, 500), 1),
                'announcement_date': (datetime.now() - timedelta(days=np.random.randint(1, 365))).date(),
                'industry': industries[i % len(industries)],
                'deal_type': np.random.choice(['Acquisition', 'Merger', 'LBO', 'Investment']),
                'status': np.random.choice(['Announced', 'Pending', 'Complete', 'Rumored']),
                'geography': np.random.choice(['North America', 'Europe', 'Asia Pacific']),
                'source': 'Sample Data'
            }
            sample_deals.append(deal)
        
        # Insert sample deals
        df_deals = pd.DataFrame(sample_deals)
        df_deals.to_sql('deals', conn, if_exists='append', index=False)
        
        # Sample companies data
        sample_companies = []
        for i in range(15):
            company = {
                'company_name': f"Sample Company {i+1}",
                'ticker': f"SC{i+1:02d}",
                'industry': industries[i % len(industries)],
                'geography': np.random.choice(['North America', 'Europe', 'Asia Pacific']),
                'market_cap': round(np.random.uniform(100, 10000), 1),
                'revenue': round(np.random.uniform(50, 2000), 1),
                'employees': np.random.randint(100, 5000),
                'index_membership': np.random.choice(['S&P 500', 'FTSE 100', 'None', 'DAX']),
                'tags': '',
                'watchlist': 0
            }
            sample_companies.append(company)
        
        df_companies = pd.DataFrame(sample_companies)
        df_companies.to_sql('companies', conn, if_exists='append', index=False)
        
        conn.close()
        print("✅ Sample data created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create sample data: {e}")
        return False

def start_application():
    """Start the Streamlit application"""
    print("🚀 Starting M&A Market Intelligence Tool...")
    print("📱 The application will open in your default web browser")
    print("🌐 URL: http://localhost:8501")
    print("\n⏹️  To stop the application, press Ctrl+C in this terminal\n")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "main_app.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Failed to start application: {e}")

def main():
    """Main deployment function"""
    print("🏢 M&A Market Intelligence Tool - Deployment Script")
    print("=" * 60)
    
    # Check current directory
    current_dir = Path.cwd()
    required_files = ['main_app.py', 'enhanced_data_ingestion.py', 'deal_sourcing_alerts.py', 'requirements.txt']
    missing_files = [f for f in required_files if not (current_dir / f).exists()]
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        print("Please ensure you're in the correct directory with all application files")
        return False
    
    # Run deployment steps
    steps = [
        ("Checking Python version", check_python_version),
        ("Installing requirements", install_requirements),
        ("Running tests", run_tests),
        ("Creating sample data", create_sample_data)
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if not step_func():
            print(f"❌ Deployment failed at: {step_name}")
            return False
    
    print("\n" + "=" * 60)
    print("🎉 Deployment completed successfully!")
    print("\n🔧 Configuration Notes:")
    print("- SQLite database will be created automatically")
    print("- Sample data has been added for demonstration")
    print("- All modules tested and working")
    
    # Ask user if they want to start the application
    start_now = input("\n🚀 Start the application now? (y/n): ").lower().strip()
    if start_now in ['y', 'yes']:
        start_application()
    else:
        print("\n📝 To start later, run: streamlit run main_app.py")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)