"""
Content Processing Module
AI-powered content generation and optimization for applications
"""

import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import re

from src.ai.openai_client import OpenAIClient
from src.utils.logging import get_logger
from src.config import config

logger = get_logger(__name__)

class ContentProcessor:
    """
    AI-powered content processing for application materials
    """
    
    def __init__(self):
        self.openai_client = OpenAIClient()
        self.enabled = config.enable_content_enhancement
    
    async def optimize_cover_letter(
        self,
        base_content: str,
        internship_details: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize cover letter for specific internship
        
        Args:
            base_content: Base cover letter template
            internship_details: Specific internship information
            user_profile: User's background and skills
            
        Returns:
            Optimized cover letter and analysis
        """
        result = {
            "optimization_timestamp": datetime.now().isoformat(),
            "ai_enabled": self.enabled and self.openai_client.is_available(),
            "original_length": len(base_content),
            "internship_title": internship_details.get('title', 'Not specified')
        }
        
        # Basic optimization (always available)
        basic_optimization = self._basic_content_optimization(
            base_content, internship_details, user_profile
        )
        result.update(basic_optimization)
        
        # AI-powered optimization
        if self.enabled and self.openai_client.is_available():
            try:
                ai_optimization = await self._ai_optimize_cover_letter(
                    base_content, internship_details, user_profile
                )
                if ai_optimization:
                    result["ai_optimized_content"] = ai_optimization
                    result["optimization_successful"] = True
                else:
                    result["optimization_successful"] = False
            except Exception as e:
                logger.error(f"AI cover letter optimization failed: {e}")
                result["optimization_error"] = str(e)
                result["optimization_successful"] = False
        
        return result
    
    def _basic_content_optimization(
        self,
        content: str,
        internship: Dict[str, Any],
        profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform basic content optimization without AI"""
        
        # Extract placeholders and basic analysis
        placeholders = re.findall(r'\{(\w+)\}', content)
        word_count = len(content.split())
        
        # Basic replacement mapping
        replacements = {
            'company': internship.get('company_name', '[Company Name]'),
            'position': internship.get('title', '[Position Title]'),
            'name': profile.get('name', '[Your Name]'),
            'degree': profile.get('education', '[Your Degree]'),
            'university': profile.get('university', '[Your University]')
        }
        
        # Apply basic replacements
        optimized_content = content
        for placeholder in placeholders:
            if placeholder in replacements:
                optimized_content = optimized_content.replace(
                    f'{{{placeholder}}}', replacements[placeholder]
                )
        
        # Basic content analysis
        analysis = {
            "word_count": word_count,
            "character_count": len(content),
            "placeholders_found": placeholders,
            "placeholders_replaced": len([p for p in placeholders if p in replacements]),
            "recommended_length": "optimal" if 150 <= word_count <= 300 else "review_needed"
        }
        
        return {
            "basic_optimization": {
                "optimized_content": optimized_content,
                "analysis": analysis,
                "suggestions": self._generate_basic_suggestions(analysis, internship)
            }
        }
    
    def _generate_basic_suggestions(
        self,
        analysis: Dict[str, Any],
        internship: Dict[str, Any]
    ) -> List[str]:
        """Generate basic improvement suggestions"""
        
        suggestions = []
        
        if analysis["word_count"] < 150:
            suggestions.append("Consider expanding your cover letter to 150-300 words")
        elif analysis["word_count"] > 300:
            suggestions.append("Consider shortening your cover letter to under 300 words")
        
        if analysis["placeholders_replaced"] < analysis["placeholders_found"]:
            suggestions.append("Some placeholders were not replaced - review and customize")
        
        # Check for required skills mention
        skills = internship.get('tags', [])
        if skills:
            suggestions.append(f"Consider mentioning relevant skills: {', '.join(skills[:3])}")
        
        suggestions.append("Personalize the content for this specific company and role")
        suggestions.append("Include specific examples of relevant experience")
        
        return suggestions
    
    async def _ai_optimize_cover_letter(
        self,
        content: str,
        internship: Dict[str, Any],
        profile: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """AI-powered cover letter optimization"""
        
        optimization_prompt = [
            {
                "role": "system",
                "content": "You are an expert career coach specializing in creating compelling cover letters for internship applications."
            },
            {
                "role": "user",
                "content": f"""Optimize this cover letter for maximum impact:

Original Cover Letter:
{content}

Internship Details:
- Position: {internship.get('title', 'Not specified')}
- Company: {internship.get('company_name', 'Not specified')}
- Required Skills: {', '.join(internship.get('tags', []))}
- Location: {internship.get('location', 'Not specified')}
- Duration: {internship.get('duration', 'Not specified')}

Candidate Profile:
- Skills: {', '.join(profile.get('skills', []))}
- Experience Level: {profile.get('experience_level', 'beginner')}
- Education: {profile.get('education', 'Not specified')}
- Career Goals: {profile.get('career_goals', 'Not specified')}

Provide optimization in JSON format:
- optimized_cover_letter: fully optimized version (150-300 words)
- key_improvements: list of major improvements made
- personalization_added: company-specific elements included
- skill_alignment: how skills were matched to requirements
- tone_assessment: professional tone evaluation
- impact_score: predicted effectiveness (1-10)
- final_suggestions: additional recommendations
"""
            }
        ]
        
        try:
            response = await self.openai_client.chat_completion(optimization_prompt, json_mode=True)
            if response:
                import json
                return json.loads(response)
        except Exception as e:
            logger.error(f"AI cover letter optimization error: {e}")
        
        return None
    
    async def generate_application_email(
        self,
        internship_details: Dict[str, Any],
        user_profile: Dict[str, Any],
        email_type: str = "application"
    ) -> Dict[str, Any]:
        """
        Generate professional application email
        
        Args:
            internship_details: Internship information
            user_profile: User's background
            email_type: Type of email (application, follow_up, thank_you)
            
        Returns:
            Generated email content and metadata
        """
        result = {
            "generation_timestamp": datetime.now().isoformat(),
            "email_type": email_type,
            "ai_enabled": self.enabled and self.openai_client.is_available()
        }
        
        # Basic email template
        basic_email = self._generate_basic_email(internship_details, user_profile, email_type)
        result["basic_email"] = basic_email
        
        # AI-enhanced email
        if self.enabled and self.openai_client.is_available():
            try:
                ai_email = await self._ai_generate_email(
                    internship_details, user_profile, email_type
                )
                if ai_email:
                    result["ai_generated_email"] = ai_email
                    result["generation_successful"] = True
                else:
                    result["generation_successful"] = False
            except Exception as e:
                logger.error(f"AI email generation failed: {e}")
                result["generation_error"] = str(e)
                result["generation_successful"] = False
        
        return result
    
    def _generate_basic_email(
        self,
        internship: Dict[str, Any],
        profile: Dict[str, Any],
        email_type: str
    ) -> Dict[str, Any]:
        """Generate basic email template"""
        
        company = internship.get('company_name', '[Company Name]')
        position = internship.get('title', '[Position Title]')
        
        if email_type == "application":
            subject = f"Application for {position} Internship - {profile.get('name', '[Your Name]')}"
            body = f"""Dear Hiring Manager,

I am writing to express my interest in the {position} internship opportunity at {company}. As a {profile.get('education', 'student')} with skills in {', '.join(profile.get('skills', [])[:3])}, I am excited about the possibility of contributing to your team.

I have attached my resume and cover letter for your review. I would welcome the opportunity to discuss how my background and enthusiasm can benefit your organization.

Thank you for your consideration.

Best regards,
{profile.get('name', '[Your Name]')}
{profile.get('email', '[Your Email]')}
{profile.get('phone', '[Your Phone]')}"""
        
        elif email_type == "follow_up":
            subject = f"Following up on {position} Internship Application"
            body = f"""Dear Hiring Manager,

I hope this email finds you well. I am following up on my application for the {position} internship position at {company}, which I submitted on [Application Date].

I remain very interested in this opportunity and would appreciate any updates on the selection process. I am happy to provide any additional information you may need.

Thank you for your time and consideration.

Best regards,
{profile.get('name', '[Your Name]')}"""
        
        else:  # thank_you
            subject = f"Thank you for the {position} Interview"
            body = f"""Dear [Interviewer Name],

Thank you for taking the time to interview me for the {position} internship position at {company}. I enjoyed our conversation about [specific topic discussed] and learning more about your team.

I am very excited about the opportunity to contribute to {company} and apply my skills in {', '.join(profile.get('skills', [])[:2])} to support your projects.

I look forward to hearing about next steps.

Best regards,
{profile.get('name', '[Your Name]')}"""
        
        return {
            "subject": subject,
            "body": body,
            "email_type": email_type,
            "word_count": len(body.split())
        }
    
    async def _ai_generate_email(
        self,
        internship: Dict[str, Any],
        profile: Dict[str, Any],
        email_type: str
    ) -> Optional[Dict[str, Any]]:
        """AI-powered email generation"""
        
        email_prompt = [
            {
                "role": "system",
                "content": f"You are a professional communication expert specializing in {email_type} emails for internship applications."
            },
            {
                "role": "user",
                "content": f"""Generate a professional {email_type} email:

Internship Details:
- Position: {internship.get('title', 'Not specified')}
- Company: {internship.get('company_name', 'Not specified')}
- Industry: {internship.get('category', 'Not specified')}
- Location: {internship.get('location', 'Not specified')}

Candidate Information:
- Name: {profile.get('name', '[Name]')}
- Education: {profile.get('education', 'Student')}
- Skills: {', '.join(profile.get('skills', []))}
- Experience Level: {profile.get('experience_level', 'Entry level')}

Generate professional email in JSON format:
- subject_line: compelling and specific subject
- email_body: professional, personalized content (100-200 words)
- tone_analysis: tone and style used
- personalization_elements: company-specific details included
- call_to_action: clear next steps requested
- professional_score: effectiveness rating (1-10)
- formatting_suggestions: how to format the email
"""
            }
        ]
        
        try:
            response = await self.openai_client.chat_completion(email_prompt, json_mode=True)
            if response:
                import json
                return json.loads(response)
        except Exception as e:
            logger.error(f"AI email generation error: {e}")
        
        return None
    
    async def analyze_job_description(
        self,
        job_description: str,
        user_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze job description and match with user skills
        
        Args:
            job_description: Full job description text
            user_skills: User's current skills
            
        Returns:
            Detailed analysis and matching
        """
        result = {
            "analysis_timestamp": datetime.now().isoformat(),
            "description_length": len(job_description),
            "user_skills_count": len(user_skills)
        }
        
        # Basic keyword analysis
        basic_analysis = self._basic_job_analysis(job_description, user_skills)
        result.update(basic_analysis)
        
        # AI-powered analysis
        if self.enabled and self.openai_client.is_available():
            try:
                ai_analysis = await self._ai_analyze_job_description(
                    job_description, user_skills
                )
                if ai_analysis:
                    result["ai_analysis"] = ai_analysis
                    result["analysis_enhanced"] = True
            except Exception as e:
                logger.error(f"AI job analysis failed: {e}")
                result["analysis_error"] = str(e)
                result["analysis_enhanced"] = False
        
        return result
    
    def _basic_job_analysis(
        self,
        description: str,
        user_skills: List[str]
    ) -> Dict[str, Any]:
        """Basic job description analysis"""
        
        # Common skill keywords
        tech_keywords = [
            'python', 'java', 'javascript', 'react', 'node', 'sql', 'aws',
            'docker', 'git', 'machine learning', 'data analysis', 'excel'
        ]
        
        soft_keywords = [
            'communication', 'teamwork', 'leadership', 'problem solving',
            'analytical', 'creative', 'adaptable', 'initiative'
        ]
        
        description_lower = description.lower()
        user_skills_lower = [skill.lower() for skill in user_skills]
        
        # Find technical skills mentioned
        tech_skills_found = [skill for skill in tech_keywords if skill in description_lower]
        soft_skills_found = [skill for skill in soft_keywords if skill in description_lower]
        
        # Match with user skills
        matching_skills = [skill for skill in user_skills_lower if skill in description_lower]
        
        # Calculate match percentage
        total_skills_found = len(tech_skills_found) + len(soft_skills_found)
        match_percentage = (len(matching_skills) / total_skills_found * 100) if total_skills_found > 0 else 0
        
        return {
            "basic_analysis": {
                "technical_skills_required": tech_skills_found,
                "soft_skills_required": soft_skills_found,
                "user_skills_matching": matching_skills,
                "match_percentage": round(match_percentage, 1),
                "total_requirements_found": total_skills_found,
                "recommendation": "strong_match" if match_percentage > 70 else "partial_match" if match_percentage > 30 else "skill_gap"
            }
        }
    
    async def _ai_analyze_job_description(
        self,
        description: str,
        user_skills: List[str]
    ) -> Optional[Dict[str, Any]]:
        """AI-powered job description analysis"""
        
        analysis_prompt = [
            {
                "role": "system",
                "content": "You are an expert HR analyst who specializes in job requirement analysis and candidate skill matching."
            },
            {
                "role": "user",
                "content": f"""Analyze this job description and evaluate skill match:

Job Description:
{description}

Candidate Skills:
{', '.join(user_skills)}

Provide comprehensive analysis in JSON format:
- required_skills: categorized list of all required skills
- nice_to_have_skills: preferred but not essential skills
- skill_match_analysis: detailed matching assessment
- missing_critical_skills: skills candidate lacks
- transferable_skills: candidate skills that could apply
- experience_level_required: estimated experience level needed
- application_readiness: is candidate ready to apply (yes/no/with_preparation)
- preparation_recommendations: specific steps to improve candidacy
- match_score: overall compatibility (1-100)
- application_strategy: how to position application effectively
"""
            }
        ]
        
        try:
            response = await self.openai_client.chat_completion(analysis_prompt, json_mode=True)
            if response:
                import json
                return json.loads(response)
        except Exception as e:
            logger.error(f"AI job analysis error: {e}")
        
        return None
    
    async def generate_interview_prep(
        self,
        internship_details: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate interview preparation materials
        
        Args:
            internship_details: Internship information
            user_profile: User's background and experience
            
        Returns:
            Interview preparation guide
        """
        if not self.enabled or not self.openai_client.is_available():
            return {
                "interview_prep_available": False,
                "reason": "AI content optimization not enabled"
            }
        
        prep_prompt = [
            {
                "role": "system",
                "content": "You are an expert interview coach specializing in internship interviews. Provide comprehensive preparation guidance."
            },
            {
                "role": "user",
                "content": f"""Create interview preparation materials:

Internship Details:
- Position: {internship_details.get('title', 'Not specified')}
- Company: {internship_details.get('company_name', 'Not specified')}
- Industry: {internship_details.get('category', 'Not specified')}
- Required Skills: {', '.join(internship_details.get('tags', []))}

Candidate Background:
- Skills: {', '.join(user_profile.get('skills', []))}
- Experience: {user_profile.get('experience_level', 'Entry level')}
- Education: {user_profile.get('education', 'Student')}
- Career Goals: {user_profile.get('career_goals', 'Not specified')}

Generate interview prep in JSON format:
- common_questions: 10 likely interview questions with sample answers
- technical_questions: technical questions specific to required skills
- behavioral_questions: STAR method behavioral questions
- company_research_topics: key areas to research about the company
- questions_to_ask: thoughtful questions candidate should ask
- preparation_timeline: week-by-week preparation schedule
- practice_recommendations: how to practice and improve
- confidence_building_tips: strategies to reduce interview anxiety
"""
            }
        ]
        
        try:
            response = await self.openai_client.chat_completion(prep_prompt, json_mode=True)
            if response:
                import json
                prep_guide = json.loads(response)
                prep_guide["preparation_timestamp"] = datetime.now().isoformat()
                prep_guide["interview_prep_available"] = True
                return prep_guide
        except Exception as e:
            logger.error(f"Interview prep generation failed: {e}")
        
        return {
            "interview_prep_available": False,
            "error": "Failed to generate interview preparation materials"
        }
