"""
Browser automation manager for Internshala platform.
Uses Selenium WebDriver for robust automation with session management.
"""

import asyncio
from typing import Optional, Dict, Any, List
from pathlib import Path
import json

from src.browser.selenium_manager import SeleniumBrowserManager
from src.browser.internshala_bot import InternshalaSeleniumBot
from src.config import config
from src.utils.logging import get_logger


class BrowserManager:
    """Manages browser instances and sessions for Internshala automation using Selenium."""
    
    def __init__(self, trace_id: Optional[str] = None):
        self.logger = get_logger(__name__, trace_id)
        self.internshala_bot: Optional[InternshalaSeleniumBot] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def start(self) -> None:
        """Initialize browser and automation tools."""
        self.logger.info("Starting browser manager with Selenium")
        
        try:
            self.internshala_bot = InternshalaSeleniumBot(self.logger.trace_id)
            await self.internshala_bot.__aenter__()
            
            self.logger.info("Browser manager started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start browser manager: {e}")
            raise RuntimeError(f"Browser initialization failed: {e}")
    
    async def close(self) -> None:
        """Close browser and cleanup resources."""
        if self.internshala_bot:
            await self.internshala_bot.__aexit__(None, None, None)
            self.internshala_bot = None
        
        self.logger.info("Browser manager closed")
    
    async def login_to_internshala(self, email: str, password: str) -> bool:
        """Login to Internshala platform."""
        if not self.internshala_bot:
            raise RuntimeError("Browser not initialized")
        
        return await self.internshala_bot.login(email, password)
    
    async def check_authentication(self) -> bool:
        """Check if user is currently authenticated."""
        if not self.internshala_bot:
            return False
        
        return await self.internshala_bot.check_authentication()
    
    async def extract_chat_messages(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Extract chat messages from Internshala."""
        if not self.internshala_bot:
            raise RuntimeError("Browser not initialized")
        
        messages = await self.internshala_bot.extract_chat_messages(limit)
        return [message.model_dump() for message in messages]
    
    async def search_internships(
        self,
        query: str = "",
        location: str = "",
        duration: str = "",
        stipend_min: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search for internships with filters."""
        if not self.internshala_bot:
            raise RuntimeError("Browser not initialized")
        
        internships = await self.internshala_bot.search_internships(
            query=query,
            location=location,
            duration=duration,
            stipend_min=stipend_min,
            limit=limit
        )
        
        return [internship.model_dump() for internship in internships]
    
    async def get_internship_details(self, url: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific internship."""
        if not self.internshala_bot:
            raise RuntimeError("Browser not initialized")
        
        return await self.internshala_bot.get_detailed_internship(url)


class InternshalaAuth:
    """Handles authentication for Internshala platform using Selenium."""
    
    def __init__(self, trace_id: Optional[str] = None):
        self.logger = get_logger(__name__, trace_id)
        self.bot = InternshalaSeleniumBot(trace_id)
    
    async def login(self, email: str, password: str) -> bool:
        """Perform login with credentials."""
        self.logger.info(f"Attempting login for: {email}")
        
        try:
            async with self.bot:
                success = await self.bot.login(email, password)
                
                if success:
                    self.logger.info("Login successful")
                else:
                    self.logger.error("Login failed")
                
                return success
                
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return False
    
    async def check_session(self) -> bool:
        """Check if existing session is valid."""
        try:
            async with self.bot:
                return await self.bot.check_authentication()
                
        except Exception as e:
            self.logger.warning(f"Session check failed: {e}")
            return False
    
    async def ensure_authenticated(self, email: str, password: str) -> bool:
        """Ensure user is authenticated, login if needed."""
        # First check existing session
        if await self.check_session():
            self.logger.info("Already authenticated with existing session")
            return True
        
        # If not authenticated, try to login
        self.logger.info("No valid session found, attempting login")
        return await self.login(email, password)
