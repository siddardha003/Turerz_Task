"""
Alternative browser automation approach using Selenium WebDriver.
This avoids compilation issues while providing the same functionality.
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from src.config import config
from src.utils.logging import get_logger


class SeleniumBrowserManager:
    """Browser manager using Selenium WebDriver as Playwright alternative."""
    
    def __init__(self, trace_id: Optional[str] = None):
        self.logger = get_logger(__name__, trace_id)
        self.driver: Optional[webdriver.Chrome] = None
        self.session_file = Path("selenium_session.json")
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def start(self) -> None:
        """Initialize Chrome WebDriver."""
        self.logger.info("Starting Selenium Chrome browser")
        
        # Configure Chrome options
        chrome_options = Options()
        
        if config.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage") 
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # Set window size
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            # Initialize the driver with automatic driver management
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(10)
            
            # Load session if available
            self._load_session()
            
            self.logger.info("Selenium browser started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start browser: {e}")
            raise RuntimeError(f"Browser initialization failed: {e}")
    
    def _load_session(self) -> None:
        """Load existing session cookies."""
        if not self.session_file.exists():
            return
            
        try:
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            
            # Navigate to a base page first to set cookies
            self.driver.get("https://internshala.com")
            
            # Add cookies
            for cookie in session_data.get('cookies', []):
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    self.logger.warning(f"Failed to add cookie: {e}")
                    
            self.logger.info("Session cookies loaded")
            
        except Exception as e:
            self.logger.warning(f"Failed to load session: {e}")
    
    async def save_session(self) -> None:
        """Save current session cookies."""
        if not self.driver:
            return
            
        try:
            session_data = {
                'cookies': self.driver.get_cookies(),
                'current_url': self.driver.current_url
            }
            
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f)
                
            self.logger.info("Session saved")
            
        except Exception as e:
            self.logger.error(f"Failed to save session: {e}")
    
    async def close(self) -> None:
        """Close browser and save session."""
        if self.driver:
            await self.save_session()
            self.driver.quit()
            self.logger.info("Browser closed")
    
    async def navigate_to(self, url: str, wait_for: Optional[str] = None) -> None:
        """Navigate to a URL."""
        if not self.driver:
            raise RuntimeError("Browser not initialized")
        
        self.logger.info(f"Navigating to: {url}")
        self.driver.get(url)
        
        if wait_for:
            await self.wait_for_selector(wait_for, timeout=10)
        
        # Small delay for stability
        time.sleep(1)
    
    async def wait_for_selector(self, selector: str, timeout: int = 30) -> bool:
        """Wait for selector to be present."""
        if not self.driver:
            raise RuntimeError("Browser not initialized")
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            return True
        except TimeoutException:
            self.logger.warning(f"Selector not found: {selector}")
            return False
    
    async def click_safe(self, selector: str, timeout: int = 10) -> bool:
        """Click element with error handling."""
        if not self.driver:
            raise RuntimeError("Browser not initialized")
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            element.click()
            self.logger.debug(f"Clicked: {selector}")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to click {selector}: {e}")
            return False
    
    async def type_safe(self, selector: str, text: str, timeout: int = 10) -> bool:
        """Type text with error handling."""
        if not self.driver:
            raise RuntimeError("Browser not initialized")
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            element.clear()
            element.send_keys(text)
            self.logger.debug(f"Typed text in: {selector}")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to type in {selector}: {e}")
            return False
    
    async def get_text_content(self, selector: str) -> Optional[str]:
        """Get text content of element."""
        if not self.driver:
            return None
        
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            return element.text
        except NoSuchElementException:
            self.logger.warning(f"Element not found: {selector}")
            return None
    
    async def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """Get attribute value of element."""
        if not self.driver:
            return None
        
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            return element.get_attribute(attribute)
        except NoSuchElementException:
            self.logger.warning(f"Element not found: {selector}")
            return None
    
    async def scroll_to_bottom(self, pause_time: float = 1.0) -> None:
        """Scroll to bottom of page with pauses."""
        if not self.driver:
            return
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            # Scroll to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause_time)
            
            # Check if new content loaded
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            
            self.logger.debug(f"Scrolled to height: {new_height}")
    
    async def take_screenshot(self, name: str = "screenshot") -> str:
        """Take screenshot for debugging."""
        if not self.driver:
            return ""
        
        screenshot_path = Path(f"debug_{name}_{self.logger.trace_id}.png")
        self.driver.save_screenshot(str(screenshot_path))
        self.logger.info(f"Screenshot saved: {screenshot_path}")
        return str(screenshot_path)
    
    @property
    def current_url(self) -> str:
        """Get current page URL."""
        if not self.driver:
            return ""
        return self.driver.current_url
