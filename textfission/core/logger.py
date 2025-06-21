import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
import json
from logging.handlers import RotatingFileHandler
import os

class CustomFormatter(logging.Formatter):
    """Custom formatter for structured logging"""
    
    def format(self, record):
        """Format log record as JSON"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        return json.dumps(log_data)

class Logger:
    """Logger management class"""
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> "Logger":
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def setup(
        self,
        name: str = "textfission",
        level: int = logging.INFO,
        log_file: Optional[str] = None,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        console_output: bool = True
    ) -> logging.Logger:
        """Setup logger with specified configuration"""
        if self._logger is not None:
            return self._logger
        
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Create formatters
        json_formatter = CustomFormatter()
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
        # Add console handler if requested
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
        
        # Add file handler if log file specified
        if log_file:
            # Create log directory if it doesn't exist
            log_dir = os.path.dirname(log_file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
            
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8"
            )
            file_handler.setFormatter(json_formatter)
            logger.addHandler(file_handler)
        
        self._logger = logger
        return logger
    
    def get_logger(self) -> logging.Logger:
        """Get current logger instance"""
        if self._logger is None:
            self.setup()
        return self._logger
    
    def set_level(self, level: int) -> None:
        """Set logging level"""
        if self._logger is None:
            self.setup()
        self._logger.setLevel(level)
    
    def add_file_handler(
        self,
        log_file: str,
        level: int = logging.INFO,
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 5
    ) -> None:
        """Add file handler to logger"""
        if self._logger is None:
            self.setup()
        
        # Create log directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(CustomFormatter())
        self._logger.addHandler(file_handler)
    
    def remove_file_handler(self, log_file: str) -> None:
        """Remove file handler from logger"""
        if self._logger is None:
            return
        
        for handler in self._logger.handlers[:]:
            if isinstance(handler, RotatingFileHandler) and handler.baseFilename == log_file:
                self._logger.removeHandler(handler)
                handler.close()
    
    def log_with_context(self, level: int, message: str, **kwargs) -> None:
        """Log message with additional context"""
        if self._logger is None:
            self.setup()
        
        extra = {"extra": kwargs}
        self._logger.log(level, message, extra=extra)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with context"""
        self.log_with_context(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message with context"""
        self.log_with_context(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with context"""
        self.log_with_context(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message with context"""
        self.log_with_context(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message with context"""
        self.log_with_context(logging.CRITICAL, message, **kwargs)
    
    def exception(self, message: str, **kwargs) -> None:
        """Log exception message with context"""
        if self._logger is None:
            self.setup()
        
        extra = {"extra": kwargs}
        self._logger.exception(message, extra=extra) 