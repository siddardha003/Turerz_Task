"""
MCP Client for Internshala Automation.
Provides a high-level interface for natural language commands.
"""

import asyncio
import json
from typing import Dict, Any, Optional

from src.mcp.nlp import NaturalLanguageProcessor, CommandExecutor, CommandIntent
from src.mcp.fastmcp_server import mcp
from src.utils.logging import get_logger
from src.config import config


logger = get_logger(__name__)


class InternshalaAutomationClient:
    """High-level client for Internshala automation with natural language support."""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.nlp = NaturalLanguageProcessor(openai_api_key)
        self.executor = CommandExecutor()
        self.logger = get_logger(__name__)
    
    async def process_natural_language_command(self, user_input: str) -> Dict[str, Any]:
        """Process a natural language command end-to-end."""
        try:
            self.logger.info(f"Processing command: {user_input}")
            
            # Step 1: Parse the natural language command
            intent = await self.nlp.parse_command(user_input)
            self.logger.info(f"Parsed intent: {intent.action} (confidence: {intent.confidence})")
            
            # Step 2: Validate confidence threshold
            if intent.confidence < 0.5:
                return {
                    "success": False,
                    "error": "Could not understand the command",
                    "suggestion": "Try rephrasing your request. Examples:\n" +
                                "- 'Download chat messages from the last 5 days'\n" +
                                "- 'Search for marketing internships'\n" +
                                "- 'Find messages mentioning stipend above 1000'",
                    "parsed_intent": intent.dict()
                }
            
            # Step 3: Execute the command using MCP tools
            result = await self._execute_mcp_tool(intent)
            
            # Step 4: Return formatted response
            return {
                "success": True,
                "original_command": user_input,
                "parsed_intent": intent.dict(),
                "result": result
            }
            
        except Exception as e:
            self.logger.error(f"Error processing command '{user_input}': {e}")
            return {
                "success": False,
                "error": str(e),
                "original_command": user_input
            }
    
    async def _execute_mcp_tool(self, intent: CommandIntent) -> Dict[str, Any]:
        """Execute MCP tool based on the parsed intent."""
        try:
            # Import tool functions directly
            from src.mcp.fastmcp_server import extract_chat_messages, search_internships, analyze_chat_messages, get_internship_details
            
            # Map actions to functions
            tool_functions = {
                "extract_chat_messages": extract_chat_messages,
                "search_internships": search_internships,
                "analyze_chat_messages": analyze_chat_messages,
                "get_internship_details": get_internship_details
            }
            
            # Get the appropriate tool function
            tool_func = tool_functions.get(intent.action)
            if not tool_func:
                return {
                    "error": f"Tool '{intent.action}' not found",
                    "available_tools": list(tool_functions.keys())
                }
            
            # Execute the tool with parsed parameters
            result = tool_func(**intent.parameters)
            
            return {
                "tool_executed": intent.action,
                "parameters_used": intent.parameters,
                "mcp_response": json.dumps(result, indent=2)
            }
        
        except Exception as e:
            self.logger.error(f"Error executing MCP tool '{intent.action}': {e}")
            return {
                "error": f"Tool execution failed: {str(e)}",
                "tool": intent.action,
                "parameters": intent.parameters
            }
    
    async def get_help(self) -> str:
        """Get help information about available commands."""
        return """
🤖 **Internshala Automation - Natural Language Commands**

**Chat Message Commands:**
• "Download chat messages from the last 5 days"
• "Find messages that mention stipend above 1000"
• "Extract all chat messages and export to CSV"
• "Get messages from last week containing 'interview'"

**Internship Search Commands:**  
• "Show opportunities posted in the last 7 days for Graphic Design"
• "Find remote marketing internships"
• "Search for Python internships at startups"
• "Download all internships where company is a startup and role is Marketing"

**Analysis Commands:**
• "Analyze chat messages for stipend patterns"
• "Show summary of extracted messages"
• "Find keyword frequency in messages"

**Detailed Information:**
• "Get details for internship at [URL]"
• "Extract requirements for these internships: [URLs]"

**Tips:**
- Be specific about time periods (e.g., "last 5 days", "this week")
- Mention specific roles, skills, or keywords
- Specify if you want startup companies only
- Add "export to CSV" if you want downloadable results
"""
    
    async def list_recent_exports(self) -> Dict[str, Any]:
        """List recent CSV exports and their locations."""
        try:
            from pathlib import Path
            import os
            
            exports_dir = Path(config.csv_output_dir)
            if not exports_dir.exists():
                return {
                    "exports": [],
                    "message": "No exports directory found"
                }
            
            csv_files = list(exports_dir.glob("*.csv"))
            csv_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            exports = []
            for file in csv_files[:10]:  # Last 10 files
                stat = file.stat()
                exports.append({
                    "filename": file.name,
                    "path": str(file),
                    "size_kb": round(stat.st_size / 1024, 2),
                    "modified": stat.st_mtime,
                    "type": "chat" if "chat" in file.name else "internship" if "internship" in file.name else "unknown"
                })
            
            return {
                "exports": exports,
                "total_files": len(csv_files),
                "exports_directory": str(exports_dir)
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "exports": []
            }


# Example usage functions for testing
async def demo_natural_language_commands():
    """Demonstrate natural language command processing."""
    client = InternshalaAutomationClient()
    
    test_commands = [
        "Download chat messages from the last 5 days",
        "Find messages that mention stipend above 1000", 
        "Show opportunities posted in the last 7 days for Graphic Design",
        "Download all internships where company is a startup and role is Marketing"
    ]
    
    print("🤖 Testing Natural Language Commands:")
    print("=" * 50)
    
    for command in test_commands:
        print(f"\n💬 User: \"{command}\"")
        result = await client.process_natural_language_command(command)
        
        if result["success"]:
            intent = result["parsed_intent"]
            print(f"🎯 Understood: {intent['action']} (confidence: {intent['confidence']})")
            print(f"📋 Parameters: {json.dumps(intent['parameters'], indent=2)}")
        else:
            print(f"❌ Error: {result['error']}")
        
        print("-" * 30)


if __name__ == "__main__":
    asyncio.run(demo_natural_language_commands())
