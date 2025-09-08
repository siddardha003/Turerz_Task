"""
Test our Selenium-based browser automation.
This will verify that ChromeDriver is working properly.
"""

import asyncio
from src.browser.selenium_manager import SeleniumBrowserManager
from src.utils.logging import get_logger


async def test_selenium_browser():
    """Test basic Selenium functionality."""
    logger = get_logger(__name__)
    
    try:
        logger.info("Testing Selenium browser setup...")
        
        async with SeleniumBrowserManager() as browser:
            # Test basic navigation
            await browser.navigate_to("https://internshala.com")
            
            # Check if page loaded
            title = browser.driver.title
            logger.info(f"Page title: {title}")
            
            # Test selector waiting
            if await browser.wait_for_selector("body", timeout=10):
                logger.info("✅ Page body found - Selenium is working!")
            else:
                logger.error("❌ Page body not found")
                return False
            
            # Take a test screenshot
            screenshot_path = await browser.take_screenshot("test_homepage")
            logger.info(f"Screenshot saved: {screenshot_path}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Selenium test failed: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(test_selenium_browser())
