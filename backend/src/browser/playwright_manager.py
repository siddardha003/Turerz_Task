"""
Playwright browser manager for Internshala automation.
Modern browser automation with better performance and reliability.
"""

import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from src.config import config
from src.utils.logging import get_logger


logger = get_logger(__name__)


class PlaywrightManager:
    """Manages Playwright browser automation for Internshala."""
    
    def __init__(self, trace_id: Optional[str] = None):
        self.logger = get_logger(__name__, trace_id)
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.session_file = Path("playwright_session.json")
    
    async def start(self, headless: bool = None) -> None:
        """Start the browser with authentication state."""
        try:
            self.logger.info("Starting Playwright browser...")
            
            self.playwright = await async_playwright().start()
            
            # Launch browser
            self.browser = await self.playwright.chromium.launch(
                headless=headless if headless is not None else config.headless,
                args=[
                    "--no-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-web-security",
                    "--disable-dev-shm-usage"
                ]
            )
            
            # Create context with session persistence
            context_options = {
                "viewport": {"width": 1920, "height": 1080},
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            }
            
            # Load saved session if exists
            if self.session_file.exists():
                try:
                    self.context = await self.browser.new_context(
                        storage_state=str(self.session_file),
                        **context_options
                    )
                    self.logger.info("Loaded saved authentication session")
                except Exception as e:
                    self.logger.warning(f"Failed to load session: {e}, creating new context")
                    self.context = await self.browser.new_context(**context_options)
            else:
                self.context = await self.browser.new_context(**context_options)
            
            # Create page
            self.page = await self.context.new_page()
            
            # Set up request/response logging
            self.page.on("request", self._log_request)
            self.page.on("response", self._log_response)
            
            self.logger.info("Playwright browser started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start browser: {e}")
            await self.close()
            raise
    
    async def close(self) -> None:
        """Close the browser and save session."""
        try:
            if self.context:
                # Save authentication state
                await self.context.storage_state(path=str(self.session_file))
                await self.context.close()
            
            if self.browser:
                await self.browser.close()
            
            if self.playwright:
                await self.playwright.stop()
            
            self.logger.info("Browser closed successfully")
            
        except Exception as e:
            self.logger.error(f"Error closing browser: {e}")
    
    async def navigate_to(self, url: str, wait_for_load: bool = True) -> None:
        """Navigate to a URL."""
        if not self.page:
            raise RuntimeError("Browser not started")
        
        try:
            self.logger.info(f"Navigating to: {url}")
            await self.page.goto(url, wait_until="networkidle" if wait_for_load else "load")
        except PlaywrightTimeoutError:
            self.logger.warning(f"Navigation timeout for {url}")
        except Exception as e:
            self.logger.error(f"Navigation failed for {url}: {e}")
            raise
    
    async def wait_for_selector(self, selector: str, timeout: int = 10000) -> bool:
        """Wait for an element to appear."""
        if not self.page:
            return False
        
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            self.logger.warning(f"Selector not found: {selector}")
            return False
    
    async def click(self, selector: str, timeout: int = 5000) -> bool:
        """Click on an element."""
        if not self.page:
            return False
        
        try:
            await self.page.click(selector, timeout=timeout)
            return True
        except Exception as e:
            self.logger.error(f"Click failed for {selector}: {e}")
            return False
    
    async def fill(self, selector: str, value: str, timeout: int = 5000) -> bool:
        """Fill an input field."""
        if not self.page:
            return False
        
        try:
            await self.page.fill(selector, value, timeout=timeout)
            return True
        except Exception as e:
            self.logger.error(f"Fill failed for {selector}: {e}")
            return False
    
    async def get_text(self, selector: str, timeout: int = 5000) -> Optional[str]:
        """Get text content of an element."""
        if not self.page:
            return None
        
        try:
            element = await self.page.wait_for_selector(selector, timeout=timeout)
            if element:
                return await element.text_content()
        except Exception as e:
            self.logger.error(f"Get text failed for {selector}: {e}")
        
        return None
    
    async def get_attribute(self, selector: str, attribute: str, timeout: int = 5000) -> Optional[str]:
        """Get attribute value of an element."""
        if not self.page:
            return None
        
        try:
            element = await self.page.wait_for_selector(selector, timeout=timeout)
            if element:
                return await element.get_attribute(attribute)
        except Exception as e:
            self.logger.error(f"Get attribute failed for {selector}: {e}")
        
        return None
    
    async def evaluate(self, script: str) -> Any:
        """Execute JavaScript in the page."""
        if not self.page:
            return None
        
        try:
            return await self.page.evaluate(script)
        except Exception as e:
            self.logger.error(f"Script evaluation failed: {e}")
            return None
    
    async def screenshot(self, path: Optional[str] = None) -> Optional[bytes]:
        """Take a screenshot."""
        if not self.page:
            return None
        
        try:
            if path:
                await self.page.screenshot(path=path, full_page=True)
                return None
            else:
                return await self.page.screenshot(full_page=True)
        except Exception as e:
            self.logger.error(f"Screenshot failed: {e}")
            return None
    
    def _log_request(self, request) -> None:
        """Log outgoing requests."""
        if request.url.startswith("https://internshala.com"):
            self.logger.debug(f"Request: {request.method} {request.url}")
    
    def _log_response(self, response) -> None:
        """Log incoming responses."""
        if response.url.startswith("https://internshala.com"):
            self.logger.debug(f"Response: {response.status} {response.url}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


class InternshalaPlaywrightBot:
    """Specialized Playwright automation for Internshala website."""
    
    def __init__(self, browser_manager: PlaywrightManager):
        self.browser = browser_manager
        self.logger = get_logger(__name__)
    
    async def login(self, email: str, password: str) -> bool:
        """Login to Internshala using Playwright."""
        try:
            self.logger.info("Attempting Internshala login...")
            
            # Navigate to login page
            await self.browser.navigate_to("https://internshala.com/login")
            
            # Wait for login form
            if not await self.browser.wait_for_selector("#email", timeout=15000):
                self.logger.error("Login form not found")
                return False
            
            # Fill credentials
            await self.browser.fill("#email", email)
            await self.browser.fill("#password", password)
            
            # Submit form
            await self.browser.click("button[type='submit']")
            
            # Wait for redirect after login
            await asyncio.sleep(3)
            
            # Check if login was successful
            if await self.browser.wait_for_selector(".user_menu, .profile_container", timeout=10000):
                self.logger.info("Login successful")
                return True
            else:
                self.logger.error("Login failed - no user menu found")
                return False
                
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return False
    
    async def check_authentication(self) -> bool:
        """Check if user is already authenticated."""
        try:
            await self.browser.navigate_to("https://internshala.com/student/dashboard")
            
            # Look for authentication indicators
            return await self.browser.wait_for_selector(".user_menu, .profile_container, .dashboard", timeout=5000)
        
        except Exception:
            return False
    
    async def navigate_to_chats(self) -> bool:
        """Navigate to chat messages page."""
        try:
            await self.browser.navigate_to("https://internshala.com/student/chat")
            return await self.browser.wait_for_selector(".chat-container, .message-list", timeout=15000)
        except Exception as e:
            self.logger.error(f"Failed to navigate to chats: {e}")
            return False
    
    async def navigate_to_internships(self, search_params: Optional[Dict[str, Any]] = None) -> bool:
        """Navigate to internships page with optional search parameters."""
        try:
            if search_params:
                # Build search URL with parameters
                base_url = "https://internshala.com/internships"
                url_params = []
                
                if search_params.get("keywords"):
                    url_params.append(f"search={search_params['keywords'][0]}")
                if search_params.get("locations"):
                    url_params.append(f"location={search_params['locations'][0]}")
                
                url = f"{base_url}?{'&'.join(url_params)}" if url_params else base_url
            else:
                url = "https://internshala.com/internships"
            
            await self.browser.navigate_to(url)
            return await self.browser.wait_for_selector(".internship_meta, .individual_internship", timeout=15000)
            
        except Exception as e:
            self.logger.error(f"Failed to navigate to internships: {e}")
            return False
