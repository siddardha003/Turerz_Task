"""
Chat message extraction and processing module.
Handles extraction, cleaning, and export of Internshala chat messages.
"""

import asyncio
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
import uuid

from src.browser.manager_selenium import BrowserManager
from src.models import ChatMessage, MessageDirection
from src.utils.logging import get_logger
from src.config import config


class ChatMessageExtractor:
    """Extracts and processes chat messages from Internshala."""
    
    def __init__(self, trace_id: Optional[str] = None):
        self.logger = get_logger(__name__, trace_id)
        self.browser_manager = BrowserManager(trace_id)
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.browser_manager.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.browser_manager.close()
    
    async def extract_all_messages(
        self, 
        limit: int = 100,
        include_sent: bool = True,
        include_received: bool = True
    ) -> List[ChatMessage]:
        """Extract all chat messages with filtering options."""
        self.logger.info(f"Starting chat message extraction (limit: {limit})")
        
        try:
            # Check authentication first
            if not await self.browser_manager.check_authentication():
                self.logger.error("User not authenticated - cannot extract messages")
                return []
            
            # Navigate to messages page
            await self.browser_manager.internshala_bot.browser.navigate_to(
                "https://internshala.com/student/messages"
            )
            
            # Wait for messages to load
            if not await self.browser_manager.internshala_bot.browser.wait_for_selector(
                ".messaging-container, .chat-container, .messages-list", timeout=15
            ):
                self.logger.warning("Messages page not found or not loaded")
                return []
            
            messages = []
            processed_conversations = 0
            
            # Get all conversation threads
            conversation_selectors = [
                ".chat-list .chat-item",
                ".conversation-list .conversation",
                ".message-threads .thread"
            ]
            
            conversation_elements = []
            for selector in conversation_selectors:
                elements = self.browser_manager.internshala_bot.browser.driver.find_elements(
                    self.browser_manager.internshala_bot.browser.driver.By.CSS_SELECTOR, 
                    selector
                )
                if elements:
                    conversation_elements = elements
                    self.logger.info(f"Found conversations using selector: {selector}")
                    break
            
            if not conversation_elements:
                self.logger.warning("No conversation threads found")
                return []
            
            self.logger.info(f"Found {len(conversation_elements)} conversation threads")
            
            # Process each conversation
            for i, conv_element in enumerate(conversation_elements):
                if len(messages) >= limit:
                    break
                    
                try:
                    self.logger.debug(f"Processing conversation {i + 1}")
                    
                    # Click on conversation to open it
                    conv_element.click()
                    await asyncio.sleep(2)  # Wait for messages to load
                    
                    # Extract messages from this conversation
                    conv_messages = await self._extract_conversation_messages(
                        conversation_id=f"conv_{i}",
                        include_sent=include_sent,
                        include_received=include_received
                    )
                    
                    messages.extend(conv_messages)
                    processed_conversations += 1
                    
                    self.logger.debug(f"Extracted {len(conv_messages)} messages from conversation {i + 1}")
                    
                    # Break if we've reached the limit
                    if len(messages) >= limit:
                        messages = messages[:limit]
                        break
                        
                except Exception as e:
                    self.logger.warning(f"Failed to process conversation {i}: {e}")
                    continue
            
            self.logger.info(f"Extraction complete: {len(messages)} messages from {processed_conversations} conversations")
            return messages
            
        except Exception as e:
            self.logger.error(f"Failed to extract chat messages: {e}")
            return []
    
    async def _extract_conversation_messages(
        self,
        conversation_id: str,
        include_sent: bool = True,
        include_received: bool = True
    ) -> List[ChatMessage]:
        """Extract messages from a single conversation."""
        messages = []
        
        try:
            # Wait for message container to load
            message_selectors = [
                ".chat-messages .message",
                ".conversation-messages .msg",
                ".message-list .message-item",
                ".messages .message-bubble"
            ]
            
            message_elements = []
            for selector in message_selectors:
                elements = self.browser_manager.internshala_bot.browser.driver.find_elements(
                    self.browser_manager.internshala_bot.browser.driver.By.CSS_SELECTOR,
                    selector
                )
                if elements:
                    message_elements = elements
                    break
            
            if not message_elements:
                self.logger.debug(f"No messages found in conversation {conversation_id}")
                return []
            
            current_url = self.browser_manager.internshala_bot.browser.current_url
            
            for msg_element in message_elements:
                try:
                    # Determine message direction
                    direction = self._determine_message_direction(msg_element)
                    
                    # Filter based on preferences
                    if direction == MessageDirection.SENT and not include_sent:
                        continue
                    if direction == MessageDirection.RECEIVED and not include_received:
                        continue
                    
                    # Extract message content
                    content = self._extract_message_content(msg_element)
                    if not content.strip():
                        continue
                    
                    # Extract sender information
                    sender = self._extract_sender_info(msg_element, direction)
                    
                    # Extract timestamp
                    timestamp = self._extract_timestamp(msg_element)
                    
                    # Extract attachments
                    attachments = self._extract_attachments(msg_element)
                    
                    # Create ChatMessage object
                    message = ChatMessage(
                        id=str(uuid.uuid4()),
                        sender=sender,
                        direction=direction,
                        timestamp=timestamp,
                        raw_text=content,
                        cleaned_text=self._clean_message_text(content),
                        attachments=attachments,
                        source_url=current_url
                    )
                    
                    messages.append(message)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to parse message in {conversation_id}: {e}")
                    continue
            
            return messages
            
        except Exception as e:
            self.logger.error(f"Failed to extract messages from conversation {conversation_id}: {e}")
            return []
    
    def _determine_message_direction(self, msg_element) -> MessageDirection:
        """Determine if message was sent or received."""
        try:
            # Check various indicators for message direction
            class_names = msg_element.get_attribute("class") or ""
            
            # Common patterns for sent messages
            sent_indicators = ["sent", "outgoing", "right", "own", "user"]
            received_indicators = ["received", "incoming", "left", "other", "company"]
            
            class_lower = class_names.lower()
            
            for indicator in sent_indicators:
                if indicator in class_lower:
                    return MessageDirection.SENT
            
            for indicator in received_indicators:
                if indicator in class_lower:
                    return MessageDirection.RECEIVED
            
            # Check parent elements for direction indicators
            parent = msg_element.find_element(msg_element.By.XPATH, "..")
            parent_class = parent.get_attribute("class") or ""
            
            for indicator in sent_indicators:
                if indicator in parent_class.lower():
                    return MessageDirection.SENT
            
            # Default to received if unclear
            return MessageDirection.RECEIVED
            
        except:
            return MessageDirection.RECEIVED
    
    def _extract_message_content(self, msg_element) -> str:
        """Extract the actual message text content."""
        try:
            # Try various selectors for message content
            content_selectors = [
                ".message-text",
                ".message-content", 
                ".msg-text",
                ".text",
                ".content"
            ]
            
            for selector in content_selectors:
                try:
                    content_elem = msg_element.find_element(msg_element.By.CSS_SELECTOR, selector)
                    return content_elem.text.strip()
                except:
                    continue
            
            # If no specific selector works, use the element text
            return msg_element.text.strip()
            
        except:
            return ""
    
    def _extract_sender_info(self, msg_element, direction: MessageDirection) -> str:
        """Extract sender name or information."""
        try:
            # Try to find sender name element
            sender_selectors = [
                ".sender-name",
                ".message-sender",
                ".from",
                ".author"
            ]
            
            for selector in sender_selectors:
                try:
                    sender_elem = msg_element.find_element(msg_element.By.CSS_SELECTOR, selector)
                    return sender_elem.text.strip()
                except:
                    continue
            
            # Fallback based on direction
            if direction == MessageDirection.SENT:
                return "You"
            else:
                return "Company Representative"
                
        except:
            return "Unknown"
    
    def _extract_timestamp(self, msg_element) -> datetime:
        """Extract message timestamp."""
        try:
            # Try various timestamp selectors
            time_selectors = [
                ".timestamp",
                ".message-time",
                ".time",
                ".date"
            ]
            
            for selector in time_selectors:
                try:
                    time_elem = msg_element.find_element(msg_element.By.CSS_SELECTOR, selector)
                    time_text = time_elem.text.strip()
                    
                    # Try to parse the timestamp
                    return self._parse_timestamp(time_text)
                except:
                    continue
            
            # If no timestamp found, use current time
            return datetime.now()
            
        except:
            return datetime.now()
    
    def _parse_timestamp(self, time_text: str) -> datetime:
        """Parse timestamp from various formats."""
        try:
            # Common timestamp patterns
            patterns = [
                "%H:%M",  # 14:30
                "%I:%M %p",  # 2:30 PM
                "%d/%m/%Y %H:%M",  # 08/09/2025 14:30
                "%Y-%m-%d %H:%M:%S",  # 2025-09-08 14:30:00
                "%b %d, %Y %I:%M %p"  # Sep 8, 2025 2:30 PM
            ]
            
            for pattern in patterns:
                try:
                    return datetime.strptime(time_text, pattern)
                except:
                    continue
            
            # If parsing fails, return current time
            return datetime.now()
            
        except:
            return datetime.now()
    
    def _extract_attachments(self, msg_element) -> List[str]:
        """Extract attachment URLs from message."""
        attachments = []
        
        try:
            # Look for attachment elements
            attachment_selectors = [
                ".attachment a",
                ".file-link",
                ".document-link",
                "a[href*='attachment']"
            ]
            
            for selector in attachment_selectors:
                try:
                    attachment_elements = msg_element.find_elements(
                        msg_element.By.CSS_SELECTOR, selector
                    )
                    for elem in attachment_elements:
                        href = elem.get_attribute("href")
                        if href:
                            attachments.append(href)
                except:
                    continue
                    
        except:
            pass
        
        return attachments
    
    def _clean_message_text(self, raw_text: str) -> str:
        """Clean and normalize message text."""
        if not raw_text:
            return ""
        
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', raw_text.strip())
        
        # Remove common artifacts
        cleaned = re.sub(r'^\s*[\[\(].*?[\]\)]\s*', '', cleaned)  # Remove [timestamp] patterns
        cleaned = re.sub(r'\s*\.\.\.\s*$', '', cleaned)  # Remove trailing ...
        
        return cleaned.strip()
    
    async def export_to_csv(
        self, 
        messages: List[ChatMessage], 
        filename: Optional[str] = None
    ) -> str:
        """Export chat messages to CSV file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"internshala_chat_messages_{timestamp}.csv"
        
        # Ensure exports directory exists
        exports_dir = Path("exports")
        exports_dir.mkdir(exist_ok=True)
        
        file_path = exports_dir / filename
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'id', 'sender', 'direction', 'timestamp', 
                    'cleaned_text', 'raw_text', 'attachments', 'source_url'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for message in messages:
                    writer.writerow({
                        'id': message.id,
                        'sender': message.sender,
                        'direction': message.direction.value,
                        'timestamp': message.timestamp.isoformat(),
                        'cleaned_text': message.cleaned_text,
                        'raw_text': message.raw_text,
                        'attachments': '; '.join(message.attachments),
                        'source_url': message.source_url
                    })
            
            self.logger.info(f"Exported {len(messages)} messages to {file_path}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"Failed to export messages to CSV: {e}")
            raise


class ChatMessageAnalyzer:
    """Analyzes extracted chat messages for insights."""
    
    def __init__(self, messages: List[ChatMessage]):
        self.messages = messages
        self.logger = get_logger(__name__)
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics about the chat messages."""
        if not self.messages:
            return {}
        
        sent_count = sum(1 for msg in self.messages if msg.direction == MessageDirection.SENT)
        received_count = len(self.messages) - sent_count
        
        # Get unique senders
        senders = set(msg.sender for msg in self.messages)
        
        # Get date range
        timestamps = [msg.timestamp for msg in self.messages]
        date_range = {
            'earliest': min(timestamps),
            'latest': max(timestamps)
        }
        
        return {
            'total_messages': len(self.messages),
            'sent_messages': sent_count,
            'received_messages': received_count,
            'unique_senders': len(senders),
            'senders_list': list(senders),
            'date_range': date_range,
            'messages_with_attachments': sum(1 for msg in self.messages if msg.attachments)
        }
    
    def find_messages_containing(self, keyword: str, case_sensitive: bool = False) -> List[ChatMessage]:
        """Find messages containing a specific keyword."""
        if not case_sensitive:
            keyword = keyword.lower()
        
        results = []
        for message in self.messages:
            text = message.cleaned_text if not case_sensitive else message.cleaned_text.lower()
            if keyword in text:
                results.append(message)
        
        return results
    
    def get_conversation_threads(self) -> Dict[str, List[ChatMessage]]:
        """Group messages by source URL (conversation thread)."""
        threads = {}
        
        for message in self.messages:
            url = message.source_url
            if url not in threads:
                threads[url] = []
            threads[url].append(message)
        
        # Sort messages in each thread by timestamp
        for url in threads:
            threads[url].sort(key=lambda msg: msg.timestamp)
        
        return threads
