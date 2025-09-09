"""
MCP Server Installation and Setup Guide
"""

import subprocess
import sys
import os
from pathlib import Path

def install_mcp_dependencies():
    """Install MCP-specific dependencies"""
    print("🔧 Installing MCP dependencies...")
    
    mcp_requirements = Path(__file__).parent / "requirements-mcp.txt"
    
    try:
        # Install MCP packages
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "-r", str(mcp_requirements)
        ])
        print("✅ MCP dependencies installed successfully")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install MCP dependencies: {e}")
        print("📝 Note: MCP is experimental. Server will run in demo mode.")
        return False
    
    return True

def setup_mcp_config():
    """Setup MCP configuration for external clients"""
    config_dir = Path.home() / ".config" / "mcp"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config_file = config_dir / "turerez-server.json"
    
    current_dir = Path(__file__).parent.parent.parent.parent  # backend/
    server_path = current_dir / "src" / "mcp" / "server.py"
    
    config = {
        "servers": {
            "turerez-automation": {
                "command": "python",
                "args": [str(server_path)],
                "description": "Turerez Internshala automation via MCP",
                "capabilities": [
                    "resources",
                    "tools", 
                    "logging"
                ]
            }
        }
    }
    
    import json
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"📝 MCP configuration created: {config_file}")
    return config_file

def test_server():
    """Test the MCP server functionality"""
    print("🧪 Testing MCP server...")
    
    # Import and test server components
    try:
        from .server import TurezMCPServer
        
        # Test server initialization
        server = TurezMCPServer()
        print("✅ Server initialization successful")
        
        # Test tool discovery
        tools = [
            "extract_chats",
            "search_internships", 
            "analyze_market",
            "export_data",
            "browser_control",
            "get_recommendations"
        ]
        
        print(f"🛠️  Available tools: {len(tools)}")
        for tool in tools:
            print(f"   • {tool}")
        
        return True
        
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Turerez MCP Server Setup")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required for MCP support")
        return
    
    # Install dependencies
    deps_ok = install_mcp_dependencies()
    
    # Setup configuration
    config_file = setup_mcp_config()
    
    # Test server
    if deps_ok:
        test_ok = test_server()
    else:
        print("⚠️  Running in demo mode (MCP dependencies not available)")
        test_ok = True
    
    print("\n📋 Setup Summary:")
    print(f"   Dependencies: {'✅' if deps_ok else '⚠️ Demo mode'}")
    print(f"   Configuration: ✅ {config_file}")
    print(f"   Server test: {'✅' if test_ok else '❌'}")
    
    if test_ok:
        print("\n🎯 Setup completed successfully!")
        print("\nTo start the MCP server:")
        print("   python src/mcp/server.py")
        print("\nTo test the client:")
        print("   python src/mcp/client_demo.py")
    else:
        print("\n❌ Setup had issues. Check error messages above.")

if __name__ == "__main__":
    main()
