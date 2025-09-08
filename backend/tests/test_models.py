"""
Test cases for core data models.
"""

import pytest
from datetime import datetime
from src.models import ChatMessage, InternshipSummary, MessageDirection, InternshipMode
from src.utils.date_parser import parse_stipend_amount, parse_relative_date


def test_chat_message_creation():
    """Test ChatMessage model creation and validation."""
    message = ChatMessage(
        id="msg_123",
        sender="John Doe",
        direction=MessageDirection.SENT,
        timestamp=datetime.now(),
        raw_text="Hello, I'm interested in the internship.",
        cleaned_text="Hello, I'm interested in the internship.",
        source_url="https://internshala.com/chat/123"
    )
    
    assert message.id == "msg_123"
    assert message.direction == MessageDirection.SENT
    assert message.attachments == []  # Default empty list


def test_internship_summary_creation():
    """Test InternshipSummary model creation."""
    internship = InternshipSummary(
        id="int_456",
        title="Web Development Intern",
        company_name="TechCorp",
        location="Mumbai",
        mode=InternshipMode.HYBRID,
        stipend_text="₹10,000-15,000 /month",
        posted_date=datetime.now(),
        url="https://internshala.com/internship/detail/456"
    )
    
    assert internship.title == "Web Development Intern"
    assert internship.mode == InternshipMode.HYBRID
    assert internship.is_startup == False  # Default


def test_stipend_parsing():
    """Test stipend amount extraction."""
    test_cases = [
        ("₹5,000-10,000 /month", (5000.0, 10000.0)),
        ("₹15,000 /month", (15000.0, 15000.0)),
        ("Unpaid", (None, None)),
        ("₹5K-10K /month", (5000.0, 10000.0)),
        ("No stipend", (None, None))
    ]
    
    for stipend_text, expected in test_cases:
        result = parse_stipend_amount(stipend_text)
        assert result == expected, f"Failed for: {stipend_text}"


def test_relative_date_parsing():
    """Test relative date parsing."""
    # Test basic functionality
    result = parse_relative_date("last 5 days")
    assert result is not None
    
    result = parse_relative_date("yesterday")
    assert result is not None
    
    result = parse_relative_date("invalid date")
    assert result is None


if __name__ == "__main__":
    pytest.main([__file__])
