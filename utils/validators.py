"""
Input validation utilities for the Philosopher Chat application.
"""
import re
from typing import Any, List, Optional, Union
from .exceptions import ValidationError

class InputValidator:
    """Utility class for validating user inputs."""
    
    @staticmethod
    def validate_non_empty_string(value: Any, field_name: str = "Input") -> str:
        """
        Validate that a value is a non-empty string.
        
        Args:
            value: The value to validate
            field_name: Name of the field for error messages
            
        Returns:
            The validated string
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be a string")
        
        if not value.strip():
            raise ValidationError(f"{field_name} cannot be empty")
        
        return value.strip()
    
    @staticmethod
    def validate_string_length(
        value: str, 
        min_length: int = 0, 
        max_length: int = 1000, 
        field_name: str = "Input"
    ) -> str:
        """
        Validate string length constraints.
        
        Args:
            value: The string to validate
            min_length: Minimum allowed length
            max_length: Maximum allowed length
            field_name: Name of the field for error messages
            
        Returns:
            The validated string
            
        Raises:
            ValidationError: If validation fails
        """
        if len(value) < min_length:
            raise ValidationError(f"{field_name} must be at least {min_length} characters long")
        
        if len(value) > max_length:
            raise ValidationError(f"{field_name} must be no more than {max_length} characters long")
        
        return value
    
    @staticmethod
    def validate_topic(topic: str) -> str:
        """
        Validate a debate or discussion topic.
        
        Args:
            topic: The topic to validate
            
        Returns:
            The validated topic
            
        Raises:
            ValidationError: If validation fails
        """
        topic = InputValidator.validate_non_empty_string(topic, "Topic")
        topic = InputValidator.validate_string_length(topic, min_length=3, max_length=200, field_name="Topic")
        
        # Check for inappropriate content patterns
        inappropriate_patterns = [
            r'\b(hate|violence|harm)\b',
            r'\b(illegal|criminal)\b',
            r'\b(explicit|nsfw)\b'
        ]
        
        for pattern in inappropriate_patterns:
            if re.search(pattern, topic.lower()):
                raise ValidationError("Topic contains inappropriate content")
        
        return topic
    
    @staticmethod
    def validate_message(message: str) -> str:
        """
        Validate a chat message.
        
        Args:
            message: The message to validate
            
        Returns:
            The validated message
            
        Raises:
            ValidationError: If validation fails
        """
        message = InputValidator.validate_non_empty_string(message, "Message")
        message = InputValidator.validate_string_length(message, min_length=1, max_length=2000, field_name="Message")
        
        # Check for spam patterns
        if len(set(message.lower())) < 3:  # Too repetitive
            raise ValidationError("Message appears to be spam or too repetitive")
        
        return message
    
    @staticmethod
    def validate_philosopher_selection(selection: Any, available_count: int) -> int:
        """
        Validate philosopher selection input.
        
        Args:
            selection: The selection input
            available_count: Number of available philosophers
            
        Returns:
            The validated selection index (0-based)
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            index = int(selection) - 1  # Convert to 0-based index
        except (ValueError, TypeError):
            raise ValidationError("Selection must be a valid number")
        
        if index < 0 or index >= available_count:
            raise ValidationError(f"Selection must be between 1 and {available_count}")
        
        return index
    
    @staticmethod
    def validate_multiple_selections(selections: str, available_count: int) -> List[int]:
        """
        Validate multiple philosopher selections.
        
        Args:
            selections: Comma-separated selection string
            available_count: Number of available philosophers
            
        Returns:
            List of validated selection indices (0-based)
            
        Raises:
            ValidationError: If validation fails
        """
        if not selections.strip():
            raise ValidationError("At least one selection is required")
        
        try:
            # Parse comma-separated values
            parts = [s.strip() for s in selections.split(',')]
            indices = []
            
            for part in parts:
                if not part:
                    continue
                
                index = int(part) - 1  # Convert to 0-based index
                if index < 0 or index >= available_count:
                    raise ValidationError(f"Selection {part} is out of range (1-{available_count})")
                
                if index in indices:
                    raise ValidationError(f"Duplicate selection: {part}")
                
                indices.append(index)
            
            if len(indices) < 2:
                raise ValidationError("At least 2 philosophers must be selected for a debate")
            
            if len(indices) > 5:
                raise ValidationError("Maximum 5 philosophers can participate in a debate")
            
            return indices
            
        except ValueError:
            raise ValidationError("Selections must be valid numbers separated by commas")
    
    @staticmethod
    def validate_session_id(session_id: Any) -> str:
        """
        Validate a session ID.
        
        Args:
            session_id: The session ID to validate
            
        Returns:
            The validated session ID
            
        Raises:
            ValidationError: If validation fails
        """
        session_id = InputValidator.validate_non_empty_string(session_id, "Session ID")
        
        # Basic UUID format validation
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if not re.match(uuid_pattern, session_id.lower()):
            raise ValidationError("Invalid session ID format")
        
        return session_id
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """
        Sanitize user input by removing potentially harmful content.
        
        Args:
            text: The text to sanitize
            
        Returns:
            The sanitized text
        """
        if not isinstance(text, str):
            return str(text)
        
        # Remove control characters except newlines and tabs
        sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        
        # Limit consecutive whitespace
        sanitized = re.sub(r'\s{10,}', ' ' * 10, sanitized)
        
        # Remove excessive punctuation
        sanitized = re.sub(r'[!?]{5,}', '!?!?', sanitized)
        
        return sanitized.strip()
    
    @staticmethod
    def validate_command(command: str) -> str:
        """
        Validate a command input.
        
        Args:
            command: The command to validate
            
        Returns:
            The validated command
            
        Raises:
            ValidationError: If validation fails
        """
        command = InputValidator.validate_non_empty_string(command, "Command")
        
        if not command.startswith('/'):
            raise ValidationError("Commands must start with '/'")
        
        # Validate command format
        command_pattern = r'^/[a-zA-Z][a-zA-Z0-9_]*$'
        if not re.match(command_pattern, command):
            raise ValidationError("Invalid command format")
        
        return command.lower()
    
    @staticmethod
    def validate_api_key(api_key: str) -> str:
        """
        Validate an OpenAI API key format.
        
        Args:
            api_key: The API key to validate
            
        Returns:
            The validated API key
            
        Raises:
            ValidationError: If validation fails
        """
        api_key = InputValidator.validate_non_empty_string(api_key, "API Key")
        
        # Basic OpenAI API key format validation
        if not api_key.startswith('sk-'):
            raise ValidationError("OpenAI API key must start with 'sk-'")
        
        if len(api_key) < 20:
            raise ValidationError("API key appears to be too short")
        
        return api_key
