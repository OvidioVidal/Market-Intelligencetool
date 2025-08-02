#!/usr/bin/env python3
"""
Performance monitoring and testing script for M&A Market Intelligence Tool
"""

import time
import sqlite3
import subprocess
import psutil
import os
from pathlib import Path

def measure_app_startup():
    """Measure application startup time"""
    print("🚀 Testing Application Startup Performance")
    print("=" * 50)
    
    # Test database initialization
    start_time = time.time()
    try:
        from enhanced_data_ingestion import EnhancedDataIngestion
        data_ingestion = EnhancedDataIngestion(auto_init=False)  # Don't auto-init
        init_time = time.time() - start_time
        print(f"✅ Data ingestion import: {init_time:.3f}s")
    except Exception as e:
        print(f"❌ Data ingestion import failed: {e}")
        return False
    
    # Test database connection
    start_time = time.time()
    try:
        conn = sqlite3.connect("market_intelligence.db")
        conn.close()
        db_time = time.time() - start_time
        print(f"✅ Database connection: {db_time:.3f}s")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
    
    # Test alert system
    start_time = time.time()
    try:
        from deal_sourcing_alerts import DealSourcingAlerts
        alerts = DealSourcingAlerts()
        alert_time = time.time() - start_time
        print(f"✅ Alert system import: {alert_time:.3f}s")
    except Exception as e:
        print(f"❌ Alert system import failed: {e}")
    
    return True

def test_database_performance():
    """Test database query performance"""
    print("\n📊 Testing Database Performance")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect("market_intelligence.db")
        
        # Test simple count query
        start_time = time.time()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM deals")
        result = cursor.fetchone()
        query_time = time.time() - start_time
        print(f"✅ Simple count query: {query_time:.3f}s ({result[0]} records)")
        
        # Test complex join query
        start_time = time.time()
        cursor.execute("""
            SELECT d.industry, COUNT(*) as count, AVG(d.deal_value) as avg_value
            FROM deals d
            GROUP BY d.industry
            LIMIT 10
        """)
        results = cursor.fetchall()
        complex_query_time = time.time() - start_time
        print(f"✅ Complex aggregation query: {complex_query_time:.3f}s ({len(results)} industries)")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database performance test failed: {e}")
        return False

def check_system_resources():
    """Check system resources"""
    print("\n💻 System Resources")
    print("=" * 50)
    
    # Memory usage
    memory = psutil.virtual_memory()
    print(f"Memory Usage: {memory.percent}% ({memory.used // (1024**2)}MB / {memory.total // (1024**2)}MB)")
    
    # CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"CPU Usage: {cpu_percent}%")
    
    # Disk usage for current directory
    disk = psutil.disk_usage('.')
    print(f"Disk Usage: {disk.percent}% ({disk.used // (1024**2)}MB / {disk.total // (1024**2)}MB)")
    
    # Database file size
    db_path = Path("market_intelligence.db")
    if db_path.exists():
        db_size = db_path.stat().st_size / (1024**2)  # MB
        print(f"Database Size: {db_size:.2f}MB")

def optimize_database():
    """Optimize database for better performance"""
    print("\n🔧 Database Optimization")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect("market_intelligence.db")
        cursor = conn.cursor()
        
        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_deals_industry ON deals(industry)",
            "CREATE INDEX IF NOT EXISTS idx_deals_announcement_date ON deals(announcement_date)",
            "CREATE INDEX IF NOT EXISTS idx_deals_status ON deals(status)",
            "CREATE INDEX IF NOT EXISTS idx_deals_value ON deals(deal_value)",
            "CREATE INDEX IF NOT EXISTS idx_companies_industry ON companies(industry)",
            "CREATE INDEX IF NOT EXISTS idx_filings_company ON filings(company_name)",
            "CREATE INDEX IF NOT EXISTS idx_filings_date ON filings(filing_date)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
            print(f"✅ Created index: {index_sql.split()[-1]}")
        
        # Vacuum database
        cursor.execute("VACUUM")
        print("✅ Database vacuumed")
        
        # Analyze for query optimization
        cursor.execute("ANALYZE")
        print("✅ Database analyzed")
        
        conn.commit()
        conn.close()
        
        print("🎉 Database optimization completed")
        return True
        
    except Exception as e:
        print(f"❌ Database optimization failed: {e}")
        return False

def generate_performance_report():
    """Generate performance report"""
    print("\n📋 Performance Report")
    print("=" * 50)
    
    report = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'database_exists': Path("market_intelligence.db").exists(),
        'app_files_present': all(Path(f).exists() for f in [
            'optimized_main_app.py', 'main_app.py', 'enhanced_data_ingestion.py'
        ])
    }
    
    # Test import times
    modules_to_test = [
        'streamlit', 'pandas', 'plotly.express', 'sqlite3'
    ]
    
    for module in modules_to_test:
        start_time = time.time()
        try:
            __import__(module)
            import_time = time.time() - start_time
            report[f'{module}_import_time'] = f"{import_time:.3f}s"
            print(f"✅ {module}: {import_time:.3f}s")
        except ImportError:
            report[f'{module}_import_time'] = "FAILED"
            print(f"❌ {module}: Import failed")
    
    return report

def main():
    """Main performance testing function"""
    print("🏢 M&A Market Intelligence Tool - Performance Monitor")
    print("=" * 60)
    
    # Run all tests
    tests = [
        ("Startup Performance", measure_app_startup),
        ("Database Performance", test_database_performance),
        ("Database Optimization", optimize_database)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results[test_name] = False
    
    # System resources
    check_system_resources()
    
    # Generate report
    report = generate_performance_report()
    
    # Summary
    print(f"\n🎯 Performance Summary")
    print("=" * 60)
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 All performance optimizations successful!")
        print("\n💡 Recommendations:")
        print("- Use 'python run.py' to start the optimized application")
        print("- Database indexes created for better query performance")
        print("- Caching enabled to reduce redundant queries")
    else:
        print("⚠️  Some optimizations failed. Check the logs above.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)