"""
Custom exceptions for the Philosopher Chat application.
"""

class AgoraException(Exception):
    """Base exception class for the Agora application."""
    
    def __init__(self, message: str, error_code: str = None):
        """
        Initialize the exception.
        
        Args:
            message: The error message
            error_code: Optional error code for categorization
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
    
    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message

class ValidationError(AgoraException):
    """Exception raised for input validation errors."""
    
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")

class ConfigurationError(AgoraException):
    """Exception raised for configuration errors."""
    
    def __init__(self, message: str):
        super().__init__(message, "CONFIG_ERROR")

class ServiceError(AgoraException):
    """Exception raised for service-level errors."""
    
    def __init__(self, message: str, service_name: str = None):
        error_code = f"{service_name.upper()}_ERROR" if service_name else "SERVICE_ERROR"
        super().__init__(message, error_code)
        self.service_name = service_name

class SessionError(AgoraException):
    """Exception raised for session management errors."""
    
    def __init__(self, message: str):
        super().__init__(message, "SESSION_ERROR")

class PhilosopherError(AgoraException):
    """Exception raised for philosopher-related errors."""
    
    def __init__(self, message: str, philosopher_name: str = None):
        super().__init__(message, "PHILOSOPHER_ERROR")
        self.philosopher_name = philosopher_name
