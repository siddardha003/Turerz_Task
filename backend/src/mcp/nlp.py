"""
Natural Language Interface for Internshala Automation.
Processes natural language commands and converts them to MCP tool calls.
"""

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta

from openai import AsyncOpenAI
from pydantic import BaseModel

from src.config import config
from src.utils.logging import get_logger


logger = get_logger(__name__)


class CommandIntent(BaseModel):
    """Represents a parsed natural language command."""
    action: str  # extract_chats, search_internships, etc.
    parameters: Dict[str, Any]
    confidence: float
    original_command: str


class NaturalLanguageProcessor:
    """Processes natural language commands for Internshala automation."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = AsyncOpenAI(api_key=api_key or config.openai_api_key)
        self.logger = get_logger(__name__)
    
    async def parse_command(self, user_input: str) -> CommandIntent:
        """Parse a natural language command into structured parameters."""
        try:
            # Create the system prompt for command parsing
            system_prompt = self._create_system_prompt()
            
            # Create the user prompt
            user_prompt = f"""
            Please parse this command: "{user_input}"
            
            Return a JSON object with:
            - action: the MCP tool to call
            - parameters: dictionary of parameters for the tool
            - confidence: float between 0-1 indicating parsing confidence
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            # Parse the response
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from the response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                parsed_data = json.loads(json_match.group())
                
                return CommandIntent(
                    action=parsed_data.get("action", "unknown"),
                    parameters=parsed_data.get("parameters", {}),
                    confidence=parsed_data.get("confidence", 0.5),
                    original_command=user_input
                )
            else:
                # Fallback parsing
                return await self._fallback_parse(user_input)
                
        except Exception as e:
            self.logger.error(f"Error parsing command '{user_input}': {e}")
            return await self._fallback_parse(user_input)
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for command parsing."""
        return """
You are an expert command parser for Internshala automation. Your job is to parse natural language commands into structured tool calls.

Available Tools and their parameters:

1. **extract_chat_messages** - Extract and filter chat messages
   Parameters:
   - limit (int): max messages to extract (1-500)
   - since_days (int): messages from last N days
   - keyword (str): filter by keyword
   - min_stipend (number): filter messages mentioning stipend above amount
   - include_sent (bool): include sent messages
   - include_received (bool): include received messages
   - export_csv (bool): export to CSV

2. **search_internships** - Search and filter internships
   Parameters:
   - role (str): job title/role to search
   - location (str): location or "Remote"
   - posted_within_days (int): posted within last N days
   - min_stipend (number): minimum stipend in INR
   - max_stipend (number): maximum stipend in INR
   - work_mode (str): "remote", "on-site", or "hybrid"
   - startup_only (bool): filter for startups only
   - limit (int): max results (1-100)
   - export_csv (bool): export to CSV

3. **analyze_chat_messages** - Analyze extracted messages
   Parameters:
   - analysis_type (str): "summary", "stipend_analysis", "sender_analysis", "keyword_frequency"
   - keyword (str): specific keyword to analyze

4. **get_internship_details** - Get detailed internship info
   Parameters:
   - internship_urls (array): list of internship URLs
   - include_requirements (bool): include requirements
   - include_company_info (bool): include company info

Example parsing:

Input: "Download chat messages from the last 5 days"
Output: {
  "action": "extract_chat_messages",
  "parameters": {
    "since_days": 5,
    "export_csv": true
  },
  "confidence": 0.95
}

Input: "Find messages that mention stipend above 1000"
Output: {
  "action": "extract_chat_messages", 
  "parameters": {
    "min_stipend": 1000,
    "keyword": "stipend"
  },
  "confidence": 0.9
}

Input: "Show opportunities posted in the last 7 days for Graphic Design"
Output: {
  "action": "search_internships",
  "parameters": {
    "role": "Graphic Design",
    "posted_within_days": 7
  },
  "confidence": 0.95
}

Input: "Download all internships where company is a startup and role is Marketing"
Output: {
  "action": "search_internships",
  "parameters": {
    "role": "Marketing", 
    "startup_only": true,
    "export_csv": true
  },
  "confidence": 0.9
}

Parse commands accurately and return JSON only. Be confident when the intent is clear.
"""
    
    async def _fallback_parse(self, user_input: str) -> CommandIntent:
        """Fallback parsing using pattern matching."""
        user_lower = user_input.lower()
        
        # Chat message extraction patterns
        if any(word in user_lower for word in ["chat", "message", "download message"]):
            parameters = {"export_csv": True}
            
            # Extract time period
            days_match = re.search(r'(\d+)\s*days?', user_lower)
            if days_match:
                parameters["since_days"] = int(days_match.group(1))
            
            # Extract stipend filter
            stipend_match = re.search(r'stipend.*?(\d+)', user_lower)
            if stipend_match:
                parameters["min_stipend"] = int(stipend_match.group(1))
            
            # Extract keyword
            if "mention" in user_lower:
                keyword_match = re.search(r'mention\s+(\w+)', user_lower)
                if keyword_match:
                    parameters["keyword"] = keyword_match.group(1)
            
            return CommandIntent(
                action="extract_chat_messages",
                parameters=parameters,
                confidence=0.7,
                original_command=user_input
            )
        
        # Internship search patterns
        elif any(word in user_lower for word in ["internship", "opportunity", "job", "search"]):
            parameters = {"export_csv": True}
            
            # Extract role/title
            role_patterns = [
                r'for\s+([a-zA-Z\s]+?)(?:\s|$)',
                r'role\s+is\s+([a-zA-Z\s]+?)(?:\s|$)',
                r'in\s+([a-zA-Z\s]+?)(?:\s|$)'
            ]
            for pattern in role_patterns:
                role_match = re.search(pattern, user_lower)
                if role_match:
                    parameters["role"] = role_match.group(1).strip().title()
                    break
            
            # Extract time period
            days_match = re.search(r'(\d+)\s*days?', user_lower)
            if days_match:
                parameters["posted_within_days"] = int(days_match.group(1))
            
            # Extract startup filter
            if "startup" in user_lower:
                parameters["startup_only"] = True
            
            # Extract location
            if "remote" in user_lower:
                parameters["work_mode"] = "remote"
            
            return CommandIntent(
                action="search_internships",
                parameters=parameters,
                confidence=0.7,
                original_command=user_input
            )
        
        # Default fallback
        return CommandIntent(
            action="unknown",
            parameters={},
            confidence=0.2,
            original_command=user_input
        )
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract specific entities from text."""
        entities = {}
        
        # Extract numbers (could be stipend, days, etc.)
        numbers = re.findall(r'\d+', text)
        if numbers:
            entities["numbers"] = [int(n) for n in numbers]
        
        # Extract time references
        time_patterns = {
            "days": r'(\d+)\s*days?',
            "weeks": r'(\d+)\s*weeks?',
            "months": r'(\d+)\s*months?'
        }
        
        for unit, pattern in time_patterns.items():
            match = re.search(pattern, text.lower())
            if match:
                entities[f"time_{unit}"] = int(match.group(1))
        
        # Extract common roles/fields
        roles = [
            "marketing", "graphic design", "web development", "python", 
            "data science", "content writing", "social media", "hr",
            "business development", "sales", "design", "programming"
        ]
        
        for role in roles:
            if role in text.lower():
                entities["role"] = role.title()
                break
        
        return entities


class CommandExecutor:
    """Executes parsed commands using MCP tools."""
    
    def __init__(self, mcp_client=None):
        self.mcp_client = mcp_client
        self.logger = get_logger(__name__)
    
    async def execute_command(self, intent: CommandIntent) -> Dict[str, Any]:
        """Execute a parsed command intent."""
        try:
            if intent.action == "extract_chat_messages":
                return await self._execute_chat_extraction(intent.parameters)
            elif intent.action == "search_internships":
                return await self._execute_internship_search(intent.parameters)
            elif intent.action == "analyze_chat_messages":
                return await self._execute_chat_analysis(intent.parameters)
            elif intent.action == "get_internship_details":
                return await self._execute_internship_details(intent.parameters)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {intent.action}",
                    "suggestion": "Try commands like 'download chat messages' or 'search for marketing internships'"
                }
        
        except Exception as e:
            self.logger.error(f"Error executing command: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_chat_extraction(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute chat message extraction."""
        # This would call the MCP tool
        # For now, return a simulation
        return {
            "success": True,
            "action": "extract_chat_messages",
            "parameters": parameters,
            "result": "Chat extraction would be executed with these parameters"
        }
    
    async def _execute_internship_search(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute internship search."""
        return {
            "success": True,
            "action": "search_internships", 
            "parameters": parameters,
            "result": "Internship search would be executed with these parameters"
        }
    
    async def _execute_chat_analysis(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute chat analysis."""
        return {
            "success": True,
            "action": "analyze_chat_messages",
            "parameters": parameters,
            "result": "Chat analysis would be executed with these parameters"
        }
    
    async def _execute_internship_details(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute internship details extraction."""
        return {
            "success": True,
            "action": "get_internship_details",
            "parameters": parameters,
            "result": "Internship details extraction would be executed with these parameters"
        }
