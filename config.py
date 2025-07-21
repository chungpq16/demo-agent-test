"""
Configuration management for Jira AI Chatbot.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the Jira AI Chatbot application."""
    
    # Jira Configuration
    JIRA_SERVER_URL = os.getenv("JIRA_SERVER_URL")
    JIRA_USERNAME = os.getenv("JIRA_USERNAME") 
    JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.1"))
    
    # Application Configuration
    APP_TITLE = os.getenv("APP_TITLE", "Jira AI Chatbot")
    APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "AI-powered chatbot for Jira issue management")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # API Limits
    DEFAULT_ISSUE_LIMIT = int(os.getenv("DEFAULT_ISSUE_LIMIT", "100"))
    ANALYSIS_ISSUE_LIMIT = int(os.getenv("ANALYSIS_ISSUE_LIMIT", "200"))
    SEARCH_LIMIT = int(os.getenv("SEARCH_LIMIT", "50"))
    
    # Chat Configuration
    MAX_CHAT_HISTORY = int(os.getenv("MAX_CHAT_HISTORY", "20"))
    
    @classmethod
    def validate_required_config(cls) -> Dict[str, Any]:
        """
        Validate that all required configuration is present.
        
        Returns:
            Dictionary with validation results
        """
        required_fields = [
            ("JIRA_SERVER_URL", cls.JIRA_SERVER_URL),
            ("JIRA_USERNAME", cls.JIRA_USERNAME),
            ("JIRA_API_TOKEN", cls.JIRA_API_TOKEN),
            ("OPENAI_API_KEY", cls.OPENAI_API_KEY)
        ]
        
        missing = []
        configured = []
        
        for field_name, field_value in required_fields:
            if not field_value or field_value.startswith("your-"):
                missing.append(field_name)
            else:
                configured.append(field_name)
        
        return {
            "is_valid": len(missing) == 0,
            "missing": missing,
            "configured": configured,
            "total_required": len(required_fields)
        }
    
    @classmethod
    def get_config_summary(cls) -> Dict[str, Any]:
        """
        Get a summary of current configuration.
        
        Returns:
            Dictionary with configuration summary
        """
        validation = cls.validate_required_config()
        
        return {
            "app_title": cls.APP_TITLE,
            "app_description": cls.APP_DESCRIPTION,
            "debug_mode": cls.DEBUG,
            "openai_model": cls.OPENAI_MODEL,
            "openai_temperature": cls.OPENAI_TEMPERATURE,
            "issue_limits": {
                "default": cls.DEFAULT_ISSUE_LIMIT,
                "analysis": cls.ANALYSIS_ISSUE_LIMIT,
                "search": cls.SEARCH_LIMIT
            },
            "max_chat_history": cls.MAX_CHAT_HISTORY,
            "validation": validation
        }

# Create a global config instance
config = Config()
