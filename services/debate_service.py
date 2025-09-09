"""
Debate service for managing multi-philosopher conversations.
"""
from typing import List, Optional, Dict, Any
import logging
from models.debate import DebateSession, DebateParticipant, DebateStatus
from models.philosopher import PhilosopherFactory, PhilosopherType
from services.gemini_service import GeminiService, GeminiServiceError
from config.settings import settings

logger = logging.getLogger(__name__)

class DebateService:
    """Service for managing debate sessions between philosophers."""
    
    def __init__(self, ai_service: GeminiService):
        """Initialize the debate service."""
        self.ai_service = ai_service
        self.max_history_length = settings.max_history_length
    
    def create_debate(
        self, 
        topic: str, 
        description: str = "",
        philosopher_types: List[PhilosopherType] = None,
        max_turns_per_participant: int = 3
    ) -> DebateSession:
        """
        Create a new debate session.
        
        Args:
            topic: The debate topic
            description: Optional description of the debate
            philosopher_types: List of philosophers to include
            max_turns_per_participant: Maximum turns each philosopher gets
            
        Returns:
            A new debate session
        """
        try:
            session = DebateSession(
                topic=topic,
                description=description,
                max_turns_per_participant=max_turns_per_participant
            )
            
            # Add philosophers if provided
            if philosopher_types:
                for philosopher_type in philosopher_types:
                    session.add_participant(philosopher_type)
            
            logger.info(f"Created debate session on topic: {topic}")
            return session
            
        except Exception as e:
            logger.error(f"Error creating debate: {e}")
            raise DebateServiceError(f"Failed to create debate: {e}")
    
    def add_participant(
        self, 
        session: DebateSession, 
        philosopher_type: PhilosopherType, 
        position: str = ""
    ) -> DebateParticipant:
        """
        Add a participant to the debate.
        
        Args:
            session: The debate session
            philosopher_type: The philosopher to add
            position: Their position on the topic
            
        Returns:
            The added participant
        """
        try:
            participant = session.add_participant(philosopher_type, position)
            logger.info(f"Added {participant.name} to debate")
            return participant
            
        except Exception as e:
            logger.error(f"Error adding participant: {e}")
            raise DebateServiceError(f"Failed to add participant: {e}")
    
    def start_debate(self, session: DebateSession) -> None:
        """
        Start the debate session.
        
        Args:
            session: The debate session to start
        """
        try:
            session.start_debate()
            
            # Generate opening statements from each philosopher
            for participant in session.participants:
                opening_statement = self._generate_opening_statement(session, participant)
                session.add_philosopher_message(participant.name, opening_statement)
            
            logger.info(f"Started debate on: {session.topic}")
            
        except Exception as e:
            logger.error(f"Error starting debate: {e}")
            raise DebateServiceError(f"Failed to start debate: {e}")
    
    def get_next_response(self, session: DebateSession, user_input: str = "") -> Optional[str]:
        """
        Get the next response in the debate.
        
        Args:
            session: The debate session
            user_input: Optional user input to influence the debate
            
        Returns:
            The next philosopher's response, or None if debate is complete
        """
        try:
            if session.status != DebateStatus.ACTIVE:
                return None
            
            current_speaker = session.get_current_speaker()
            if not current_speaker:
                return None
            
            # Check if debate should be completed
            if session.is_debate_complete():
                session.complete_debate()
                return self._generate_closing_summary(session)
            
            # Generate response from current speaker
            response = self._generate_debate_response(session, current_speaker, user_input)
            session.add_philosopher_message(current_speaker.name, response)
            
            # Advance to next speaker
            session.advance_speaker()
            
            return response
            
        except GeminiServiceError as e:
            logger.error(f"Gemini service error in debate: {e}")
            return f"[{current_speaker.name if current_speaker else 'System'}]: I apologize, but I'm having difficulty formulating my response at the moment."
        except Exception as e:
            logger.error(f"Error getting next debate response: {e}")
            raise DebateServiceError(f"Failed to get debate response: {e}")
    
    def add_user_input(self, session: DebateSession, user_message: str) -> None:
        """
        Add user input to the debate.
        
        Args:
            session: The debate session
            user_message: The user's message or question
        """
        try:
            session.add_user_message(user_message)
            logger.info("Added user input to debate")
            
        except Exception as e:
            logger.error(f"Error adding user input: {e}")
            raise DebateServiceError(f"Failed to add user input: {e}")
    
    def pause_debate(self, session: DebateSession) -> None:
        """Pause the debate session."""
        session.pause_debate()
        logger.info("Debate paused")
    
    def resume_debate(self, session: DebateSession) -> None:
        """Resume the debate session."""
        session.resume_debate()
        logger.info("Debate resumed")
    
    def _generate_opening_statement(self, session: DebateSession, participant: DebateParticipant) -> str:
        """Generate an opening statement for a participant."""
        philosopher = PhilosopherFactory.create_philosopher(participant.philosopher_type)
        
        prompt = f"""You are participating in a philosophical debate on the topic: "{session.topic}"
        
        {session.description if session.description else ''}
        
        Your position (if any): {participant.position if participant.position else 'To be determined through dialogue'}
        
        Other participants: {', '.join(p.name for p in session.participants if p.name != participant.name)}
        
        Please provide a brief opening statement (2-3 sentences) introducing your perspective on this topic. 
        Stay true to your philosophical approach and historical context."""
        
        try:
            return self.ai_service.generate_response_sync(
                system_prompt=philosopher.get_system_prompt(),
                conversation_history=[],
                user_message=prompt,
                temperature=0.9
            )
        except Exception as e:
            logger.error(f"Error generating opening statement: {e}")
            return f"I am {participant.name}, and I look forward to exploring the topic of {session.topic} with my esteemed colleagues."
    
    def _generate_debate_response(
        self, 
        session: DebateSession, 
        participant: DebateParticipant, 
        user_input: str = ""
    ) -> str:
        """Generate a response from a participant in the debate."""
        philosopher = PhilosopherFactory.create_philosopher(participant.philosopher_type)
        
        # Prepare conversation history
        history = session.get_conversation_history(include_system=False)
        if len(history) > self.max_history_length:
            history = history[-self.max_history_length:]
        
        # Create context prompt
        other_participants = [p.name for p in session.participants if p.name != participant.name]
        context_prompt = f"""You are participating in a philosophical debate on: "{session.topic}"
        
        Other participants: {', '.join(other_participants)}
        
        This is turn {participant.turn_count + 1} of {session.max_turns_per_participant} for you.
        
        {"User input: " + user_input if user_input else ""}
        
        Please respond to the previous arguments and present your philosophical perspective. 
        Engage directly with what others have said while staying true to your philosophical approach.
        Keep your response focused and substantive (2-4 sentences)."""
        
        try:
            return self.ai_service.generate_response_sync(
                system_prompt=philosopher.get_system_prompt(),
                conversation_history=history,
                user_message=context_prompt,
                temperature=0.8
            )
        except Exception as e:
            logger.error(f"Error generating debate response: {e}")
            return f"I find this discussion most intriguing, though I must reflect further on the points raised."
    
    def _generate_closing_summary(self, session: DebateSession) -> str:
        """Generate a closing summary of the debate."""
        participants = [p.name for p in session.participants]
        
        summary_prompt = f"""The philosophical debate on "{session.topic}" has concluded with {len(participants)} participants: {', '.join(participants)}.
        
        Please provide a brief, neutral summary of the key philosophical positions that emerged during this debate. 
        Highlight the main points of agreement and disagreement between the philosophers.
        Keep it concise (3-4 sentences)."""
        
        try:
            return self.ai_service.generate_response_sync(
                system_prompt="You are a neutral moderator summarizing a philosophical debate.",
                conversation_history=session.get_conversation_history(include_system=False)[-10:],
                user_message=summary_prompt,
                temperature=0.7
            )
        except Exception as e:
            logger.error(f"Error generating closing summary: {e}")
            return f"The debate on {session.topic} has concluded. Each philosopher presented their unique perspective, contributing to a rich philosophical dialogue."

class DebateServiceError(Exception):
    """Custom exception for debate service errors."""
    pass
