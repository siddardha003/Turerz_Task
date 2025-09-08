"""
Test the chat message extraction functionality.
This tests the extraction logic without requiring actual login.
"""

import asyncio
from datetime import datetime
import uuid

from src.chat.extractor import ChatMessageExtractor, ChatMessageAnalyzer
from src.models import ChatMessage, MessageDirection
from src.utils.logging import get_logger


async def test_chat_extraction_demo():
    """Demo test of chat extraction with mock data."""
    logger = get_logger(__name__)
    
    logger.info("🧪 Testing Chat Extraction System")
    
    # Create mock chat messages for testing
    mock_messages = [
        ChatMessage(
            id=str(uuid.uuid4()),
            sender="You", 
            direction=MessageDirection.SENT,
            timestamp=datetime.now(),
            raw_text="Hi, I'm interested in the Python internship position.",
            cleaned_text="Hi, I'm interested in the Python internship position.",
            attachments=[],
            source_url="https://internshala.com/chat/123"
        ),
        ChatMessage(
            id=str(uuid.uuid4()),
            sender="TechCorp HR",
            direction=MessageDirection.RECEIVED,
            timestamp=datetime.now(),
            raw_text="Thank you for your interest! Can you tell us about your Python experience?",
            cleaned_text="Thank you for your interest! Can you tell us about your Python experience?",
            attachments=[],
            source_url="https://internshala.com/chat/123"
        ),
        ChatMessage(
            id=str(uuid.uuid4()),
            sender="You",
            direction=MessageDirection.SENT,
            timestamp=datetime.now(),
            raw_text="I have 2 years of experience with Python, Django, and Flask frameworks.",
            cleaned_text="I have 2 years of experience with Python, Django, and Flask frameworks.",
            attachments=["https://internshala.com/attachment/resume.pdf"],
            source_url="https://internshala.com/chat/123"
        ),
        ChatMessage(
            id=str(uuid.uuid4()),
            sender="StartupXYZ",
            direction=MessageDirection.RECEIVED,
            timestamp=datetime.now(),
            raw_text="Great! When would you be available for a quick interview?",
            cleaned_text="Great! When would you be available for a quick interview?",
            attachments=[],
            source_url="https://internshala.com/chat/456"
        )
    ]
    
    logger.info(f"✅ Created {len(mock_messages)} mock messages")
    
    # Test the analyzer
    analyzer = ChatMessageAnalyzer(mock_messages)
    stats = analyzer.get_summary_stats()
    
    logger.info("📊 Analysis Results:")
    logger.info(f"  Total messages: {stats['total_messages']}")
    logger.info(f"  Sent messages: {stats['sent_messages']}")
    logger.info(f"  Received messages: {stats['received_messages']}")
    logger.info(f"  Unique senders: {stats['unique_senders']}")
    logger.info(f"  Senders: {stats['senders_list']}")
    
    # Test keyword search
    python_messages = analyzer.find_messages_containing("python")
    logger.info(f"  Messages containing 'python': {len(python_messages)}")
    
    # Test conversation threads
    threads = analyzer.get_conversation_threads()
    logger.info(f"  Conversation threads: {len(threads)}")
    
    # Test CSV export (create mock extractor)
    try:
        # Create a temporary extractor just for export functionality
        temp_extractor = ChatMessageExtractor()
        
        csv_file = await temp_extractor.export_to_csv(mock_messages, "test_chat_export.csv")
        logger.info(f"✅ Exported to: {csv_file}")
        
    except Exception as e:
        logger.warning(f"CSV export test failed: {e}")
    
    logger.info("🎉 Chat extraction test completed!")
    return True


if __name__ == "__main__":
    asyncio.run(test_chat_extraction_demo())
