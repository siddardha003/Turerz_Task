"""
AI Integration Package
OpenAI-powered features for intelligent automation
"""

__version__ = "1.0.0"

from .openai_client import OpenAIClient
from .analysis import AIAnalyzer
from .recommendations import SmartRecommendations
from .content_processor import ContentProcessor

__all__ = [
    "OpenAIClient",
    "AIAnalyzer", 
    "SmartRecommendations",
    "ContentProcessor"
]
