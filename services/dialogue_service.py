"""
Dialogue service for managing conversations with philosophers.
"""
from typing import Optional, Dict, Any
import logging
from models.dialogue import DialogueSession, Message, MessageType
from models.philosopher import PhilosopherFactory, PhilosopherType, Philosopher
from services.gemini_service import GeminiService, GeminiServiceError
from config.settings import settings

logger = logging.getLogger(__name__)

class DialogueService:
    """Service for managing dialogue sessions with philosophers."""
    
    def __init__(self, ai_service: GeminiService):
        """Initialize the dialogue service."""
        self.ai_service = ai_service
        self.max_history_length = settings.max_history_length
    
    def start_dialogue(self, philosopher_type: PhilosopherType) -> DialogueSession:
        """
        Start a new dialogue session with a philosopher.
        
        Args:
            philosopher_type: The type of philosopher to converse with
            
        Returns:
            A new dialogue session
        """
        try:
            philosopher = PhilosopherFactory.create_philosopher(philosopher_type)
            session = DialogueSession(philosopher_name=philosopher.name)
            
            # Add welcome message
            welcome_msg = self._generate_welcome_message(philosopher)
            session.add_philosopher_message(welcome_msg)
            
            logger.info(f"Started dialogue session with {philosopher.name}")
            return session
            
        except Exception as e:
            logger.error(f"Error starting dialogue with {philosopher_type}: {e}")
            raise DialogueServiceError(f"Failed to start dialogue: {e}")
    
    def send_message(self, session: DialogueSession, user_message: str) -> Message:
        """
        Send a message to the philosopher and get a response.
        
        Args:
            session: The dialogue session
            user_message: The user's message
            
        Returns:
            The philosopher's response message
        """
        try:
            # Add user message to session
            session.add_user_message(user_message)
            
            # Get philosopher and generate response
            philosopher_type = self._get_philosopher_type_from_name(session.philosopher_name)
            philosopher = PhilosopherFactory.create_philosopher(philosopher_type)
            
            # Prepare conversation history
            history = self._prepare_conversation_history(session)
            
            # Generate response
            response = self.ai_service.generate_response_sync(
                system_prompt=philosopher.get_system_prompt(),
                conversation_history=history,
                user_message=user_message
            )
            
            # Add philosopher response to session
            response_message = session.add_philosopher_message(response)
            
            # Trim history if needed
            self._trim_session_history(session)
            
            logger.debug(f"Generated response in dialogue with {philosopher.name}")
            return response_message
            
        except GeminiServiceError as e:
            logger.error(f"Gemini service error in dialogue: {e}")
            error_msg = f"I apologize, but I'm having trouble formulating a response right now. Error: {str(e)}"
            return session.add_philosopher_message(error_msg)
        except Exception as e:
            logger.error(f"Error in dialogue service: {e}")
            raise DialogueServiceError(f"Failed to process message: {e}")
    
    def get_philosopher_info(self, philosopher_type: PhilosopherType) -> Dict[str, Any]:
        """
        Get information about a philosopher.
        
        Args:
            philosopher_type: The philosopher type
            
        Returns:
            Philosopher information dictionary
        """
        try:
            profile = PhilosopherFactory.get_philosopher_info(philosopher_type)
            return {
                "name": profile.name,
                "era": profile.era,
                "nationality": profile.nationality,
                "key_concepts": profile.key_concepts,
                "famous_works": profile.famous_works,
                "philosophical_school": profile.philosophical_school,
                "description": profile.brief_description
            }
        except Exception as e:
            logger.error(f"Error getting philosopher info: {e}")
            raise DialogueServiceError(f"Failed to get philosopher info: {e}")
    
    def _generate_welcome_message(self, philosopher: Philosopher) -> str:
        """Generate a welcome message from the philosopher."""
        welcome_messages = {
            "Socrates": "Greetings, my friend! I am Socrates of Athens. I know nothing, yet I am eager to learn through our dialogue. What questions trouble your mind today?",
            "Plato": "Welcome, seeker of wisdom! I am Plato, student of Socrates. Let us explore the realm of Ideas and discover the truth that lies beyond the shadows. What philosophical matter shall we examine?",
            "Aristotle": "Greetings! I am Aristotle of Stagira. Through careful observation and logical reasoning, we can understand the world around us. What subject would you like to investigate together?",
            "Confucius": "Welcome, friend. I am Kong Qiu, whom you call Confucius. Let us discuss the cultivation of virtue and the path to a harmonious life. What wisdom do you seek?",
            "Marcus Aurelius": "Salve! I am Marcus Aurelius, Emperor of Rome and student of Stoic philosophy. In our brief time together, let us reflect on virtue, duty, and the art of living well. What weighs upon your mind?",
            "Immanuel Kant": "Guten Tag! I am Immanuel Kant from Königsberg. Through the power of reason, we can discover moral truths and understand the limits of human knowledge. What philosophical question shall we examine systematically?",
            "Friedrich Nietzsche": "Ah, another seeker! I am Friedrich Nietzsche. Let us question everything, destroy old idols, and perhaps create new values. What sacred cow shall we examine today?",
            "René Descartes": "Bonjour! I am René Descartes. Let us doubt everything until we find something certain, then build our knowledge upon that foundation. What truth shall we seek together?",
            "John Locke": "Good day! I am John Locke. Through experience and reason, we can understand both the natural world and the proper foundations of government. What matter would you like to explore?",
            "Karl Marx": "Greetings, comrade! I am Karl Marx. Let us examine the material conditions of society and work toward a more just world for all workers. What social question concerns you?"
        }
        
        return welcome_messages.get(philosopher.name, f"Greetings! I am {philosopher.name}. How may I share my philosophical insights with you today?")
    
    def _get_philosopher_type_from_name(self, name: str) -> PhilosopherType:
        """Get philosopher type from name."""
        name_to_type = {
            "Socrates": PhilosopherType.SOCRATES,
            "Plato": PhilosopherType.PLATO,
            "Aristotle": PhilosopherType.ARISTOTLE,
            "Confucius": PhilosopherType.CONFUCIUS,
            "Marcus Aurelius": PhilosopherType.MARCUS_AURELIUS,
            "Immanuel Kant": PhilosopherType.IMMANUEL_KANT,
            "Friedrich Nietzsche": PhilosopherType.FRIEDRICH_NIETZSCHE,
            "René Descartes": PhilosopherType.RENE_DESCARTES,
            "John Locke": PhilosopherType.JOHN_LOCKE,
            "Karl Marx": PhilosopherType.KARL_MARX
        }
        
        if name not in name_to_type:
            raise ValueError(f"Unknown philosopher name: {name}")
        
        return name_to_type[name]
    
    def _prepare_conversation_history(self, session: DialogueSession) -> list:
        """Prepare conversation history for AI model."""
        history = session.get_conversation_history(include_system=False)
        
        # Truncate if too long
        if len(history) > self.max_history_length:
            history = history[-self.max_history_length:]
        
        return self.ai_service.truncate_history(history)
    
    def _trim_session_history(self, session: DialogueSession) -> None:
        """Trim session history to prevent it from growing too large."""
        if len(session.messages) > self.max_history_length * 2:
            # Keep the first message (welcome) and the most recent messages
            welcome_msg = session.messages[0] if session.messages else None
            recent_messages = session.messages[-(self.max_history_length * 2 - 1):]
            
            session.messages = [welcome_msg] + recent_messages if welcome_msg else recent_messages

class DialogueServiceError(Exception):
    """Custom exception for dialogue service errors."""
    pass
