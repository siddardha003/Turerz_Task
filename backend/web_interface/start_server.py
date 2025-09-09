#!/usr/bin/env python3
"""
Turerez Web Interface Startup Script
Starts the FastAPI web server with MCP integration
"""

import sys
import os
import subprocess
from pathlib import Path

def install_dependencies():
    """Install web interface dependencies"""
    print("🔧 Installing web interface dependencies...")
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "-r", str(requirements_file)
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_backend_dependencies():
    """Check if backend dependencies are available"""
    try:
        # Add backend to path
        backend_path = Path(__file__).parent.parent
        sys.path.insert(0, str(backend_path))
        
        # Test imports
        from src.config import config
        from src.mcp.server import TurezMCPServer
        print("✅ Backend dependencies available")
        return True
    except ImportError as e:
        print(f"❌ Backend dependencies missing: {e}")
        print("💡 Make sure to run this from the backend directory")
        return False

def start_web_server():
    """Start the FastAPI web server"""
    print("🚀 Starting Turerez Web Interface...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📖 API documentation at: http://localhost:8000/docs")
    print("⏹️  Press Ctrl+C to stop the server")
    
    try:
        import uvicorn
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

def main():
    """Main startup function"""
    print("🌟 Turerez Web Interface Startup")
    print("=" * 50)
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    if not (current_dir / "app.py").exists():
        print("❌ Please run this script from the web_interface directory")
        print(f"📂 Current directory: {current_dir}")
        print("💡 Expected: .../backend/web_interface/")
        return
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Dependency installation failed")
        return
    
    # Check backend
    if not check_backend_dependencies():
        print("❌ Backend dependencies not available")
        print("💡 Make sure you're in the backend directory structure")
        return
    
    # Start server
    start_web_server()

if __name__ == "__main__":
    main()
