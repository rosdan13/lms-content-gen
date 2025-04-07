import logging
import json
import os
from typing import Any, Dict, Optional
from google.cloud import logging as cloud_logging
from google.cloud.logging.handlers import CloudLoggingHandler
from google.cloud.logging_v2.handlers.transports.background_thread import BackgroundThreadTransport

# Determine if running in Google Cloud environment
IS_CLOUD_ENVIRONMENT = os.environ.get('K_SERVICE') is not None

class CustomCloudLogger:
    """Custom logger that sends logs to Google Cloud Logging when in cloud environment."""
    
    def __init__(self, name: str = "lms_ai_content"):
        self.logger_name = name
        self.logger = logging.getLogger(name)
        
        # Set up basic configuration
        self.logger.setLevel(logging.INFO)
        
        # Always add a console handler for local debugging
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # Only set up cloud logging if in cloud environment
        if IS_CLOUD_ENVIRONMENT:
            try:
                # Initialize the Google Cloud Logging client
                client = cloud_logging.Client()
                
                # Create a cloud logging handler with synchronous transport
                cloud_handler = CloudLoggingHandler(
                    client, 
                    name=self.logger_name,
                    transport=BackgroundThreadTransport
                )
                self.logger.addHandler(cloud_handler)
                
                # Log successful initialization
                self.logger.info("Cloud logging initialized successfully")
            except Exception as e:
                # If cloud logging setup fails, log to console
                console_handler.setLevel(logging.ERROR)
                self.logger.error(f"Failed to initialize cloud logging: {str(e)}")
    
    def _format_extra(self, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Format extra fields to include in structured logs."""
        formatted = extra or {}
        
        # Add default fields that might be useful
        if 'service' not in formatted:
            formatted['service'] = os.environ.get('K_SERVICE', 'lms-content-generator')
        
        return formatted
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log an info message with optional structured data."""
        self.logger.info(message, extra=self._format_extra(extra))
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log an error message with optional structured data."""
        self.logger.error(message, extra=self._format_extra(extra))
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log a warning message with optional structured data."""
        self.logger.warning(message, extra=self._format_extra(extra))
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log a debug message with optional structured data."""
        self.logger.debug(message, extra=self._format_extra(extra))
    
    def exception(self, message: str, exc_info=True, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log an exception with traceback and optional structured data."""
        self.logger.exception(message, exc_info=exc_info, extra=self._format_extra(extra))

# Create a singleton instance
logger = CustomCloudLogger()