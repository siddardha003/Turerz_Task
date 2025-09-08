"""
Internshala authentication and session management.
Handles login flow and session validation.
"""

import asyncio
from typing import Optional, Tuple
from src.browser.manager import BrowserManager
from src.config import config
from src.utils.logging import get_logger


class InternshalaAuth:
    """Handles Internshala authentication and session management."""
    
    def __init__(self, browser_manager: BrowserManager):
        self.browser = browser_manager
        self.logger = get_logger(__name__, browser_manager.logger.trace_id)
        
        # Internshala selectors (may need updates based on current UI)
        self.selectors = {
            'login_button': 'a[href*="login"], .login-btn, button:has-text("Login")',
            'email_input': 'input[type="email"], input[name="email"], #email',
            'password_input': 'input[type="password"], input[name="password"], #password',
            'submit_button': 'button[type="submit"], .login-submit, button:has-text("Login")',
            'profile_indicator': '.profile-container, .user-menu, [data-testid="profile"]',
            'dashboard_indicator': '.dashboard, .student-dashboard, h1:has-text("Dashboard")',
            'logout_button': 'a:has-text("Logout"), .logout'
        }
    
    async def is_logged_in(self) -> bool:
        """Check if already logged in by looking for profile indicators."""
        self.logger.info("Checking login status")
        
        try:
            await self.browser.navigate_to("https://internshala.com/student/dashboard")
            
            # Look for dashboard or profile indicators
            indicators = [
                self.selectors['profile_indicator'],
                self.selectors['dashboard_indicator']
            ]
            
            for indicator in indicators:
                if await self.browser.wait_for_selector(indicator, timeout=5000):
                    self.logger.info("Already logged in")
                    return True
            
            # Check if redirected to login page
            current_url = self.browser.page.url if self.browser.page else ""
            if "login" in current_url.lower():
                self.logger.info("Not logged in - redirected to login page")
                return False
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Error checking login status: {e}")
            return False
    
    async def login(self) -> Tuple[bool, str]:
        """
        Perform login to Internshala.
        Returns (success, message) tuple.
        """
        self.logger.info("Starting login process")
        
        try:
            # Navigate to login page
            await self.browser.navigate_to("https://internshala.com/login/student")
            await asyncio.sleep(2)
            
            # Take screenshot for debugging
            await self.browser.take_screenshot("before_login")
            
            # Find and fill email
            email_filled = await self._fill_email()
            if not email_filled:
                return False, "Could not find or fill email field"
            
            # Find and fill password
            password_filled = await self._fill_password()
            if not password_filled:
                return False, "Could not find or fill password field"
            
            # Submit form
            submitted = await self._submit_login_form()
            if not submitted:
                return False, "Could not submit login form"
            
            # Wait for redirect and verify login
            await asyncio.sleep(3)
            success = await self._verify_login_success()
            
            if success:
                await self.browser.save_session()
                self.logger.info("Login successful")
                return True, "Login successful"
            else:
                await self.browser.take_screenshot("login_failed")
                return False, "Login failed - please check credentials"
                
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            await self.browser.take_screenshot("login_error")
            return False, f"Login error: {str(e)}"
    
    async def _fill_email(self) -> bool:
        """Fill email field with multiple selector attempts."""
        email_selectors = [
            'input[type="email"]',
            'input[name="email"]',
            '#email',
            'input[placeholder*="email" i]',
            '.email-input input'
        ]
        
        for selector in email_selectors:
            if await self.browser.wait_for_selector(selector, timeout=3000):
                success = await self.browser.type_safe(selector, config.internshala_email)
                if success:
                    self.logger.debug(f"Email filled using selector: {selector}")
                    return True
        
        self.logger.error("Could not find email input field")
        return False
    
    async def _fill_password(self) -> bool:
        """Fill password field with multiple selector attempts."""
        password_selectors = [
            'input[type="password"]',
            'input[name="password"]',
            '#password',
            'input[placeholder*="password" i]',
            '.password-input input'
        ]
        
        for selector in password_selectors:
            if await self.browser.wait_for_selector(selector, timeout=3000):
                success = await self.browser.type_safe(selector, config.internshala_password)
                if success:
                    self.logger.debug(f"Password filled using selector: {selector}")
                    return True
        
        self.logger.error("Could not find password input field")
        return False
    
    async def _submit_login_form(self) -> bool:
        """Submit login form with multiple selector attempts."""
        submit_selectors = [
            'button[type="submit"]',
            '.login-submit',
            'button:has-text("Login")',
            'input[type="submit"]',
            '.btn-primary',
            'form button'
        ]
        
        for selector in submit_selectors:
            if await self.browser.wait_for_selector(selector, timeout=3000):
                success = await self.browser.click_safe(selector)
                if success:
                    self.logger.debug(f"Form submitted using selector: {selector}")
                    return True
        
        # Try pressing Enter as fallback
        try:
            if self.browser.page:
                await self.browser.page.keyboard.press('Enter')
                self.logger.debug("Form submitted using Enter key")
                return True
        except Exception:
            pass
        
        self.logger.error("Could not submit login form")
        return False
    
    async def _verify_login_success(self) -> bool:
        """Verify login was successful by checking for dashboard elements."""
        # Wait for potential redirect
        await asyncio.sleep(2)
        
        # Check current URL
        current_url = self.browser.page.url if self.browser.page else ""
        self.logger.debug(f"Current URL after login: {current_url}")
        
        # Look for success indicators
        success_indicators = [
            '.dashboard',
            '.student-dashboard',
            '.profile-container',
            'h1:has-text("Dashboard")',
            '.user-menu',
            '[data-testid="profile"]'
        ]
        
        for indicator in success_indicators:
            if await self.browser.wait_for_selector(indicator, timeout=5000):
                self.logger.debug(f"Login verified with indicator: {indicator}")
                return True
        
        # Check if still on login page (indicates failure)
        if "login" in current_url.lower():
            return False
        
        # Check for error messages
        error_selectors = [
            '.error-message',
            '.alert-danger',
            '.login-error',
            '[class*="error"]'
        ]
        
        for selector in error_selectors:
            error_text = await self.browser.get_text_content(selector)
            if error_text:
                self.logger.warning(f"Login error detected: {error_text}")
                return False
        
        return True
    
    async def logout(self) -> bool:
        """Logout from Internshala."""
        self.logger.info("Logging out")
        
        try:
            # Look for logout link/button
            logout_selectors = [
                'a:has-text("Logout")',
                '.logout',
                '[href*="logout"]'
            ]
            
            for selector in logout_selectors:
                if await self.browser.wait_for_selector(selector, timeout=3000):
                    success = await self.browser.click_safe(selector)
                    if success:
                        await asyncio.sleep(2)
                        self.logger.info("Logout successful")
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Logout error: {e}")
            return False
