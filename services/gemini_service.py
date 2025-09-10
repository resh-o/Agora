"""
Gemini AI service for handling Google Generative AI interactions.
"""
import google.generativeai as genai
from typing import List, Dict, Any, Optional
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

class GeminiService:
    """Service for handling Gemini AI model interactions."""
    
    def __init__(self):
        """Initialize the Gemini service."""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.model_name)
        self.max_tokens = settings.max_tokens
        self.temperature = settings.temperature
    
    def generate_response_sync(
        self, 
        system_prompt: str, 
        conversation_history: List[Dict[str, str]], 
        user_message: str,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate a response from the Gemini model synchronously.
        
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
            if not settings.gemini_api_key:
                raise GeminiServiceError("Gemini API key is not properly configured")
            
            # Build the full prompt with system context and history
            full_prompt = self._build_prompt(system_prompt, conversation_history, user_message)
            
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=temperature or self.temperature,
                max_output_tokens=self.max_tokens,
                top_p=0.8,
                top_k=40
            )
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            if not response.text:
                raise GeminiServiceError("Empty response from Gemini API")
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise GeminiServiceError(f"Gemini API error: {e}")
    
    def _build_prompt(
        self, 
        system_prompt: str, 
        conversation_history: List[Dict[str, str]], 
        user_message: str
    ) -> str:
        """Build a complete prompt for Gemini from system prompt, history, and user message."""
        
        prompt_parts = [
            f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n",
            "CONVERSATION HISTORY:"
        ]
        
        # Add conversation history
        if conversation_history:
            for message in conversation_history:
                role = "Human" if message["role"] == "user" else "Assistant"
                prompt_parts.append(f"{role}: {message['content']}")
        else:
            prompt_parts.append("(No previous conversation)")
        
        # Add current user message
        prompt_parts.extend([
            f"\nCURRENT MESSAGE:",
            f"Human: {user_message}",
            f"\nAssistant:"
        ])
        
        return "\n".join(prompt_parts)
    
    def validate_api_key(self) -> bool:
        """
        Validate that the Gemini API key is working.
        
        Returns:
            True if API key is valid, False otherwise
        """
        try:
            test_model = genai.GenerativeModel('gemini-1.5-flash')
            response = test_model.generate_content("Hello")
            return bool(response.text)
        except Exception as e:
            logger.error(f"API key validation failed: {e}")
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

class GeminiServiceError(Exception):
    """Custom exception for Gemini service errors."""
    pass
