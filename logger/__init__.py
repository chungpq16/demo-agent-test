"""
Logger module for GenAI Application
Provides centralized logging configuration and management.
"""
import logging
import os
from datetime import datetime
from typing import Optional


class Logger:
    """Centralized logger configuration for the application."""
    
    _instance: Optional['Logger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize logger configuration."""
        if self._logger is None:
            self._setup_logger()
    
    def _setup_logger(self):
        """Setup logging configuration with file and console handlers."""
        # Get log level from environment or default to INFO
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        
        # Create logger
        self._logger = logging.getLogger('genai_app')
        self._logger.setLevel(getattr(logging, log_level, logging.INFO))
        
        # Prevent duplicate handlers
        if self._logger.handlers:
            return
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        
        # File handler
        log_filename = f"genai_app_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # Add handlers to logger
        self._logger.addHandler(console_handler)
        self._logger.addHandler(file_handler)
        
        self._logger.info(f"Logger initialized with level: {log_level}")
    
    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance."""
        return self._logger
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self._logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self._logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self._logger.critical(message, **kwargs)


# Convenience function to get logger instance
def get_logger() -> Logger:
    """Get the singleton logger instance."""
    return Logger()
