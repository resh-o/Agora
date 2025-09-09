"""
Configuration settings for the Agora application.
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application configuration settings."""
    
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.app_name = os.getenv("APP_NAME", "Agora")
        self.debug = os.getenv("DEBUG", "False").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # AI Model Configuration
        self.model_name = "gemini-1.5-flash"
        self.max_tokens = 500
        self.temperature = 0.8
        
        # Session Configuration
        self.max_history_length = 20
        self.session_timeout = 3600  # 1 hour in seconds
        
    def validate(self) -> bool:
        """Validate that required settings are present."""
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required but not set")
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            "app_name": self.app_name,
            "debug": self.debug,
            "log_level": self.log_level,
            "model_name": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "max_history_length": self.max_history_length,
            "session_timeout": self.session_timeout
        }

# Global settings instance
settings = Settings()
