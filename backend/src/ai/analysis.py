"""
AI-Powered Analysis Module
Intelligent analysis of chat messages and internship data
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from src.ai.openai_client import OpenAIClient
from src.utils.logging import get_logger
from src.config import config

logger = get_logger(__name__)

class AIAnalyzer:
    """
    AI-powered analyzer for chat messages and internship data
    """
    
    def __init__(self):
        self.openai_client = OpenAIClient()
        self.enabled = config.enable_ai_analysis
    
    async def analyze_chat_conversations(
        self,
        messages: List[Dict[str, Any]],
        include_sentiment: bool = True,
        include_success_prediction: bool = True
    ) -> Dict[str, Any]:
        """
        Comprehensive AI analysis of chat conversations
        
        Args:
            messages: List of chat messages
            include_sentiment: Whether to include sentiment analysis
            include_success_prediction: Whether to predict application success
            
        Returns:
            Analysis results
        """
        analysis = {
            "total_messages": len(messages),
            "analysis_timestamp": datetime.now().isoformat(),
            "ai_enabled": self.enabled and self.openai_client.is_available()
        }
        
        if not messages:
            analysis["status"] = "no_data"
            return analysis
        
        # Basic statistical analysis
        analysis.update(self._basic_message_analysis(messages))
        
        # AI-powered analysis if available
        if self.enabled and self.openai_client.is_available():
            try:
                ai_insights = await self.openai_client.analyze_chat_messages(messages)
                if ai_insights:
                    analysis["ai_insights"] = ai_insights
                    analysis["enhanced_analysis"] = True
                else:
                    analysis["enhanced_analysis"] = False
            except Exception as e:
                logger.error(f"AI analysis failed: {e}")
                analysis["ai_error"] = str(e)
                analysis["enhanced_analysis"] = False
        
        return analysis
    
    def _basic_message_analysis(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform basic statistical analysis of messages"""
        
        if not messages:
            return {}
        
        # Group by sender
        senders = {}
        response_times = []
        
        for msg in messages:
            sender = msg.get('sender', 'Unknown')
            if sender not in senders:
                senders[sender] = {
                    'count': 0,
                    'total_length': 0,
                    'last_message': None
                }
            
            senders[sender]['count'] += 1
            content = msg.get('cleaned_text', '')
            senders[sender]['total_length'] += len(content)
            senders[sender]['last_message'] = msg.get('timestamp')
        
        # Calculate metrics
        total_conversations = len(senders)
        avg_messages_per_conversation = len(messages) / total_conversations if total_conversations > 0 else 0
        
        # Find most active sender
        most_active_sender = max(senders.items(), key=lambda x: x[1]['count'])[0] if senders else None
        
        return {
            "basic_metrics": {
                "total_conversations": total_conversations,
                "average_messages_per_conversation": round(avg_messages_per_conversation, 2),
                "most_active_sender": most_active_sender,
                "unique_senders": list(senders.keys())
            },
            "sender_breakdown": senders
        }
    
    async def analyze_internship_market(
        self,
        internships: List[Dict[str, Any]],
        analysis_focus: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        AI-powered market analysis of internship opportunities
        
        Args:
            internships: List of internship data
            analysis_focus: Focus area (skills, companies, locations, comprehensive)
            
        Returns:
            Market analysis results
        """
        analysis = {
            "total_internships": len(internships),
            "analysis_focus": analysis_focus,
            "analysis_timestamp": datetime.now().isoformat(),
            "ai_enabled": self.enabled and self.openai_client.is_available()
        }
        
        if not internships:
            analysis["status"] = "no_data"
            return analysis
        
        # Basic market analysis
        analysis.update(self._basic_market_analysis(internships))
        
        # AI-powered insights
        if self.enabled and self.openai_client.is_available():
            try:
                ai_insights = await self.openai_client.analyze_internship_opportunities(internships)
                if ai_insights:
                    analysis["ai_market_insights"] = ai_insights
                    analysis["enhanced_analysis"] = True
                else:
                    analysis["enhanced_analysis"] = False
            except Exception as e:
                logger.error(f"AI market analysis failed: {e}")
                analysis["ai_error"] = str(e)
                analysis["enhanced_analysis"] = False
        
        return analysis
    
    def _basic_market_analysis(self, internships: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform basic statistical market analysis"""
        
        if not internships:
            return {}
        
        # Analyze by categories
        categories = {}
        locations = {}
        companies = {}
        skills_count = {}
        
        for internship in internships:
            # Categories
            title = internship.get('title', '')
            category = self._extract_category_from_title(title)
            categories[category] = categories.get(category, 0) + 1
            
            # Locations
            location = internship.get('location', 'Unknown')
            locations[location] = locations.get(location, 0) + 1
            
            # Companies
            company = internship.get('company_name', 'Unknown')
            companies[company] = companies.get(company, 0) + 1
            
            # Skills
            skills = internship.get('tags', [])
            for skill in skills:
                skills_count[skill] = skills_count.get(skill, 0) + 1
        
        # Get top items
        top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]
        top_locations = sorted(locations.items(), key=lambda x: x[1], reverse=True)[:10]
        top_companies = sorted(companies.items(), key=lambda x: x[1], reverse=True)[:10]
        top_skills = sorted(skills_count.items(), key=lambda x: x[1], reverse=True)[:15]
        
        return {
            "market_breakdown": {
                "top_categories": top_categories,
                "top_locations": top_locations,
                "top_companies": top_companies,
                "top_skills": top_skills
            },
            "market_stats": {
                "unique_categories": len(categories),
                "unique_locations": len(locations),
                "unique_companies": len(companies),
                "unique_skills": len(skills_count)
            }
        }
    
    def _extract_category_from_title(self, title: str) -> str:
        """Extract category from internship title"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['software', 'developer', 'programming', 'coding']):
            return 'Software Development'
        elif any(word in title_lower for word in ['data', 'analytics', 'science']):
            return 'Data Science'
        elif any(word in title_lower for word in ['marketing', 'digital', 'social media']):
            return 'Marketing'
        elif any(word in title_lower for word in ['design', 'ui', 'ux', 'graphic']):
            return 'Design'
        elif any(word in title_lower for word in ['finance', 'accounting', 'banking']):
            return 'Finance'
        elif any(word in title_lower for word in ['hr', 'human resource', 'recruitment']):
            return 'Human Resources'
        else:
            return 'Other'
    
    async def predict_application_success(
        self,
        chat_history: List[Dict[str, Any]],
        internship_data: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict application success using AI
        
        Args:
            chat_history: Previous chat interactions
            internship_data: Target internship information
            user_profile: User's profile and qualifications
            
        Returns:
            Success prediction and recommendations
        """
        if not self.enabled or not self.openai_client.is_available():
            return {
                "prediction_available": False,
                "reason": "AI analysis not enabled or available"
            }
        
        # Prepare context for AI analysis
        context = {
            "chat_interactions": len(chat_history),
            "internship_title": internship_data.get('title', ''),
            "company": internship_data.get('company_name', ''),
            "required_skills": internship_data.get('tags', []),
            "user_skills": user_profile.get('skills', []),
            "user_experience": user_profile.get('experience_level', 'beginner')
        }
        
        # Use OpenAI for prediction
        prediction_prompt = [
            {
                "role": "system",
                "content": "You are an expert career advisor who predicts internship application success rates based on user profile, target opportunity, and communication history."
            },
            {
                "role": "user",
                "content": f"""Predict application success for this scenario:

Target Internship:
- Title: {internship_data.get('title', '')}
- Company: {internship_data.get('company_name', '')}
- Required Skills: {', '.join(internship_data.get('tags', []))}

User Profile:
- Skills: {', '.join(user_profile.get('skills', []))}
- Experience Level: {user_profile.get('experience_level', 'beginner')}

Communication History: {len(chat_history)} previous interactions

Provide prediction in JSON format:
- success_probability: percentage (0-100)
- confidence_level: high/medium/low
- key_strengths: what works in user's favor
- improvement_areas: what could be better
- specific_recommendations: actionable advice
- optimal_timing: when to apply
"""
            }
        ]
        
        try:
            response = await self.openai_client.chat_completion(prediction_prompt, json_mode=True)
            if response:
                import json
                prediction = json.loads(response)
                prediction["prediction_timestamp"] = datetime.now().isoformat()
                prediction["prediction_available"] = True
                return prediction
        except Exception as e:
            logger.error(f"Success prediction failed: {e}")
        
        return {
            "prediction_available": False,
            "error": "Prediction analysis failed"
        }
