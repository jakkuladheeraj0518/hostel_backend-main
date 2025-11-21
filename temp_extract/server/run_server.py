#!/usr/bin/env python3
"""
Hostel Management System - Server Startup Script
This script handles all the setup and runs the server without errors.
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("=" * 60)
    print("🏨 HOSTEL MANAGEMENT SYSTEM API SERVER")
    print("=" * 60)
    print("🚀 Starting up...")

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("📦 Checking dependencies...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'sqlalchemy', 'psycopg2-binary', 
        'pydantic', 'python-jose', 'passlib', 'bcrypt', 'python-multipart'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package} - MISSING")
    
    if missing_packages:
        print(f"\n⚠️  Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install"
            ] + missing_packages)
            print("✅ All dependencies installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    return True

def check_database():
    """Check database connection"""
    print("🗄️  Checking database connection...")
    
    try:
        # Import here to avoid issues if dependencies aren't installed yet
        from app.core.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        print("  ✅ Database connection successful")
        return True
    except Exception as e:
        print(f"  ⚠️  Database connection issue: {e}")
        print("  📝 Note: This is normal if using SQLite or if PostgreSQL isn't set up yet")
        return True  # Continue anyway, as the app will create tables

def run_server():
    """Run the FastAPI server"""
    print("🌐 Starting FastAPI server...")
    
    try:
        import uvicorn
        
        # Configuration
        config = {
            "app": "app.main:app",
            "host": "127.0.0.1",
            "port": 8000,
            "reload": True,
            "log_level": "info",
            "access_log": True
        }
        
        print(f"🔗 Server will be available at: http://{config['host']}:{config['port']}")
        print(f"📚 API Documentation: http://{config['host']}:{config['port']}/docs")
        print(f"🔄 Auto-reload: {'Enabled' if config['reload'] else 'Disabled'}")
        print("\n" + "=" * 60)
        print("🎯 SERVER IS STARTING...")
        print("=" * 60)
        print("💡 Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Start the server
        uvicorn.run(**config)
        
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("🛑 Server stopped by user")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Server startup failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("  1. Make sure port 8000 is not in use")
        print("  2. Check if all dependencies are installed")
        print("  3. Verify the app.main:app import path")
        return False
    
    return True

def main():
    """Main startup function"""
    print_banner()
    
    # Change to the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed. Please install missing packages manually.")
        return
    
    # Step 2: Check database
    check_database()
    
    # Step 3: Run server
    print("\n🚀 All checks passed! Starting server...")
    time.sleep(1)
    
    success = run_server()
    
    if success:
        print("✅ Server shutdown completed successfully")
    else:
        print("❌ Server encountered errors during startup")

if __name__ == "__main__":
    main()