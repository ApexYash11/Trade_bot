"""
Logging filter to redact sensitive information from logs.
Prevents API keys and secrets from being exposed in log files.
"""

import logging
import os
import re


class RedactingFilter(logging.Filter):
    """
    Logging filter that redacts sensitive information.
    
    Redacts:
    - API keys and secrets
    - Bearer tokens
    - Any environment variable values that look like credentials
    
    Uses pattern matching to identify and mask sensitive data.
    """
    
    def __init__(self):
        """Initialize the filter with patterns to redact."""
        super().__init__()
        
        # Get sensitive values from environment
        self.api_key = os.getenv("API_KEY", "")
        self.api_secret = os.getenv("API_SECRET", "")
        
        # Build patterns for sensitive data
        self.patterns = []
        
        if self.api_key:
            # Redact full API key and partial matches (first 8 chars at least)
            self.patterns.append(self.api_key)
            if len(self.api_key) > 8:
                self.patterns.append(self.api_key[:8] + ".*")
        
        if self.api_secret:
            # Redact full API secret and partial matches
            self.patterns.append(self.api_secret)
            if len(self.api_secret) > 8:
                self.patterns.append(self.api_secret[:8] + ".*")
        
        # Additional patterns
        self.patterns.extend([
            r"API[_-]?KEY[\"'\s]*[:=][\"'\s]*([A-Za-z0-9]+)",
            r"API[_-]?SECRET[\"'\s]*[:=][\"'\s]*([A-Za-z0-9]+)",
            r"Bearer\s+([A-Za-z0-9\._-]+)",
            r"Authorization[\"'\s]*[:=][\"'\s]*Bearer\s+([A-Za-z0-9\._-]+)",
            r"password[\"'\s]*[:=][\"'\s]*([A-Za-z0-9!@#$%^&*]+)",
        ])
    
    def filter(self, record):
        """
        Filter log record and redact sensitive information.
        
        Args:
            record: LogRecord to filter
            
        Returns:
            True (always allow the record through)
        """
        # Redact the message
        if record.msg:
            record.msg = self._redact(str(record.msg))
        
        # Redact any arguments
        if record.args:
            if isinstance(record.args, dict):
                record.args = {
                    k: self._redact(str(v)) for k, v in record.args.items()
                }
            elif isinstance(record.args, tuple):
                record.args = tuple(
                    self._redact(str(arg)) for arg in record.args
                )
        
        # Redact exc_info if present
        if record.exc_info:
            record.exc_text = self._redact(str(record.exc_info))
        
        return True
    
    def _redact(self, text):
        """
        Redact sensitive information from text.
        
        Args:
            text: Text to redact
            
        Returns:
            Text with sensitive info masked
        """
        redacted = text
        
        # Redact exact matches
        for pattern in self.patterns:
            if not pattern.startswith(r"["):  # Skip regex patterns for now
                redacted = redacted.replace(pattern, "***REDACTED***")
        
        # Redact regex patterns
        regex_patterns = [
            (r"API_KEY[\"'\s]*[:=][\"'\s]*([A-Za-z0-9]+)", r"API_KEY=***REDACTED***"),
            (r"API_SECRET[\"'\s]*[:=][\"'\s]*([A-Za-z0-9]+)", r"API_SECRET=***REDACTED***"),
            (r"Bearer\s+([A-Za-z0-9\._-]+)", r"Bearer ***REDACTED***"),
            (r"Authorization[\"'\s]*[:=][\"'\s]*Bearer\s+([A-Za-z0-9\._-]+)", 
             r"Authorization: Bearer ***REDACTED***"),
            (r"password[\"'\s]*[:=][\"'\s]*([A-Za-z0-9!@#$%^&*]+)", 
             r"password=***REDACTED***"),
        ]
        
        for pattern, replacement in regex_patterns:
            redacted = re.sub(pattern, replacement, redacted, flags=re.IGNORECASE)
        
        return redacted
