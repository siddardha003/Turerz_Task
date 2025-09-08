"""
Configuration management for Internshala automation.
Handles environment variables and application settings.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config(BaseSettings):
    """Application configuration."""
    
    # Internshala credentials
    internshala_email: str = Field(..., env="INTERNSHALA_EMAIL")
    internshala_password: str = Field(..., env="INTERNSHALA_PASSWORD")
    
    # OpenAI configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    
    # MCP configuration
    mcp_server_name: str = Field(default="internshala-automation", env="MCP_SERVER_NAME")
    mcp_server_version: str = Field(default="1.0.0", env="MCP_SERVER_VERSION")
    
    # Browser settings
    headless: bool = Field(default=True, env="HEADLESS")
    browser_timeout: int = Field(default=30000, env="BROWSER_TIMEOUT")
    
    # Data export settings
    csv_output_dir: str = Field(default="./exports", env="CSV_OUTPUT_DIR")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Rate limiting
    requests_per_minute: int = Field(default=30, env="REQUESTS_PER_MINUTE")
    concurrent_requests: int = Field(default=3, env="CONCURRENT_REQUESTS")
    
    # Derived properties
    @property
    def output_dir(self) -> Path:
        """Get output directory as Path object."""
        path = Path(self.csv_output_dir)
        path.mkdir(exist_ok=True)
        return path
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global configuration instance
config = Config()
