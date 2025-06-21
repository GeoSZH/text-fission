import time
from typing import Optional, Dict, Any
from ..core.logger import Logger

logger = Logger.get_instance()

class TextFissionError(Exception):
    """Base exception class for TextFission"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
        
        # Log error
        logger.error(
            self.message,
            error_code=self.error_code,
            details=self.details
        )

class ConfigurationError(TextFissionError):
    """Configuration related errors"""
    pass

class ModelError(TextFissionError):
    """Model related errors"""
    pass

class GenerationError(TextFissionError):
    """Text generation related errors"""
    pass

class ProcessingError(TextFissionError):
    """Text processing related errors"""
    pass

class ValidationError(TextFissionError):
    """Validation related errors"""
    pass

class CacheError(TextFissionError):
    """Cache related errors"""
    pass

class ExportError(TextFissionError):
    """Export related errors"""
    pass

class APIError(TextFissionError):
    """API related errors"""
    pass

class ResourceError(TextFissionError):
    """Resource related errors"""
    pass

class TimeoutError(TextFissionError):
    """Timeout related errors"""
    pass

class RetryError(TextFissionError):
    """Retry related errors"""
    pass

class ErrorHandler:
    """Error handling utility class"""
    
    @staticmethod
    def handle_error(
        error: Exception,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> TextFissionError:
        """Convert exception to TextFissionError"""
        if isinstance(error, TextFissionError):
            return error
        
        # Map common exceptions to TextFissionError
        error_map = {
            ValueError: ValidationError,
            KeyError: ConfigurationError,
            FileNotFoundError: ResourceError,
            TimeoutError: TimeoutError,
            ConnectionError: APIError,
            MemoryError: ResourceError,
            PermissionError: ResourceError,
            NotImplementedError: ProcessingError
        }
        
        error_class = error_map.get(type(error), TextFissionError)
        return error_class(
            str(error),
            error_code=error_code,
            details=details
        )
    
    @staticmethod
    def retry_on_error(
        func,
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        error_codes: Optional[list] = None
    ):
        """Retry decorator for handling retryable errors"""
        def wrapper(*args, **kwargs):
            last_error = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except TextFissionError as e:
                    last_error = e
                    if error_codes and e.error_code not in error_codes:
                        raise
                    
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Retry attempt {attempt + 1} of {max_attempts}",
                            error_code=e.error_code,
                            delay=current_delay
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        raise RetryError(
                            f"Max retry attempts ({max_attempts}) exceeded",
                            error_code="MAX_RETRIES_EXCEEDED",
                            details={"last_error": str(last_error)}
                        )
                except Exception as e:
                    last_error = ErrorHandler.handle_error(e)
                    raise last_error
        
        return wrapper

class ErrorCodes:
    """Error code constants"""
    
    # Configuration errors
    INVALID_CONFIG = "INVALID_CONFIG"
    MISSING_CONFIG = "MISSING_CONFIG"
    INVALID_VALUE = "INVALID_VALUE"
    
    # Model errors
    MODEL_ERROR = "MODEL_ERROR"
    API_ERROR = "API_ERROR"
    RATE_LIMIT = "RATE_LIMIT"
    INVALID_RESPONSE = "INVALID_RESPONSE"
    
    # Generation errors
    GENERATION_ERROR = "GENERATION_ERROR"
    INVALID_PROMPT = "INVALID_PROMPT"
    INVALID_OUTPUT = "INVALID_OUTPUT"
    
    # Processing errors
    PROCESSING_ERROR = "PROCESSING_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    PROCESSING_TIMEOUT = "PROCESSING_TIMEOUT"
    
    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_FORMAT = "INVALID_FORMAT"
    MISSING_REQUIRED = "MISSING_REQUIRED"
    
    # Cache errors
    CACHE_ERROR = "CACHE_ERROR"
    CACHE_MISS = "CACHE_MISS"
    CACHE_FULL = "CACHE_FULL"
    
    # Export errors
    EXPORT_ERROR = "EXPORT_ERROR"
    INVALID_FORMAT = "INVALID_FORMAT"
    WRITE_ERROR = "WRITE_ERROR"
    
    # Resource errors
    RESOURCE_ERROR = "RESOURCE_ERROR"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    OUT_OF_MEMORY = "OUT_OF_MEMORY"
    
    # Timeout errors
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    OPERATION_TIMEOUT = "OPERATION_TIMEOUT"
    CONNECTION_TIMEOUT = "CONNECTION_TIMEOUT"
    
    # Retry errors
    RETRY_ERROR = "RETRY_ERROR"
    MAX_RETRIES_EXCEEDED = "MAX_RETRIES_EXCEEDED"
    RETRY_FAILED = "RETRY_FAILED" 