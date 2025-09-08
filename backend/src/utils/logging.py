"""
Logging configuration for Internshala automation.
Provides structured logging with trace IDs.
"""

import logging
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.config import config


class TraceLogger:
    """Logger with trace ID support for request tracking."""
    
    def __init__(self, name: str, trace_id: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.trace_id = trace_id or str(uuid.uuid4())[:8]
    
    def _log(self, level: int, message: str, **kwargs):
        """Log message with trace ID."""
        extra = kwargs.get('extra', {})
        extra['trace_id'] = self.trace_id
        kwargs['extra'] = extra
        
        formatted_message = f"[{self.trace_id}] {message}"
        self.logger.log(level, formatted_message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self._log(logging.CRITICAL, message, **kwargs)


def setup_logging() -> None:
    """Configure application logging."""
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Console handler
            logging.StreamHandler(sys.stdout),
            # File handler
            logging.FileHandler(
                log_dir / f"internshala_automation_{datetime.now().strftime('%Y%m%d')}.log"
            )
        ]
    )
    
    # Set specific logger levels
    logging.getLogger("playwright").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str, trace_id: Optional[str] = None) -> TraceLogger:
    """Get a trace logger instance."""
    return TraceLogger(name, trace_id)


# Initialize logging on import
setup_logging()
