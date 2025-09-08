"""
Date and time utilities for Internshala automation.
Handles date parsing, normalization, and relative date calculations.
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Tuple
import pytz

# Indian timezone for Internshala
IST = pytz.timezone('Asia/Kolkata')


def parse_relative_date(text: str) -> Optional[datetime]:
    """
    Parse relative date expressions like 'last 5 days', 'yesterday', etc.
    Returns datetime in IST timezone.
    """
    text = text.lower().strip()
    now = datetime.now(IST)
    
    # Pattern matching for common expressions
    patterns = [
        (r'last (\d+) days?', lambda m: now - timedelta(days=int(m.group(1)))),
        (r'past (\d+) days?', lambda m: now - timedelta(days=int(m.group(1)))),
        (r'(\d+) days? ago', lambda m: now - timedelta(days=int(m.group(1)))),
        (r'yesterday', lambda m: now - timedelta(days=1)),
        (r'last week', lambda m: now - timedelta(weeks=1)),
        (r'last month', lambda m: now - timedelta(days=30)),
        (r'today', lambda m: now.replace(hour=0, minute=0, second=0, microsecond=0)),
    ]
    
    for pattern, handler in patterns:
        match = re.search(pattern, text)
        if match:
            return handler(match)
    
    return None


def parse_internshala_date(date_text: str) -> Optional[datetime]:
    """
    Parse date formats commonly used on Internshala.
    Examples: "2 days ago", "1 week ago", "Dec 15, 2023"
    """
    date_text = date_text.strip()
    
    # Try relative date first
    relative_date = parse_relative_date(date_text)
    if relative_date:
        return relative_date
    
    # Try absolute date formats
    date_formats = [
        "%b %d, %Y",  # Dec 15, 2023
        "%B %d, %Y",  # December 15, 2023
        "%d/%m/%Y",   # 15/12/2023
        "%Y-%m-%d",   # 2023-12-15
        "%d-%m-%Y",   # 15-12-2023
    ]
    
    for fmt in date_formats:
        try:
            # Parse as naive datetime then localize to IST
            dt = datetime.strptime(date_text, fmt)
            return IST.localize(dt)
        except ValueError:
            continue
    
    return None


def parse_stipend_amount(stipend_text: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Parse stipend text to extract min and max amounts.
    
    Examples:
    - "₹5,000-10,000 /month" -> (5000.0, 10000.0)
    - "₹15,000 /month" -> (15000.0, 15000.0)
    - "Unpaid" -> (None, None)
    - "₹5K-10K /month" -> (5000.0, 10000.0)
    """
    if not stipend_text or stipend_text.lower() in ['unpaid', 'no stipend', '-']:
        return None, None
    
    # Clean the text - remove currency symbols and /month, /week
    cleaned = re.sub(r'[₹,]', '', stipend_text)
    cleaned = re.sub(r'/month|/week', '', cleaned).strip()
    
    # Handle K (thousands) notation before extracting numbers
    cleaned = re.sub(r'(\d+(?:\.\d+)?)k', r'\g<1>000', cleaned, flags=re.IGNORECASE)
    
    # Extract numbers (including decimals)
    numbers = re.findall(r'\d+(?:\.\d+)?', cleaned)
    
    if not numbers:
        return None, None
    
    # Convert to floats
    amounts = [float(num) for num in numbers]
    
    if len(amounts) == 1:
        return amounts[0], amounts[0]
    elif len(amounts) >= 2:
        return min(amounts), max(amounts)
    
    return None, None


def normalize_duration(duration_text: str) -> str:
    """
    Normalize duration text to standard format.
    
    Examples:
    - "3 months" -> "3 months"
    - "3-6 months" -> "3-6 months"
    - "6 Months" -> "6 months"
    """
    if not duration_text:
        return ""
    
    # Convert to lowercase and normalize spacing
    normalized = re.sub(r'\s+', ' ', duration_text.strip().lower())
    
    # Standardize month/week representations
    normalized = re.sub(r'\bmonths?\b', 'months', normalized)
    normalized = re.sub(r'\bweeks?\b', 'weeks', normalized)
    
    return normalized


def is_within_date_range(
    target_date: datetime,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    since_days: Optional[int] = None
) -> bool:
    """
    Check if target_date falls within the specified range.
    """
    now = datetime.now(IST)
    
    # Handle since_days
    if since_days:
        from_date = now - timedelta(days=since_days)
    
    # Default to_date is now
    if to_date is None:
        to_date = now
    
    # Check range
    if from_date and target_date < from_date:
        return False
    if to_date and target_date > to_date:
        return False
    
    return True
