"""
===========================================================
Project: Agents-Rag
Developer: Yallaiah Onteru
Contact: yonteru414@gmail.com | GitHub: @https://yonteru414.github.io/Yallaiah-AI-ML-Engineer/ 
Support: yonteru.ai.engineer@gmail.com
===========================================================

Description:
------------
Logger Utility
Console and file logging helper with configurable levels.

Main Use:
---------
Centralized logging system that:
1. Provides structured logging across the application
2. Manages console and file output
3. Supports multiple log levels and formatting
4. Handles email processing and AI operation logging
"""

import logging
import os
from datetime import datetime
from typing import Optional
from config.settings import settings

class Logger:
    """Centralized logging utility."""
    
    def __init__(self, name: str = "AI_Agents"):
        """
        Initialize logger with console and file handlers.
        
        Args:
            name: Logger name
        """
        # =============== start __init__ ======
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up console and file handlers."""
        # =============== start _setup_handlers ======
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler(settings.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def info(self, message: str):
        """Log info message."""
        # =============== start info ======
        self.logger.info(message)
    
    def debug(self, message: str):
        """Log debug message - disabled for cleaner output."""
        pass
    
    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message."""
        self.logger.critical(message)
    
    def log_email_processing(self, sender_name: Optional[str], success: bool, error: Optional[str] = None):
        """
        Log email processing results.
        
        Args:
            sender_name: Name of the sender
            success: Whether processing was successful
            error: Error message if processing failed
        """
        if success:
            self.info(f"Email processed successfully for sender: {sender_name}")
        else:
            self.error(f"Email processing failed for sender: {sender_name}, Error: {error}")
    
    def log_ai_operation(self, operation: str, success: bool, details: Optional[str] = None):
        """
        Log AI operation results.
        
        Args:
            operation: Name of the AI operation
            success: Whether operation was successful
            details: Additional details about the operation
        """
        if success:
            self.info(f"AI operation '{operation}' completed successfully. {details or ''}")
        else:
            self.error(f"AI operation '{operation}' failed. {details or ''}")
    
    def log_service_status(self, service_name: str, available: bool, details: Optional[str] = None):
        """
        Log service availability status.
        
        Args:
            service_name: Name of the service
            available: Whether service is available
            details: Additional details about the service status
        """
        if available:
            self.info(f"Service '{service_name}' is available. {details or ''}")
        else:
            self.warning(f"Service '{service_name}' is not available. {details or ''}")

# Global logger instance
logger = Logger()
