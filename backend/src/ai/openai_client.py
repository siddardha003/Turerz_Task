"""
OpenAI Client Integration
Handles communication with OpenAI API for intelligent features
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import openai
from openai import AsyncOpenAI

from src.config import config
from src.utils.logging import get_logger

logger = get_logger(__name__)

class OpenAIClient:
    """
    OpenAI API client for Turerez automation
    Provides intelligent analysis and natural language processing
    """
    
    def __init__(self):
        self.client = None
        self.enabled = config.openai_enabled
        self.model = config.openai_model
        self.max_tokens = config.openai_max_tokens
        self.temperature = config.openai_temperature
        
        if self.enabled:
            try:
                self.client = AsyncOpenAI(api_key=config.openai_api_key)
                logger.info(f"OpenAI client initialized with model: {self.model}")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.enabled = False
        else:
            logger.warning("OpenAI integration disabled - API key not configured")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        json_mode: bool = False
    ) -> Optional[str]:
        """
        Get chat completion from OpenAI
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (defaults to config)
            max_tokens: Max tokens (defaults to config)
            temperature: Temperature (defaults to config)
            json_mode: Whether to request JSON response
            
        Returns:
            Response content or None if failed
        """
        if not self.enabled:
            logger.warning("OpenAI not enabled - returning None")
            return None
        
        try:
            response_format = {"type": "json_object"} if json_mode else {"type": "text"}
            
            response = await self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
                response_format=response_format
            )
            
            content = response.choices[0].message.content
            logger.debug(f"OpenAI response received: {len(content) if content else 0} characters")
            
            return content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None
    
    async def analyze_chat_messages(self, messages: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Analyze chat messages using AI
        
        Args:
            messages: List of chat message objects
            
        Returns:
            Analysis results or None
        """
        if not self.enabled or not messages:
            return None
        
        # Prepare messages for analysis
        chat_text = "\n".join([
            f"From {msg.get('sender', 'Unknown')}: {msg.get('cleaned_text', '')}"
            for msg in messages[:50]  # Limit to recent messages
        ])
        
        prompt_messages = [
            {
                "role": "system",
                "content": "You are an expert analyzer of internship application conversations. Analyze the conversation data and provide insights in JSON format."
            },
            {
                "role": "user", 
                "content": f"""Analyze these internship-related chat messages and provide insights:

{chat_text}

Please provide analysis in JSON format with these fields:
- sentiment_analysis: Overall sentiment (positive/negative/neutral)
- response_rate: Estimated response rate analysis
- key_themes: Main topics discussed
- company_engagement: Level of company engagement
- success_indicators: Signs of potential success
- recommendations: Actionable recommendations
- urgency_level: How urgent follow-ups should be
"""
            }
        ]
        
        try:
            response = await self.chat_completion(prompt_messages, json_mode=True)
            if response:
                return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI analysis response: {e}")
        
        return None
    
    async def analyze_internship_opportunities(self, internships: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Analyze internship opportunities using AI
        
        Args:
            internships: List of internship objects
            
        Returns:
            Analysis results or None
        """
        if not self.enabled or not internships:
            return None
        
        # Prepare internship data for analysis
        internship_text = "\n".join([
            f"Title: {intern.get('title', '')}, Company: {intern.get('company_name', '')}, "
            f"Location: {intern.get('location', '')}, Stipend: {intern.get('stipend_text', '')}, "
            f"Skills: {', '.join(intern.get('tags', []))}"
            for intern in internships[:30]  # Limit for token efficiency
        ])
        
        prompt_messages = [
            {
                "role": "system",
                "content": "You are an expert career advisor analyzing internship opportunities. Provide strategic insights in JSON format."
            },
            {
                "role": "user",
                "content": f"""Analyze these internship opportunities and provide strategic insights:

{internship_text}

Please provide analysis in JSON format with these fields:
- market_trends: Current market trends observed
- skill_demand: Most in-demand skills
- salary_insights: Salary/stipend analysis
- geographic_trends: Location-based insights
- growth_opportunities: Best growth potential roles
- application_strategy: Strategic recommendations
- priority_applications: Which opportunities to prioritize
- skill_gaps: Skills to develop for better opportunities
"""
            }
        ]
        
        try:
            response = await self.chat_completion(prompt_messages, json_mode=True)
            if response:
                return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI analysis response: {e}")
        
        return None
    
    async def generate_application_content(
        self,
        internship: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> Optional[Dict[str, str]]:
        """
        Generate application content (cover letter, etc.)
        
        Args:
            internship: Internship details
            user_profile: User's profile information
            
        Returns:
            Generated content or None
        """
        if not self.enabled:
            return None
        
        prompt_messages = [
            {
                "role": "system",
                "content": "You are an expert career counselor who writes compelling internship applications. Generate personalized application content."
            },
            {
                "role": "user",
                "content": f"""Generate application content for this internship:

Internship Details:
- Title: {internship.get('title', '')}
- Company: {internship.get('company_name', '')}
- Requirements: {internship.get('description', '')}
- Skills needed: {', '.join(internship.get('tags', []))}

User Profile:
- Skills: {', '.join(user_profile.get('skills', []))}
- Experience: {user_profile.get('experience', '')}
- Interests: {', '.join(user_profile.get('interests', []))}

Please provide in JSON format:
- cover_letter: Professional cover letter (150-200 words)
- key_highlights: 3-5 key points to emphasize
- questions_to_ask: Thoughtful questions for the employer
- follow_up_strategy: How and when to follow up
"""
            }
        ]
        
        try:
            response = await self.chat_completion(prompt_messages, json_mode=True)
            if response:
                return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse application content response: {e}")
        
        return None
    
    async def process_natural_language_query(self, query: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process natural language queries for MCP integration
        
        Args:
            query: Natural language query
            context: Context information
            
        Returns:
            Processed query with intent and parameters
        """
        if not self.enabled:
            return None
        
        prompt_messages = [
            {
                "role": "system",
                "content": """You are an AI assistant that converts natural language queries into structured commands for an internship automation system. 

Available tools:
- extract_chats: Extract chat messages with filters
- search_internships: Search internships with criteria
- analyze_market: Perform market analysis
- export_data: Export data in various formats
- get_recommendations: Get AI recommendations

Convert the user query into appropriate tool calls with parameters."""
            },
            {
                "role": "user",
                "content": f"""User query: "{query}"

Context: {json.dumps(context, default=str)}

Convert this into structured tool calls in JSON format:
{{
  "intent": "main intent of the query",
  "tool_calls": [
    {{
      "tool": "tool_name",
      "parameters": {{}}
    }}
  ],
  "explanation": "what the system will do"
}}"""
            }
        ]
        
        try:
            response = await self.chat_completion(prompt_messages, json_mode=True)
            if response:
                return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse natural language query response: {e}")
        
        return None
    
    async def enhance_export_content(self, data: Dict[str, Any], export_type: str) -> Optional[Dict[str, Any]]:
        """
        Enhance export content with AI insights
        
        Args:
            data: Data to be exported
            export_type: Type of export (chat, internships, etc.)
            
        Returns:
            Enhanced content with AI insights
        """
        if not self.enabled:
            return data
        
        prompt_messages = [
            {
                "role": "system",
                "content": f"You are an AI assistant that enhances {export_type} export reports with intelligent insights and summaries."
            },
            {
                "role": "user",
                "content": f"""Enhance this {export_type} export with intelligent insights:

Data summary: {len(data.get('items', []))} items
Export type: {export_type}

Please provide enhancement in JSON format:
- executive_summary: Key takeaways and insights
- trends_identified: Important trends or patterns
- actionable_insights: Specific recommendations
- success_metrics: Key performance indicators
- next_steps: Recommended actions
"""
            }
        ]
        
        try:
            response = await self.chat_completion(prompt_messages, json_mode=True)
            if response:
                enhancement = json.loads(response)
                data['ai_insights'] = enhancement
                data['enhanced_at'] = datetime.now().isoformat()
                return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse enhancement response: {e}")
        
        return data
    
    def is_available(self) -> bool:
        """Check if OpenAI integration is available"""
        return self.enabled and self.client is not None
