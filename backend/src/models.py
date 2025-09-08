"""
Core data models for Internshala automation.
Defines structured data types for chats and internships.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
import re


class MessageDirection(str, Enum):
    """Direction of a chat message."""
    SENT = "sent"
    RECEIVED = "received"


class InternshipMode(str, Enum):
    """Mode of internship work."""
    ON_SITE = "on-site"
    REMOTE = "remote"
    HYBRID = "hybrid"


class ChatMessage(BaseModel):
    """Represents a single chat message from Internshala."""
    
    id: str = Field(..., description="Unique message identifier")
    sender: str = Field(..., description="Name of message sender")
    direction: MessageDirection = Field(..., description="Message direction")
    timestamp: datetime = Field(..., description="Message timestamp")
    raw_text: str = Field(..., description="Original message text")
    cleaned_text: str = Field(..., description="Processed message text")
    attachments: List[str] = Field(default_factory=list, description="Attachment URLs")
    source_url: str = Field(..., description="URL of the chat page")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class InternshipSummary(BaseModel):
    """Summary information for an internship listing."""
    
    id: str = Field(..., description="Unique internship identifier")
    title: str = Field(..., description="Internship title/role")
    company_name: str = Field(..., description="Company name")
    location: str = Field(..., description="Location or 'Remote'")
    mode: InternshipMode = Field(..., description="Work mode")
    stipend_text: str = Field(..., description="Original stipend text")
    stipend_numeric_min: Optional[float] = Field(None, description="Minimum stipend amount")
    stipend_numeric_max: Optional[float] = Field(None, description="Maximum stipend amount")
    posted_date: datetime = Field(..., description="Date when posted")
    apply_by: Optional[datetime] = Field(None, description="Application deadline")
    url: str = Field(..., description="URL to internship page")
    is_startup: bool = Field(default=False, description="Whether company is a startup")
    tags: List[str] = Field(default_factory=list, description="Skill/category tags")
    
    def __init__(self, **data):
        # Auto-parse stipend if numeric values are not provided
        if 'stipend_text' in data and ('stipend_numeric_min' not in data or 'stipend_numeric_max' not in data):
            from src.utils.date_parser import parse_stipend_amount
            min_amt, max_amt = parse_stipend_amount(data['stipend_text'])
            if 'stipend_numeric_min' not in data:
                data['stipend_numeric_min'] = min_amt
            if 'stipend_numeric_max' not in data:
                data['stipend_numeric_max'] = max_amt
        super().__init__(**data)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class InternshipDetail(InternshipSummary):
    """Detailed information for a specific internship."""
    
    description: str = Field(..., description="Full internship description")
    responsibilities: List[str] = Field(default_factory=list, description="Key responsibilities")
    skills: List[str] = Field(default_factory=list, description="Required skills")
    openings: Optional[int] = Field(None, description="Number of openings")
    duration: str = Field(..., description="Internship duration")
    perks: List[str] = Field(default_factory=list, description="Additional perks")


class ChatFilter(BaseModel):
    """Filter criteria for chat messages."""
    
    since_days: Optional[int] = Field(None, ge=1, description="Messages from last N days")
    from_date: Optional[datetime] = Field(None, description="Start date")
    to_date: Optional[datetime] = Field(None, description="End date")
    keyword: Optional[str] = Field(None, description="Search keyword")
    min_stipend: Optional[float] = Field(None, description="Minimum stipend mentioned")
    limit: Optional[int] = Field(None, ge=1, le=1000, description="Maximum results")


class InternshipFilter(BaseModel):
    """Filter criteria for internship search."""
    
    role: Optional[str] = Field(None, description="Role/title filter")
    posted_within_days: Optional[int] = Field(None, ge=1, description="Posted within N days")
    category: Optional[str] = Field(None, description="Category filter")
    location: Optional[str] = Field(None, description="Location filter")
    remote: Optional[bool] = Field(None, description="Remote work filter")
    startup_only: Optional[bool] = Field(None, description="Startup companies only")
    min_stipend: Optional[float] = Field(None, description="Minimum stipend")
    limit: Optional[int] = Field(None, ge=1, le=500, description="Maximum results")


class ExportConfig(BaseModel):
    """Configuration for data export."""
    
    entity: str = Field(..., pattern="^(chats|internships)$", description="Entity type to export")
    file_path: Optional[str] = Field(None, description="Custom export path")
    include_metadata: bool = Field(default=True, description="Include metadata columns")
    timestamp_format: str = Field(default="ISO", description="Timestamp format")
