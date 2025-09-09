"""
AI service for handling OpenAI API interactions.
"""
import openai
from typing import List, Dict, Any, Optional
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

class AIService:
    """Service for handling AI model interactions."""
    
    def __init__(self):
        """Initialize the AI service with OpenAI client."""
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = settings.model_name
        self.max_tokens = settings.max_tokens
        self.temperature = settings.temperature
    
    async def generate_response(
        self, 
        system_prompt: str, 
        conversation_history: List[Dict[str, str]], 
        user_message: str,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate a response from the AI model.
        
        Args:
            system_prompt: The system prompt defining the philosopher's personality
            conversation_history: Previous conversation messages
            user_message: The current user message
            temperature: Optional temperature override
            
        Returns:
            The AI-generated response
        """
        try:
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": user_message})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=temperature or self.temperature,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise AIServiceError(f"AI service error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in AI service: {e}")
            raise AIServiceError(f"Unexpected error: {e}")
    
    def generate_response_sync(
        self, 
        system_prompt: str, 
        conversation_history: List[Dict[str, str]], 
        user_message: str,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate a response from the AI model synchronously.
        
        Args:
            system_prompt: The system prompt defining the philosopher's personality
            conversation_history: Previous conversation messages
            user_message: The current user message
            temperature: Optional temperature override
            
        Returns:
            The AI-generated response
        """
        try:
            # Validate API key first
            if not self.client.api_key or not self.client.api_key.startswith('sk-'):
                raise AIServiceError("OpenAI API key is not properly configured")
            
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": user_message})
            
            # Debug logging
            logger.info(f"Making API call with {len(messages)} messages")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=temperature or self.temperature,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            if not response.choices or not response.choices[0].message.content:
                raise AIServiceError("Empty response from OpenAI API")
            
            return response.choices[0].message.content.strip()
            
        except openai.AuthenticationError as e:
            logger.error(f"OpenAI Authentication error: {e}")
            raise AIServiceError(f"Invalid API key or authentication failed: {e}")
        except openai.RateLimitError as e:
            logger.error(f"OpenAI Rate limit error: {e}")
            raise AIServiceError(f"Rate limit exceeded: {e}")
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise AIServiceError(f"API error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in AI service: {e}")
            raise AIServiceError(f"Unexpected error: {e}")
    
    def validate_api_key(self) -> bool:
        """
        Validate that the OpenAI API key is working.
        
        Returns:
            True if API key is valid, False otherwise
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return True
        except openai.AuthenticationError:
            return False
        except Exception:
            return False
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in a text.
        Rough approximation: 1 token ≈ 4 characters
        
        Args:
            text: The text to estimate tokens for
            
        Returns:
            Estimated number of tokens
        """
        return len(text) // 4
    
    def truncate_history(self, history: List[Dict[str, str]], max_tokens: int = 2000) -> List[Dict[str, str]]:
        """
        Truncate conversation history to fit within token limits.
        
        Args:
            history: The conversation history
            max_tokens: Maximum tokens to keep
            
        Returns:
            Truncated history
        """
        if not history:
            return history
        
        total_tokens = 0
        truncated_history = []
        
        # Start from the most recent messages
        for message in reversed(history):
            message_tokens = self.estimate_tokens(message.get("content", ""))
            if total_tokens + message_tokens > max_tokens:
                break
            
            truncated_history.insert(0, message)
            total_tokens += message_tokens
        
        return truncated_history

class AIServiceError(Exception):
    """Custom exception for AI service errors."""
    pass
