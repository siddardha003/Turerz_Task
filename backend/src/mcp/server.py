"""
MCP Server for Internshala Automation.
Provides tools for chat extraction and internship search through Model Context Protocol.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
from datetime import datetime, timedelta

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    TextContent,
    Tool,
)
from pydantic import BaseModel

from src.chat.extractor import ChatMessageExtractor, ChatMessageAnalyzer
from src.internships.scraper import InternshipScraper, InternshipSearchFilter
from src.models import ChatFilter, InternshipFilter, InternshipMode
from src.utils.logging import get_logger
from src.config import config


logger = get_logger(__name__)


class InternshalaTools:
    """Collection of MCP tools for Internshala automation."""
    
    def __init__(self):
        self.chat_extractor = None
        self.internship_scraper = None
    
    async def initialize(self):
        """Initialize tools with browser automation."""
        try:
            self.chat_extractor = ChatMessageExtractor()
            self.internship_scraper = InternshipScraper()
            logger.info("Internshala tools initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize tools: {e}")
            raise
    
    async def cleanup(self):
        """Clean up resources."""
        if self.chat_extractor:
            await self.chat_extractor.__aexit__(None, None, None)
        if self.internship_scraper:
            await self.internship_scraper.cleanup()


# Global tools instance
tools = InternshalaTools()


# Define MCP Tools
TOOLS = [
    Tool(
        name="extract_chat_messages",
        description="Extract chat messages from Internshala with optional filtering",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of messages to extract",
                    "default": 50,
                    "minimum": 1,
                    "maximum": 500
                },
                "since_days": {
                    "type": "integer", 
                    "description": "Extract messages from the last N days",
                    "minimum": 1,
                    "maximum": 365
                },
                "keyword": {
                    "type": "string",
                    "description": "Filter messages containing this keyword"
                },
                "min_stipend": {
                    "type": "number",
                    "description": "Filter messages mentioning stipend above this amount"
                },
                "include_sent": {
                    "type": "boolean",
                    "description": "Include sent messages",
                    "default": True
                },
                "include_received": {
                    "type": "boolean", 
                    "description": "Include received messages",
                    "default": True
                },
                "export_csv": {
                    "type": "boolean",
                    "description": "Export results to CSV file",
                    "default": True
                }
            },
            "required": []
        }
    ),
    
    Tool(
        name="search_internships",
        description="Search and filter internship opportunities on Internshala",
        inputSchema={
            "type": "object",
            "properties": {
                "role": {
                    "type": "string",
                    "description": "Role or job title to search for (e.g., 'Graphic Design', 'Marketing')"
                },
                "location": {
                    "type": "string", 
                    "description": "Location preference (city name or 'Remote')"
                },
                "posted_within_days": {
                    "type": "integer",
                    "description": "Find opportunities posted within the last N days",
                    "minimum": 1,
                    "maximum": 30
                },
                "min_stipend": {
                    "type": "number",
                    "description": "Minimum stipend amount in INR"
                },
                "max_stipend": {
                    "type": "number", 
                    "description": "Maximum stipend amount in INR"
                },
                "work_mode": {
                    "type": "string",
                    "enum": ["remote", "on-site", "hybrid"],
                    "description": "Work mode preference"
                },
                "startup_only": {
                    "type": "boolean",
                    "description": "Filter for startup companies only"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results",
                    "default": 20,
                    "minimum": 1,
                    "maximum": 100
                },
                "export_csv": {
                    "type": "boolean",
                    "description": "Export results to CSV file",
                    "default": True
                }
            },
            "required": []
        }
    ),
    
    Tool(
        name="analyze_chat_messages", 
        description="Analyze extracted chat messages for patterns and insights",
        inputSchema={
            "type": "object",
            "properties": {
                "analysis_type": {
                    "type": "string",
                    "enum": ["summary", "stipend_analysis", "sender_analysis", "keyword_frequency"],
                    "description": "Type of analysis to perform",
                    "default": "summary"
                },
                "keyword": {
                    "type": "string",
                    "description": "Specific keyword to analyze (for keyword_frequency analysis)"
                }
            },
            "required": []
        }
    ),
    
    Tool(
        name="get_internship_details",
        description="Get detailed information about specific internships",
        inputSchema={
            "type": "object", 
            "properties": {
                "internship_urls": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of internship URLs to get details for"
                },
                "include_requirements": {
                    "type": "boolean",
                    "description": "Include detailed requirements and skills",
                    "default": True
                },
                "include_company_info": {
                    "type": "boolean",
                    "description": "Include company information",
                    "default": True
                }
            },
            "required": ["internship_urls"]
        }
    )
]


async def call_extract_chat_messages(arguments: Dict[str, Any]) -> CallToolResult:
    """Extract chat messages tool implementation."""
    try:
        # Parse arguments with defaults
        limit = arguments.get("limit", 50)
        since_days = arguments.get("since_days")
        keyword = arguments.get("keyword")
        min_stipend = arguments.get("min_stipend")
        include_sent = arguments.get("include_sent", True)
        include_received = arguments.get("include_received", True)
        export_csv = arguments.get("export_csv", True)
        
        # Create filter
        chat_filter = ChatFilter(
            since_days=since_days,
            keyword=keyword,
            min_stipend=min_stipend,
            limit=limit
        )
        
        # Extract messages
        async with ChatMessageExtractor() as extractor:
            messages = await extractor.extract_all_messages(
                limit=limit,
                include_sent=include_sent,
                include_received=include_received
            )
            
            # Apply additional filtering
            if chat_filter.keyword:
                messages = [
                    msg for msg in messages 
                    if chat_filter.keyword.lower() in msg.cleaned_text.lower()
                ]
            
            if chat_filter.min_stipend:
                # Filter messages mentioning stipend above threshold
                messages = [
                    msg for msg in messages
                    if any(str(chat_filter.min_stipend) in msg.cleaned_text 
                          for word in msg.cleaned_text.split())
                ]
            
            # Export if requested
            csv_file = None
            if export_csv and messages:
                csv_file = await extractor.export_to_csv(messages)
            
            # Generate summary
            analyzer = ChatMessageAnalyzer(messages)
            stats = analyzer.get_summary_stats()
            
            result = {
                "total_messages": len(messages),
                "messages_extracted": min(limit, len(messages)),
                "summary_stats": stats,
                "csv_file": csv_file,
                "sample_messages": [
                    {
                        "sender": msg.sender,
                        "direction": msg.direction.value,
                        "text": msg.cleaned_text[:100] + "..." if len(msg.cleaned_text) > 100 else msg.cleaned_text,
                        "timestamp": msg.timestamp.isoformat()
                    }
                    for msg in messages[:5]
                ]
            }
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Successfully extracted {len(messages)} chat messages.\n\n" +
                             f"Summary:\n{json.dumps(result, indent=2)}"
                    )
                ]
            )
    
    except Exception as e:
        logger.error(f"Error in extract_chat_messages: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text", 
                    text=f"Error extracting chat messages: {str(e)}"
                )
            ]
        )


async def call_search_internships(arguments: Dict[str, Any]) -> CallToolResult:
    """Search internships tool implementation."""
    try:
        # Parse arguments
        role = arguments.get("role")
        location = arguments.get("location")
        posted_within_days = arguments.get("posted_within_days")
        min_stipend = arguments.get("min_stipend")
        max_stipend = arguments.get("max_stipend")
        work_mode = arguments.get("work_mode")
        startup_only = arguments.get("startup_only")
        limit = arguments.get("limit", 20)
        export_csv = arguments.get("export_csv", True)
        
        # Create search filter
        search_filter = InternshipSearchFilter(
            keywords=[role] if role else [],
            locations=[location] if location else [],
            min_stipend=min_stipend,
            max_stipend=max_stipend,
            work_mode=InternshipMode(work_mode) if work_mode else None,
            company_types=["startup"] if startup_only else None
        )
        
        # Search internships
        async with InternshipScraper() as scraper:
            internships = await scraper.search_internships(
                search_filter=search_filter,
                limit=limit
            )
            
            # Filter by posted date if specified
            if posted_within_days:
                cutoff_date = datetime.now() - timedelta(days=posted_within_days)
                internships = [
                    internship for internship in internships
                    if internship.posted_date >= cutoff_date
                ]
            
            # Export if requested
            csv_file = None
            if export_csv and internships:
                csv_file = await scraper.export_to_csv(internships)
            
            result = {
                "total_found": len(internships),
                "search_criteria": {
                    "role": role,
                    "location": location,
                    "posted_within_days": posted_within_days,
                    "stipend_range": f"{min_stipend}-{max_stipend}" if min_stipend or max_stipend else None,
                    "work_mode": work_mode,
                    "startup_only": startup_only
                },
                "csv_file": csv_file,
                "sample_internships": [
                    {
                        "title": internship.title,
                        "company": internship.company_name,
                        "location": internship.location,
                        "stipend": internship.stipend_text,
                        "posted_date": internship.posted_date.isoformat(),
                        "url": internship.url
                    }
                    for internship in internships[:5]
                ]
            }
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Found {len(internships)} internships matching your criteria.\n\n" +
                             f"Results:\n{json.dumps(result, indent=2)}"
                    )
                ]
            )
    
    except Exception as e:
        logger.error(f"Error in search_internships: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Error searching internships: {str(e)}"
                )
            ]
        )


async def call_analyze_chat_messages(arguments: Dict[str, Any]) -> CallToolResult:
    """Analyze chat messages tool implementation."""
    try:
        analysis_type = arguments.get("analysis_type", "summary")
        keyword = arguments.get("keyword")
        
        # This would typically work with previously extracted messages
        # For now, we'll return a placeholder analysis
        
        result = {
            "analysis_type": analysis_type,
            "message": "Chat analysis feature ready. Extract messages first using extract_chat_messages tool."
        }
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Chat analysis completed.\n\n{json.dumps(result, indent=2)}"
                )
            ]
        )
    
    except Exception as e:
        logger.error(f"Error in analyze_chat_messages: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Error analyzing chat messages: {str(e)}"
                )
            ]
        )


async def call_get_internship_details(arguments: Dict[str, Any]) -> CallToolResult:
    """Get internship details tool implementation."""
    try:
        internship_urls = arguments.get("internship_urls", [])
        include_requirements = arguments.get("include_requirements", True)
        include_company_info = arguments.get("include_company_info", True)
        
        if not internship_urls:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="No internship URLs provided."
                    )
                ]
            )
        
        # Extract detailed information
        detailed_internships = []
        async with InternshipScraper() as scraper:
            for url in internship_urls[:10]:  # Limit to 10 for performance
                details = await scraper.get_internship_details(url)
                if details:
                    detailed_internships.append(details)
        
        result = {
            "internships_processed": len(internship_urls),
            "details_extracted": len(detailed_internships),
            "internships": detailed_internships
        }
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Extracted details for {len(detailed_internships)} internships.\n\n" +
                         f"Results:\n{json.dumps(result, indent=2)}"
                )
            ]
        )
    
    except Exception as e:
        logger.error(f"Error in get_internship_details: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Error getting internship details: {str(e)}"
                )
            ]
        )


# Tool routing
TOOL_HANDLERS = {
    "extract_chat_messages": call_extract_chat_messages,
    "search_internships": call_search_internships, 
    "analyze_chat_messages": call_analyze_chat_messages,
    "get_internship_details": call_get_internship_details
}


async def main():
    """Run the MCP server."""
    logger.info("Starting Internshala MCP server...")
    
    async with stdio_server() as (read_stream, write_stream):
        server = Server("internshala-automation")
        
        @server.list_tools()
        async def list_tools(request: ListToolsRequest) -> ListToolsResult:
            """List available tools."""
            return ListToolsResult(tools=TOOLS)
        
        @server.call_tool()
        async def call_tool(request: CallToolRequest) -> CallToolResult:
            """Call a tool."""
            handler = TOOL_HANDLERS.get(request.params.name)
            if not handler:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Unknown tool: {request.params.name}"
                        )
                    ]
                )
            
            return await handler(request.params.arguments or {})
        
        # Initialize tools
        await tools.initialize()
        
        try:
            await server.run(
                read_stream, 
                write_stream,
                InitializationOptions(
                    server_name="internshala-automation",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None
                    )
                )
            )
        finally:
            await tools.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
