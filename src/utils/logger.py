"""
Logging utility for the infotainment testing system.
Provides consistent logging with file output and console display.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
import yaml

class InfotainmentLogger:
    """Custom logger for the infotainment testing system."""
    
    def __init__(self, name: str = "infotainment_test", log_level: str = "INFO"):
        self.name = name
        self.log_level = getattr(logging, log_level.upper())
        
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Configure logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_level)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Add file handler
        self._setup_file_handler(log_dir)
        
        # Add console handler
        self._setup_console_handler()
        
        # Add formatter
        self._setup_formatter()
    
    def _setup_file_handler(self, log_dir: Path) -> None:
        """Setup file handler for logging to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"infotainment_test_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(self.log_level)
        self.logger.addHandler(file_handler)
    
    def _setup_console_handler(self) -> None:
        """Setup console handler for logging to stdout."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        self.logger.addHandler(console_handler)
    
    def _setup_formatter(self) -> None:
        """Setup formatter for log messages."""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        for handler in self.logger.handlers:
            handler.setFormatter(formatter)
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """Log critical message."""
        self.logger.critical(message)
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str = "") -> None:
        """Log performance metric with standardized format."""
        message = f"PERFORMANCE: {metric_name} = {value}{unit}"
        self.logger.info(message)
    
    def log_test_event(self, test_name: str, event_type: str, details: str = "") -> None:
        """Log test-related events."""
        message = f"TEST_EVENT: {test_name} - {event_type}"
        if details:
            message += f" - {details}"
        self.logger.info(message)
    
    def log_system_event(self, component: str, event: str, status: str = "OK") -> None:
        """Log system component events."""
        message = f"SYSTEM: {component} - {event} - {status}"
        self.logger.info(message)
    
    def log_error_with_context(self, error: Exception, context: str = "") -> None:
        """Log error with additional context information."""
        error_msg = f"ERROR: {type(error).__name__}: {str(error)}"
        if context:
            error_msg += f" | Context: {context}"
        self.logger.error(error_msg)

def setup_logging(name: str = "infotainment_test", log_level: str = "INFO") -> InfotainmentLogger:
    """Setup and return a configured logger instance."""
    return InfotainmentLogger(name, log_level)

def get_logger(name: str = "infotainment_test") -> logging.Logger:
    """Get a logger instance by name."""
    return logging.getLogger(name)

# Example usage
if __name__ == "__main__":
    # Test the logger
    logger = setup_logging("test_logger", "DEBUG")
    
    logger.info("Logger initialized successfully")
    logger.debug("This is a debug message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    logger.log_performance_metric("response_time", 0.125, "ms")
    logger.log_test_event("media_test", "started", "Testing media playback")
    logger.log_system_event("interface", "initialized", "OK") 