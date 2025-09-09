"""
MCP Client Example - Demonstrates how to interact with Turerez MCP Server
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List

try:
    from mcp.client import Client
    from mcp.client.stdio import stdio_client
    from mcp.types import TextContent
except ImportError:
    print("MCP client libraries not available. This is a demo client.")

class TurezMCPClient:
    """
    Example MCP client for interacting with Turerez automation server
    """
    
    def __init__(self, server_command: List[str] = None):
        self.server_command = server_command or ["python", "src/mcp/server.py"]
        self.client = None
        self.connected = False
    
    async def connect(self):
        """Connect to the MCP server"""
        try:
            # In a real implementation, this would connect to the actual MCP server
            print(f"🔌 Connecting to Turerez MCP Server...")
            print(f"📡 Server command: {' '.join(self.server_command)}")
            
            # Simulate connection
            await asyncio.sleep(1)
            self.connected = True
            print("✅ Connected to Turerez MCP Server")
            
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            self.connected = False
    
    async def disconnect(self):
        """Disconnect from the MCP server"""
        if self.connected:
            print("🔌 Disconnecting from server...")
            self.connected = False
            print("✅ Disconnected")
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools"""
        if not self.connected:
            await self.connect()
        
        # Simulated tool list (would come from actual server)
        tools = [
            {
                "name": "extract_chats",
                "description": "Extract chat messages from Internshala conversations",
                "parameters": ["limit", "export_format", "include_analytics"]
            },
            {
                "name": "search_internships",
                "description": "Search and scrape internships from Internshala", 
                "parameters": ["category", "location", "stipend_min", "duration", "limit"]
            },
            {
                "name": "analyze_market",
                "description": "Perform comprehensive market analysis on internship data",
                "parameters": ["analysis_type", "data_source"]
            },
            {
                "name": "export_data",
                "description": "Export data with advanced analytics and visualizations",
                "parameters": ["data_type", "format", "analytics_level", "include_charts"]
            },
            {
                "name": "browser_control",
                "description": "Control browser automation",
                "parameters": ["action", "headless"]
            },
            {
                "name": "get_recommendations",
                "description": "Get AI-powered recommendations",
                "parameters": ["recommendation_type", "user_profile"]
            }
        ]
        
        print("🛠️  Available Tools:")
        for tool in tools:
            print(f"   • {tool['name']}: {tool['description']}")
        
        return tools
    
    async def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources"""
        if not self.connected:
            await self.connect()
        
        resources = [
            {
                "uri": "turerez://config",
                "name": "Turerez Configuration",
                "description": "Current configuration settings"
            },
            {
                "uri": "turerez://status",
                "name": "Server Status", 
                "description": "Current server and browser status"
            },
            {
                "uri": "turerez://exports",
                "name": "Export History",
                "description": "Recent export operations"
            }
        ]
        
        print("📄 Available Resources:")
        for resource in resources:
            print(f"   • {resource['uri']}: {resource['name']}")
        
        return resources
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> str:
        """Call a tool on the server"""
        if not self.connected:
            await self.connect()
        
        arguments = arguments or {}
        
        print(f"🔧 Calling tool: {tool_name}")
        print(f"📝 Arguments: {json.dumps(arguments, indent=2)}")
        
        # Simulate tool call results
        if tool_name == "extract_chats":
            result = {
                "messages": [
                    {
                        "id": "msg_1",
                        "sender": "TechCorp HR",
                        "content": "Thank you for your application!",
                        "timestamp": datetime.now().isoformat()
                    }
                ],
                "analytics": {
                    "total_conversations": 15,
                    "response_rate": 0.65,
                    "avg_response_time": "2.3 hours"
                },
                "metadata": {
                    "total_messages": 1,
                    "extracted_at": datetime.now().isoformat()
                }
            }
        
        elif tool_name == "search_internships":
            result = {
                "internships": [
                    {
                        "title": "Software Development Intern",
                        "company": "TechStartup Inc",
                        "location": "Bangalore",
                        "stipend": "₹15,000/month",
                        "duration": "3 months"
                    }
                ],
                "metadata": {
                    "total_found": 1,
                    "searched_at": datetime.now().isoformat()
                }
            }
        
        elif tool_name == "analyze_market":
            result = {
                "analysis_type": arguments.get("analysis_type", "comprehensive"),
                "insights": {
                    "top_skills": {
                        "Python": 85,
                        "JavaScript": 72,
                        "SQL": 68
                    },
                    "average_stipend": 12500,
                    "top_locations": {
                        "Bangalore": 45,
                        "Mumbai": 32,
                        "Remote": 25
                    }
                }
            }
        
        elif tool_name == "browser_control":
            action = arguments.get("action", "status")
            result = f"Browser {action} completed successfully"
        
        else:
            result = f"Tool {tool_name} executed with arguments: {arguments}"
        
        print(f"✅ Tool result:")
        if isinstance(result, dict):
            print(json.dumps(result, indent=2, default=str))
        else:
            print(result)
        
        return json.dumps(result, default=str) if isinstance(result, dict) else str(result)
    
    async def read_resource(self, uri: str) -> str:
        """Read a resource from the server"""
        if not self.connected:
            await self.connect()
        
        print(f"📖 Reading resource: {uri}")
        
        if uri == "turerez://config":
            resource_data = {
                "browser_settings": {
                    "headless": True,
                    "timeout": 30,
                    "user_agent": "Turerez/1.0.0"
                },
                "export_settings": {
                    "default_format": "excel",
                    "include_analytics": True
                }
            }
        elif uri == "turerez://status":
            resource_data = {
                "server_status": "running",
                "browser_status": "connected",
                "last_activity": datetime.now().isoformat()
            }
        elif uri == "turerez://exports":
            resource_data = {
                "recent_exports": [
                    {
                        "file": "chat_export_2024.xlsx",
                        "timestamp": datetime.now().isoformat(),
                        "type": "chat_data"
                    }
                ]
            }
        else:
            resource_data = {"error": f"Unknown resource: {uri}"}
        
        result = json.dumps(resource_data, indent=2, default=str)
        print(f"📄 Resource content:\n{result}")
        return result

async def demo_workflow():
    """Demonstrate a complete workflow using the MCP client"""
    client = TurezMCPClient()
    
    print("🚀 Turerez MCP Client Demo")
    print("=" * 50)
    
    try:
        # Connect and explore
        await client.connect()
        print()
        
        # List available tools and resources
        await client.list_tools()
        print()
        await client.list_resources()
        print()
        
        # Read server status
        await client.read_resource("turerez://status")
        print()
        
        # Demonstrate tool calls
        print("🔧 Demonstrating Tool Calls:")
        print("-" * 30)
        
        # 1. Control browser
        await client.call_tool("browser_control", {"action": "connect", "headless": True})
        print()
        
        # 2. Extract chats
        await client.call_tool("extract_chats", {
            "limit": 10,
            "export_format": "json",
            "include_analytics": True
        })
        print()
        
        # 3. Search internships
        await client.call_tool("search_internships", {
            "category": "Computer Science",
            "location": ["Bangalore", "Remote"],
            "stipend_min": 10000,
            "limit": 5
        })
        print()
        
        # 4. Analyze market
        await client.call_tool("analyze_market", {
            "analysis_type": "comprehensive"
        })
        print()
        
        # 5. Export data
        await client.call_tool("export_data", {
            "data_type": "combined",
            "format": "excel",
            "analytics_level": "comprehensive",
            "include_charts": True
        })
        print()
        
        # 6. Get recommendations
        await client.call_tool("get_recommendations", {
            "recommendation_type": "application_strategy",
            "user_profile": {
                "skills": ["Python", "JavaScript"],
                "experience_level": "intermediate"
            }
        })
        print()
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
    
    finally:
        await client.disconnect()
        print("\n🎯 Demo completed!")

if __name__ == "__main__":
    print("Turerez MCP Client - Interactive Demo")
    print("This demonstrates how external applications can interact with Turerez via MCP")
    print()
    
    asyncio.run(demo_workflow())
