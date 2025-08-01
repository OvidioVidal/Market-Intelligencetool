#!/usr/bin/env python3
"""
Simple setup script for M&A Market Intelligence Tool
This installs dependencies and prepares the application for use
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    print("This may take a few minutes...")
    
    try:
        # Upgrade pip first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        print("\n💡 Try manually installing with:")
        print("   pip install streamlit pandas plotly openpyxl xlsxwriter")
        return False

def main():
    print("🏢 M&A Market Intelligence Tool - Setup")
    print("=" * 50)
    print("\n🔧 This will install all required Python packages")
    
    # Check Python version
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor} is compatible")
    else:
        print(f"⚠️  Python {version.major}.{version.minor} detected. Python 3.8+ recommended")
    
    # Install requirements
    if install_requirements():
        print("\n🎉 Setup completed successfully!")
        print("\n🚀 To start the application:")
        print("   streamlit run main_app.py")
        print("\n🌐 The app will open at: http://localhost:8501")
        print("\n📚 See README.md for usage instructions")
    else:
        print("\n❌ Setup failed. Please install packages manually.")

if __name__ == "__main__":
    main()