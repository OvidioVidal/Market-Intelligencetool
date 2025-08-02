#!/usr/bin/env python3
"""
Unified startup script for M&A Market Intelligence Tool
Handles initialization and launches the Streamlit application
"""

import subprocess
import sys
import os
from pathlib import Path
import sqlite3

def check_database():
    """Check if database exists and is properly initialized"""
    db_path = Path("market_intelligence.db")
    
    if not db_path.exists():
        print("🔧 Database not found. Initializing...")
        return False
    
    try:
        # Check if required tables exist
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        conn.close()
        
        required_tables = ['deals', 'companies', 'filings', 'alerts', 'watchlist']
        missing_tables = [table for table in required_tables if table not in tables]
        
        if missing_tables:
            print(f"⚠️  Missing database tables: {missing_tables}")
            return False
        
        print("✅ Database properly initialized")
        return True
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

def initialize_app():
    """Initialize the application"""
    print("🏢 M&A Market Intelligence Tool")
    print("=" * 50)
    
    # Check Python version
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor} compatible")
    else:
        print(f"⚠️  Python {version.major}.{version.minor} detected. Recommend 3.8+")
    
    # Check if dependencies are installed
    try:
        import streamlit
        import pandas
        import plotly
        print("✅ Required packages available")
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Installing requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Initialize database if needed
    if not check_database():
        print("🔧 Setting up database...")
        try:
            from enhanced_data_ingestion import EnhancedDataIngestion
            data_ingestion = EnhancedDataIngestion()
            print("✅ Database initialized successfully")
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            return False
    
    return True

def start_streamlit():
    """Start the Streamlit application"""
    print("\n🚀 Starting Market Intelligence Tool...")
    print("📍 Application will be available at: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the application\n")
    
    try:
        # Start Streamlit with main_app.py
        subprocess.run(["streamlit", "run", "main_app.py", "--server.port", "8501"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except FileNotFoundError:
        print("❌ Streamlit not found. Please install with: pip install streamlit")
        return False
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        return False
    
    return True

def main():
    """Main entry point"""
    # Check if we're in the right directory
    required_files = ['main_app.py', 'enhanced_data_ingestion.py', 'requirements.txt']
    missing_files = [f for f in required_files if not Path(f).exists()]
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        print("Please ensure you're in the correct project directory")
        return False
    
    # Initialize application
    if not initialize_app():
        print("❌ Application initialization failed")
        return False
    
    # Start Streamlit
    return start_streamlit()

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)