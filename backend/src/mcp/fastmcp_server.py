"""
Simplified MCP Server for Internshala Automation.
Uses FastMCP for easier setup.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from src.chat.extractor import ChatMessageExtractor, ChatMessageAnalyzer  
from src.internships.scraper import InternshipScraper, InternshipSearchFilter
from src.models import ChatFilter, InternshipFilter, InternshipMode
from src.utils.logging import get_logger
from src.config import config


logger = get_logger(__name__)

# Create FastMCP server
mcp = FastMCP("Internshala Automation")


@mcp.tool()
def extract_chat_messages(
    limit: int = 50,
    since_days: Optional[int] = None,
    keyword: Optional[str] = None,
    min_stipend: Optional[float] = None,
    include_sent: bool = True,
    include_received: bool = True,
    export_csv: bool = True
) -> Dict[str, Any]:
    """Extract chat messages from Internshala with optional filtering."""
    
    async def run_extraction():
        try:
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
                
                return {
                    "success": True,
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
        
        except Exception as e:
            logger.error(f"Error in extract_chat_messages: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # Run the async function
    return asyncio.run(run_extraction())


@mcp.tool()
def search_internships(
    role: Optional[str] = None,
    location: Optional[str] = None,
    posted_within_days: Optional[int] = None,
    min_stipend: Optional[float] = None,
    max_stipend: Optional[float] = None,
    work_mode: Optional[str] = None,
    startup_only: Optional[bool] = None,
    limit: int = 20,
    export_csv: bool = True
) -> Dict[str, Any]:
    """Search and filter internship opportunities on Internshala."""
    
    async def run_search():
        try:
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
                
                return {
                    "success": True,
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
        
        except Exception as e:
            logger.error(f"Error in search_internships: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    return asyncio.run(run_search())


@mcp.tool()
def analyze_chat_messages(
    analysis_type: str = "summary",
    keyword: Optional[str] = None
) -> Dict[str, Any]:
    """Analyze extracted chat messages for patterns and insights."""
    
    # This would typically work with previously extracted messages
    # For now, we'll return a placeholder analysis
    
    return {
        "success": True,
        "analysis_type": analysis_type,
        "message": "Chat analysis feature ready. Extract messages first using extract_chat_messages tool."
    }


@mcp.tool()
def get_internship_details(
    internship_urls: List[str],
    include_requirements: bool = True,
    include_company_info: bool = True
) -> Dict[str, Any]:
    """Get detailed information about specific internships."""
    
    async def run_details():
        try:
            if not internship_urls:
                return {
                    "success": False,
                    "error": "No internship URLs provided."
                }
            
            # Extract detailed information
            detailed_internships = []
            async with InternshipScraper() as scraper:
                for url in internship_urls[:10]:  # Limit to 10 for performance
                    details = await scraper.get_internship_details(url)
                    if details:
                        detailed_internships.append(details)
            
            return {
                "success": True,
                "internships_processed": len(internship_urls),
                "details_extracted": len(detailed_internships),
                "internships": detailed_internships
            }
        
        except Exception as e:
            logger.error(f"Error in get_internship_details: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    return asyncio.run(run_details())


if __name__ == "__main__":
    mcp.run()
