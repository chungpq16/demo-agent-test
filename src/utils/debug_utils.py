"""
Enhanced logging configuration with debug capabilities.
"""

import logging
import os
import sys
from typing import Optional

def setup_logging(debug: bool = False, log_level: Optional[str] = None) -> logging.Logger:
    """
    Setup comprehensive logging configuration.
    
    Args:
        debug: Enable debug mode
        log_level: Override log level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Configured logger
    """
    # Determine log level
    if log_level:
        level = getattr(logging, log_level.upper(), logging.INFO)
    elif debug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Setup file handler for debug logs
    file_handler = logging.FileHandler('jira_chatbot_debug.log')
    file_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Add handlers
    root_logger.addHandler(console_handler)
    if debug:
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger('jira_client').setLevel(level)
    logging.getLogger('jira_agent').setLevel(level)
    logging.getLogger('chatbot').setLevel(level)
    logging.getLogger('jira_tools').setLevel(level)
    
    # Suppress some noisy libraries unless in debug mode
    if not debug:
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('httpcore').setLevel(logging.WARNING)
        logging.getLogger('httpx').setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging setup complete - Level: {logging.getLevelName(level)}")
    
    return logger

def get_debug_info() -> dict:
    """Get comprehensive debug information."""
    from config import config
    import platform
    
    debug_info = {
        'system': {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'working_directory': os.getcwd()
        },
        'configuration': config.get_config_summary(),
        'environment_variables': {
            'JIRA_SERVER_URL': bool(os.getenv('JIRA_SERVER_URL')),
            'JIRA_USERNAME': bool(os.getenv('JIRA_USERNAME')),
            'JIRA_API_TOKEN': bool(os.getenv('JIRA_API_TOKEN')),
            'OPENAI_API_KEY': bool(os.getenv('OPENAI_API_KEY')),
            'DEBUG': os.getenv('DEBUG', 'false').lower()
        }
    }
    
    return debug_info
