"""
Smart Recommendations Module
AI-powered recommendations for internship applications
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from src.ai.openai_client import OpenAIClient
from src.utils.logging import get_logger
from src.config import config

logger = get_logger(__name__)

class SmartRecommendations:
    """
    AI-powered recommendation system for internship applications
    """
    
    def __init__(self):
        self.openai_client = OpenAIClient()
        self.enabled = config.enable_smart_recommendations
    
    async def get_application_strategy(
        self,
        user_profile: Dict[str, Any],
        available_internships: List[Dict[str, Any]],
        chat_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive application strategy
        
        Args:
            user_profile: User's skills, experience, preferences
            available_internships: List of available opportunities
            chat_history: Previous communication history
            
        Returns:
            Strategic recommendations
        """
        recommendations = {
            "strategy_timestamp": datetime.now().isoformat(),
            "ai_enabled": self.enabled and self.openai_client.is_available(),
            "total_opportunities": len(available_internships)
        }
        
        if not available_internships:
            recommendations["status"] = "no_opportunities"
            return recommendations
        
        # Basic strategy analysis
        recommendations.update(self._basic_strategy_analysis(user_profile, available_internships))
        
        # AI-powered strategic insights
        if self.enabled and self.openai_client.is_available():
            try:
                ai_strategy = await self._generate_ai_strategy(
                    user_profile, available_internships, chat_history
                )
                if ai_strategy:
                    recommendations["ai_strategy"] = ai_strategy
                    recommendations["enhanced_strategy"] = True
                else:
                    recommendations["enhanced_strategy"] = False
            except Exception as e:
                logger.error(f"AI strategy generation failed: {e}")
                recommendations["ai_error"] = str(e)
                recommendations["enhanced_strategy"] = False
        
        return recommendations
    
    def _basic_strategy_analysis(
        self,
        user_profile: Dict[str, Any],
        internships: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate basic strategy recommendations"""
        
        user_skills = set(skill.lower() for skill in user_profile.get('skills', []))
        user_interests = set(interest.lower() for interest in user_profile.get('interests', []))
        
        # Score internships based on skill match
        scored_internships = []
        for internship in internships:
            required_skills = set(skill.lower() for skill in internship.get('tags', []))
            skill_match = len(user_skills & required_skills) / len(required_skills) if required_skills else 0
            
            title_lower = internship.get('title', '').lower()
            interest_match = any(interest in title_lower for interest in user_interests)
            
            total_score = skill_match * 0.7 + (0.3 if interest_match else 0)
            
            scored_internships.append({
                'internship': internship,
                'skill_match_score': skill_match,
                'interest_match': interest_match,
                'total_score': total_score
            })
        
        # Sort by score
        scored_internships.sort(key=lambda x: x['total_score'], reverse=True)
        
        # Generate recommendations
        top_matches = scored_internships[:5]
        skill_gaps = set()
        
        for internship in internships[:10]:  # Analyze top opportunities
            required_skills = set(skill.lower() for skill in internship.get('tags', []))
            gaps = required_skills - user_skills
            skill_gaps.update(gaps)
        
        return {
            "basic_strategy": {
                "top_recommendations": [
                    {
                        "title": match['internship'].get('title', ''),
                        "company": match['internship'].get('company_name', ''),
                        "match_score": round(match['total_score'] * 100, 1),
                        "skill_match": round(match['skill_match_score'] * 100, 1),
                        "interest_match": match['interest_match']
                    }
                    for match in top_matches
                ],
                "skill_gaps_identified": list(skill_gaps)[:10],
                "total_high_match": len([s for s in scored_internships if s['total_score'] > 0.5]),
                "application_priority": "high" if top_matches and top_matches[0]['total_score'] > 0.7 else "medium"
            }
        }
    
    async def _generate_ai_strategy(
        self,
        user_profile: Dict[str, Any],
        internships: List[Dict[str, Any]],
        chat_history: Optional[List[Dict[str, Any]]]
    ) -> Optional[Dict[str, Any]]:
        """Generate AI-powered application strategy"""
        
        # Prepare context for AI
        internship_summary = "\n".join([
            f"- {intern.get('title', '')} at {intern.get('company_name', '')} "
            f"(Skills: {', '.join(intern.get('tags', [])[:3])})"
            for intern in internships[:15]
        ])
        
        chat_summary = ""
        if chat_history:
            chat_summary = f"\nPrevious communication history: {len(chat_history)} interactions"
        
        strategy_prompt = [
            {
                "role": "system",
                "content": "You are an expert career strategist specializing in internship applications. Provide comprehensive, actionable strategies."
            },
            {
                "role": "user",
                "content": f"""Create a strategic application plan for this candidate:

User Profile:
- Skills: {', '.join(user_profile.get('skills', []))}
- Experience Level: {user_profile.get('experience_level', 'beginner')}
- Interests: {', '.join(user_profile.get('interests', []))}
- Career Goals: {user_profile.get('career_goals', 'Not specified')}

Available Opportunities:
{internship_summary}

{chat_summary}

Provide strategic recommendations in JSON format:
- priority_applications: top 5 opportunities with reasoning
- skill_development_plan: specific skills to develop
- application_timeline: when to apply to each opportunity  
- networking_strategy: how to improve chances
- follow_up_strategy: communication approach
- backup_plan: alternative opportunities
- success_metrics: how to measure progress
"""
            }
        ]
        
        try:
            response = await self.openai_client.chat_completion(strategy_prompt, json_mode=True)
            if response:
                import json
                return json.loads(response)
        except Exception as e:
            logger.error(f"AI strategy generation error: {e}")
        
        return None
    
    async def get_skill_recommendations(
        self,
        user_profile: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get personalized skill development recommendations
        
        Args:
            user_profile: User's current skills and experience
            market_data: Current market analysis data
            
        Returns:
            Skill development recommendations
        """
        recommendations = {
            "recommendation_timestamp": datetime.now().isoformat(),
            "ai_enabled": self.enabled and self.openai_client.is_available()
        }
        
        current_skills = set(skill.lower() for skill in user_profile.get('skills', []))
        
        # Basic skill analysis
        if 'market_breakdown' in market_data:
            top_skills = market_data['market_breakdown'].get('top_skills', [])
            
            # Find skill gaps
            skill_gaps = []
            for skill, count in top_skills:
                if skill.lower() not in current_skills:
                    skill_gaps.append({
                        'skill': skill,
                        'market_demand': count,
                        'priority': 'high' if count > 10 else 'medium'
                    })
            
            recommendations['basic_analysis'] = {
                'current_skills_count': len(current_skills),
                'market_relevant_skills': len([s for s, _ in top_skills if s.lower() in current_skills]),
                'skill_gaps_identified': skill_gaps[:10]
            }
        
        # AI-powered skill recommendations
        if self.enabled and self.openai_client.is_available():
            try:
                ai_recommendations = await self._generate_skill_recommendations(
                    user_profile, market_data
                )
                if ai_recommendations:
                    recommendations["ai_skill_plan"] = ai_recommendations
                    recommendations["enhanced_recommendations"] = True
            except Exception as e:
                logger.error(f"AI skill recommendations failed: {e}")
                recommendations["ai_error"] = str(e)
        
        return recommendations
    
    async def _generate_skill_recommendations(
        self,
        user_profile: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate AI-powered skill development plan"""
        
        skill_prompt = [
            {
                "role": "system",
                "content": "You are an expert career development advisor specializing in skill development for internship success."
            },
            {
                "role": "user",
                "content": f"""Create a personalized skill development plan:

Current Profile:
- Existing Skills: {', '.join(user_profile.get('skills', []))}
- Experience Level: {user_profile.get('experience_level', 'beginner')}
- Career Goals: {user_profile.get('career_goals', 'Not specified')}

Market Insights:
- Top In-Demand Skills: {market_data.get('market_breakdown', {}).get('top_skills', [])[:10]}
- Growing Categories: {market_data.get('market_breakdown', {}).get('top_categories', [])[:5]}

Provide development plan in JSON format:
- priority_skills: top 5 skills to develop with reasoning
- learning_path: step-by-step learning approach
- time_investment: estimated time for each skill
- learning_resources: specific resources and platforms
- milestone_tracking: how to measure progress
- portfolio_projects: projects to demonstrate skills
- certification_goals: relevant certifications to pursue
"""
            }
        ]
        
        try:
            response = await self.openai_client.chat_completion(skill_prompt, json_mode=True)
            if response:
                import json
                return json.loads(response)
        except Exception as e:
            logger.error(f"Skill recommendations generation error: {e}")
        
        return None
    
    async def get_networking_recommendations(
        self,
        user_profile: Dict[str, Any],
        target_companies: List[str],
        industry_focus: str
    ) -> Dict[str, Any]:
        """
        Get networking and relationship building recommendations
        
        Args:
            user_profile: User's background and goals
            target_companies: Companies of interest
            industry_focus: Target industry or field
            
        Returns:
            Networking strategy recommendations
        """
        if not self.enabled or not self.openai_client.is_available():
            return {
                "networking_available": False,
                "reason": "AI recommendations not enabled"
            }
        
        networking_prompt = [
            {
                "role": "system",
                "content": "You are a professional networking expert who helps students build valuable industry connections for internship success."
            },
            {
                "role": "user",
                "content": f"""Create a networking strategy for internship success:

User Background:
- Skills: {', '.join(user_profile.get('skills', []))}
- Experience: {user_profile.get('experience_level', 'beginner')}
- Industry Focus: {industry_focus}
- Target Companies: {', '.join(target_companies)}

Provide networking strategy in JSON format:
- linkedin_strategy: how to optimize and use LinkedIn effectively
- industry_events: relevant events and conferences to attend
- online_communities: communities and forums to join
- informational_interviews: how to request and conduct them
- content_strategy: what content to create and share
- mentor_identification: how to find and approach mentors
- follow_up_techniques: how to maintain relationships
- networking_timeline: 30/60/90 day networking plan
"""
            }
        ]
        
        try:
            response = await self.openai_client.chat_completion(networking_prompt, json_mode=True)
            if response:
                import json
                networking_plan = json.loads(response)
                networking_plan["recommendation_timestamp"] = datetime.now().isoformat()
                networking_plan["networking_available"] = True
                return networking_plan
        except Exception as e:
            logger.error(f"Networking recommendations failed: {e}")
        
        return {
            "networking_available": False,
            "error": "Failed to generate networking recommendations"
        }
