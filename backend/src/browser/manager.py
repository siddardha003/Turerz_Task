"""
Browser automation utilities using Playwright.
Handles session management, login flow, and rate limiting.
"""

import asyncio
import json
from pathlib import Path
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from src.config import config
from src.utils.logging import get_logger


class BrowserManager:
    """Manages browser instances and sessions for Internshala automation."""
    
    def __init__(self, trace_id: Optional[str] = None):
        self.logger = get_logger(__name__, trace_id)
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.session_file = Path("session_state.json")
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def start(self) -> None:
        """Initialize browser and context."""
        self.logger.info("Starting browser session")
        
        playwright = await async_playwright().start()
        
        # Launch browser with appropriate settings
        self.browser = await playwright.chromium.launch(
            headless=config.headless,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            ]
        )
        
        # Create context with session persistence
        context_options = {
            'viewport': {'width': 1920, 'height': 1080},
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Load existing session if available
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r') as f:
                    session_data = json.load(f)
                context_options['storage_state'] = session_data
                self.logger.info("Loaded existing session state")
            except Exception as e:
                self.logger.warning(f"Failed to load session state: {e}")
        
        self.context = await self.browser.new_context(**context_options)
        self.page = await self.context.new_page()
        
        # Set timeouts
        self.page.set_default_timeout(config.browser_timeout)
        
        self.logger.info("Browser session started successfully")
    
    async def save_session(self) -> None:
        """Save current session state."""
        if not self.context:
            return
            
        try:
            session_state = await self.context.storage_state()
            with open(self.session_file, 'w') as f:
                json.dump(session_state, f)
            self.logger.info("Session state saved")
        except Exception as e:
            self.logger.error(f"Failed to save session state: {e}")
    
    async def close(self) -> None:
        """Close browser and save session."""
        if self.context:
            await self.save_session()
        
        if self.browser:
            await self.browser.close()
            self.logger.info("Browser session closed")
    
    async def navigate_to(self, url: str, wait_for: str = 'networkidle') -> None:
        """Navigate to a URL with proper waiting."""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        self.logger.info(f"Navigating to: {url}")
        await self.page.goto(url, wait_until=wait_for)
        await asyncio.sleep(1)  # Additional stability wait
    
    async def wait_for_selector(self, selector: str, timeout: Optional[int] = None) -> bool:
        """Wait for selector with error handling."""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        try:
            await self.page.wait_for_selector(selector, timeout=timeout or config.browser_timeout)
            return True
        except Exception as e:
            self.logger.warning(f"Selector not found: {selector} - {e}")
            return False
    
    async def click_safe(self, selector: str, timeout: Optional[int] = None) -> bool:
        """Click element with error handling."""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        try:
            await self.page.click(selector, timeout=timeout or config.browser_timeout)
            self.logger.debug(f"Clicked: {selector}")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to click {selector}: {e}")
            return False
    
    async def type_safe(self, selector: str, text: str, timeout: Optional[int] = None) -> bool:
        """Type text with error handling."""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        try:
            await self.page.fill(selector, text, timeout=timeout or config.browser_timeout)
            self.logger.debug(f"Typed text in: {selector}")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to type in {selector}: {e}")
            return False
    
    async def get_text_content(self, selector: str) -> Optional[str]:
        """Get text content of element."""
        if not self.page:
            return None
        
        try:
            element = await self.page.query_selector(selector)
            if element:
                return await element.text_content()
        except Exception as e:
            self.logger.warning(f"Failed to get text from {selector}: {e}")
        
        return None
    
    async def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """Get attribute value of element."""
        if not self.page:
            return None
        
        try:
            element = await self.page.query_selector(selector)
            if element:
                return await element.get_attribute(attribute)
        except Exception as e:
            self.logger.warning(f"Failed to get {attribute} from {selector}: {e}")
        
        return None
    
    async def scroll_to_bottom(self, pause_time: float = 1.0) -> None:
        """Scroll to bottom of page with pauses."""
        if not self.page:
            return
        
        previous_height = 0
        while True:
            # Scroll to bottom
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(pause_time)
            
            # Check if new content loaded
            new_height = await self.page.evaluate("document.body.scrollHeight")
            if new_height == previous_height:
                break
            previous_height = new_height
            
            self.logger.debug(f"Scrolled to height: {new_height}")
    
    async def take_screenshot(self, name: str = "screenshot") -> str:
        """Take screenshot for debugging."""
        if not self.page:
            return ""
        
        screenshot_path = Path(f"debug_{name}_{self.logger.trace_id}.png")
        await self.page.screenshot(path=screenshot_path)
        self.logger.info(f"Screenshot saved: {screenshot_path}")
        return str(screenshot_path)
