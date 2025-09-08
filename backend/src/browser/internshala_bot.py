"""
Internshala-specific automation using Selenium WebDriver.
This provides all the functionality needed for our application.
"""

import asyncio
import time
from typing import List, Optional, Dict, Any
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.browser.selenium_manager import SeleniumBrowserManager
from src.models import ChatMessage, InternshipSummary
from src.utils.logging import get_logger


class InternshalaSeleniumBot:
    """Selenium-based automation for Internshala platform."""
    
    def __init__(self, trace_id: Optional[str] = None):
        self.logger = get_logger(__name__, trace_id)
        self.browser = SeleniumBrowserManager(trace_id)
        self.base_url = "https://internshala.com"
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.browser.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.browser.close()
    
    async def login(self, email: str, password: str) -> bool:
        """Login to Internshala account."""
        self.logger.info("Starting login process")
        
        try:
            # Navigate to login page
            await self.browser.navigate_to(f"{self.base_url}/login")
            
            # Wait for login form
            if not await self.browser.wait_for_selector("input[name='email']", timeout=10):
                self.logger.error("Login form not found")
                return False
            
            # Fill login form
            await self.browser.type_safe("input[name='email']", email)
            await self.browser.type_safe("input[name='password']", password)
            
            # Click login button
            if await self.browser.click_safe("button[type='submit']"):
                # Wait for redirect after login
                time.sleep(3)
                
                # Check if we're logged in successfully
                current_url = self.browser.current_url
                if "login" not in current_url and "internshala.com" in current_url:
                    self.logger.info("Login successful")
                    await self.browser.save_session()
                    return True
                else:
                    self.logger.error("Login failed - still on login page")
                    return False
            
            return False
            
        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            return False
    
    async def extract_chat_messages(self, limit: int = 50) -> List[ChatMessage]:
        """Extract chat messages from Internshala messaging system."""
        self.logger.info(f"Extracting chat messages (limit: {limit})")
        
        try:
            # Navigate to messages page
            await self.browser.navigate_to(f"{self.base_url}/student/messages")
            
            # Wait for messages to load
            if not await self.browser.wait_for_selector(".chat_list", timeout=15):
                self.logger.warning("Messages page not found or empty")
                return []
            
            messages = []
            
            # Get conversation list
            conversation_elements = self.browser.driver.find_elements(
                By.CSS_SELECTOR, ".chat_list .chat_item"
            )
            
            if not conversation_elements:
                self.logger.warning("No conversations found")
                return []
            
            self.logger.info(f"Found {len(conversation_elements)} conversations")
            
            # Process each conversation
            for i, conv_element in enumerate(conversation_elements[:10]):  # Limit conversations
                try:
                    # Click on conversation
                    conv_element.click()
                    time.sleep(2)
                    
                    # Wait for messages to load
                    await self.browser.wait_for_selector(".chat_messages", timeout=10)
                    
                    # Extract messages from this conversation
                    message_elements = self.browser.driver.find_elements(
                        By.CSS_SELECTOR, ".chat_messages .message"
                    )
                    
                    for msg_element in message_elements[-limit:]:  # Get latest messages
                        try:
                            # Extract message details
                            sender_elem = msg_element.find_element(By.CSS_SELECTOR, ".sender")
                            content_elem = msg_element.find_element(By.CSS_SELECTOR, ".content")
                            time_elem = msg_element.find_element(By.CSS_SELECTOR, ".time")
                            
                            message = ChatMessage(
                                sender=sender_elem.text.strip(),
                                content=content_elem.text.strip(),
                                timestamp=datetime.now(),  # Parse from time_elem.text if needed
                                conversation_id=f"conv_{i}",
                                platform="internshala"
                            )
                            
                            messages.append(message)
                            
                        except Exception as e:
                            self.logger.warning(f"Failed to parse message: {e}")
                            continue
                    
                    if len(messages) >= limit:
                        break
                        
                except Exception as e:
                    self.logger.warning(f"Failed to process conversation {i}: {e}")
                    continue
            
            self.logger.info(f"Extracted {len(messages)} chat messages")
            return messages
            
        except Exception as e:
            self.logger.error(f"Failed to extract chat messages: {e}")
            return []
    
    async def search_internships(
        self, 
        query: str = "", 
        location: str = "", 
        duration: str = "",
        stipend_min: Optional[int] = None,
        limit: int = 50
    ) -> List[InternshipSummary]:
        """Search for internships with filters."""
        self.logger.info(f"Searching internships: query='{query}', location='{location}'")
        
        try:
            # Navigate to internships page
            search_url = f"{self.base_url}/internships"
            await self.browser.navigate_to(search_url)
            
            # Wait for search page to load
            if not await self.browser.wait_for_selector("#internship_search", timeout=15):
                self.logger.error("Search page not loaded properly")
                return []
            
            # Apply search filters
            if query:
                await self.browser.type_safe("#internship_search", query)
                await self.browser.click_safe("button[type='submit']")
                time.sleep(3)
            
            if location:
                # Handle location filter if available
                location_filter = "#location_filter"
                if await self.browser.wait_for_selector(location_filter, timeout=5):
                    await self.browser.type_safe(location_filter, location)
            
            # Wait for results to load
            await self.browser.wait_for_selector(".internship_meta", timeout=10)
            
            # Scroll to load more results
            await self.browser.scroll_to_bottom(pause_time=2)
            
            # Extract internship listings
            internships = []
            internship_elements = self.browser.driver.find_elements(
                By.CSS_SELECTOR, ".internship_meta"
            )
            
            self.logger.info(f"Found {len(internship_elements)} internship listings")
            
            for element in internship_elements[:limit]:
                try:
                    # Extract internship details
                    title_elem = element.find_element(By.CSS_SELECTOR, ".internship_summary_title")
                    company_elem = element.find_element(By.CSS_SELECTOR, ".company_name")
                    location_elem = element.find_element(By.CSS_SELECTOR, ".location_name")
                    
                    # Try to extract stipend
                    stipend_text = ""
                    try:
                        stipend_elem = element.find_element(By.CSS_SELECTOR, ".stipend")
                        stipend_text = stipend_elem.text.strip()
                    except:
                        pass
                    
                    # Try to extract duration
                    duration_text = ""
                    try:
                        duration_elem = element.find_element(By.CSS_SELECTOR, ".duration")
                        duration_text = duration_elem.text.strip()
                    except:
                        pass
                    
                    # Try to extract apply by date
                    apply_by_text = ""
                    try:
                        apply_elem = element.find_element(By.CSS_SELECTOR, ".apply_by")
                        apply_by_text = apply_elem.text.strip()
                    except:
                        pass
                    
                    # Get internship URL
                    link_elem = element.find_element(By.CSS_SELECTOR, "a")
                    url = link_elem.get_attribute("href")
                    
                    # Create internship summary
                    internship = InternshipSummary(
                        title=title_elem.text.strip(),
                        company=company_elem.text.strip(),
                        location=location_elem.text.strip(),
                        duration=duration_text,
                        stipend=stipend_text,
                        apply_by=apply_by_text,
                        url=url,
                        platform="internshala",
                        scraped_at=datetime.now()
                    )
                    
                    # Apply stipend filter if specified
                    if stipend_min and internship.stipend_amount_min:
                        if internship.stipend_amount_min < stipend_min:
                            continue
                    
                    internships.append(internship)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to parse internship listing: {e}")
                    continue
            
            self.logger.info(f"Successfully extracted {len(internships)} internships")
            return internships
            
        except Exception as e:
            self.logger.error(f"Failed to search internships: {e}")
            return []
    
    async def get_detailed_internship(self, url: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific internship."""
        self.logger.info(f"Getting detailed internship info: {url}")
        
        try:
            await self.browser.navigate_to(url)
            
            # Wait for internship detail page
            if not await self.browser.wait_for_selector(".internship_details", timeout=10):
                self.logger.error("Internship details page not loaded")
                return None
            
            # Extract detailed information
            details = {}
            
            # Basic info
            details["title"] = await self.browser.get_text_content(".profile_name")
            details["company"] = await self.browser.get_text_content(".company_name")
            details["description"] = await self.browser.get_text_content(".description_text")
            
            # Requirements and skills
            details["skills"] = await self.browser.get_text_content(".skills_required")
            details["perks"] = await self.browser.get_text_content(".perks")
            
            # Application info
            details["total_applications"] = await self.browser.get_text_content(".applications_count")
            
            return details
            
        except Exception as e:
            self.logger.error(f"Failed to get detailed internship info: {e}")
            return None
    
    async def check_authentication(self) -> bool:
        """Check if user is currently authenticated."""
        try:
            await self.browser.navigate_to(f"{self.base_url}/student/dashboard")
            
            # If we can access dashboard, we're authenticated
            if await self.browser.wait_for_selector(".dashboard", timeout=5):
                self.logger.info("User is authenticated")
                return True
            else:
                self.logger.info("User is not authenticated")
                return False
                
        except Exception as e:
            self.logger.warning(f"Authentication check failed: {e}")
            return False
