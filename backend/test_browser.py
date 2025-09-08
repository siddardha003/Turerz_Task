"""
Test script for browser automation components.
Validates login flow and basic functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.browser.manager import BrowserManager
from src.browser.auth import InternshalaAuth
from src.browser.rate_limiter import get_rate_limiter, rate_limited_request
from src.config import config
from src.utils.logging import get_logger


async def test_browser_setup():
    """Test basic browser setup and navigation."""
    logger = get_logger(__name__)
    logger.info("Testing browser setup")
    
    try:
        async with BrowserManager() as browser:
            # Test basic navigation
            await browser.navigate_to("https://internshala.com")
            
            # Take screenshot
            screenshot_path = await browser.take_screenshot("homepage")
            logger.info(f"Homepage screenshot: {screenshot_path}")
            
            # Test selector waiting
            found = await browser.wait_for_selector("body", timeout=5000)
            assert found, "Could not find body element"
            
            logger.info("✅ Browser setup test passed")
            return True
            
    except Exception as e:
        logger.error(f"❌ Browser setup test failed: {e}")
        return False


async def test_rate_limiter():
    """Test rate limiting functionality."""
    logger = get_logger(__name__)
    logger.info("Testing rate limiter")
    
    try:
        rate_limiter = get_rate_limiter()
        
        # Test rapid requests
        start_time = asyncio.get_event_loop().time()
        
        for i in range(5):
            async with rate_limited_request(f"test_request_{i}"):
                logger.debug(f"Executed request {i}")
        
        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time
        
        logger.info(f"5 requests took {duration:.2f} seconds")
        
        # Get status
        status = await rate_limiter.get_status()
        logger.info(f"Rate limiter status: {status}")
        
        logger.info("✅ Rate limiter test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Rate limiter test failed: {e}")
        return False


async def test_login_flow():
    """Test Internshala login flow (requires valid credentials)."""
    logger = get_logger(__name__)
    logger.info("Testing login flow")
    
    # Check if credentials are configured
    if not config.internshala_email or config.internshala_email == "your_email@example.com":
        logger.warning("⚠️ Skipping login test - no credentials configured")
        return True
    
    try:
        async with BrowserManager() as browser:
            auth = InternshalaAuth(browser)
            
            # Check if already logged in
            already_logged_in = await auth.is_logged_in()
            logger.info(f"Already logged in: {already_logged_in}")
            
            if not already_logged_in:
                # Attempt login
                success, message = await auth.login()
                logger.info(f"Login result: {success} - {message}")
                
                if success:
                    # Verify login
                    verified = await auth.is_logged_in()
                    assert verified, "Login verification failed"
                    
                    logger.info("✅ Login flow test passed")
                    return True
                else:
                    logger.error(f"❌ Login failed: {message}")
                    return False
            else:
                logger.info("✅ Login flow test passed (already logged in)")
                return True
            
    except Exception as e:
        logger.error(f"❌ Login flow test failed: {e}")
        return False


async def main():
    """Run all browser automation tests."""
    logger = get_logger(__name__)
    logger.info("Starting browser automation tests")
    
    tests = [
        ("Browser Setup", test_browser_setup),
        ("Rate Limiter", test_rate_limiter),
        ("Login Flow", test_login_flow)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running test: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        logger.info("🎉 All tests passed! Browser automation is ready.")
    else:
        logger.error("⚠️ Some tests failed. Check configuration and network connectivity.")


if __name__ == "__main__":
    print("Turerz Browser Automation Test")
    print("=" * 40)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"❌ Test runner error: {e}")
