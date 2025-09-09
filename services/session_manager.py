"""
Session manager for handling dialogue and debate sessions.
"""
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
from models.dialogue import DialogueSession
from models.debate import DebateSession
from config.settings import settings

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages active dialogue and debate sessions."""
    
    def __init__(self):
        """Initialize the session manager."""
        self.dialogue_sessions: Dict[str, DialogueSession] = {}
        self.debate_sessions: Dict[str, DebateSession] = {}
        self.session_timeout = settings.session_timeout
    
    def add_dialogue_session(self, session: DialogueSession) -> str:
        """
        Add a dialogue session to the manager.
        
        Args:
            session: The dialogue session to add
            
        Returns:
            The session ID
        """
        self.dialogue_sessions[session.id] = session
        logger.info(f"Added dialogue session {session.id} with {session.philosopher_name}")
        return session.id
    
    def get_dialogue_session(self, session_id: str) -> Optional[DialogueSession]:
        """
        Get a dialogue session by ID.
        
        Args:
            session_id: The session ID
            
        Returns:
            The dialogue session or None if not found
        """
        session = self.dialogue_sessions.get(session_id)
        if session and session.is_expired(self.session_timeout):
            self.remove_dialogue_session(session_id)
            return None
        return session
    
    def remove_dialogue_session(self, session_id: str) -> bool:
        """
        Remove a dialogue session.
        
        Args:
            session_id: The session ID to remove
            
        Returns:
            True if session was removed, False if not found
        """
        if session_id in self.dialogue_sessions:
            del self.dialogue_sessions[session_id]
            logger.info(f"Removed dialogue session {session_id}")
            return True
        return False
    
    def add_debate_session(self, session: DebateSession) -> str:
        """
        Add a debate session to the manager.
        
        Args:
            session: The debate session to add
            
        Returns:
            The session ID
        """
        self.debate_sessions[session.id] = session
        logger.info(f"Added debate session {session.id} on topic: {session.topic}")
        return session.id
    
    def get_debate_session(self, session_id: str) -> Optional[DebateSession]:
        """
        Get a debate session by ID.
        
        Args:
            session_id: The session ID
            
        Returns:
            The debate session or None if not found
        """
        return self.debate_sessions.get(session_id)
    
    def remove_debate_session(self, session_id: str) -> bool:
        """
        Remove a debate session.
        
        Args:
            session_id: The session ID to remove
            
        Returns:
            True if session was removed, False if not found
        """
        if session_id in self.debate_sessions:
            del self.debate_sessions[session_id]
            logger.info(f"Removed debate session {session_id}")
            return True
        return False
    
    def get_active_dialogue_sessions(self) -> List[DialogueSession]:
        """
        Get all active dialogue sessions.
        
        Returns:
            List of active dialogue sessions
        """
        active_sessions = []
        expired_session_ids = []
        
        for session_id, session in self.dialogue_sessions.items():
            if session.is_expired(self.session_timeout):
                expired_session_ids.append(session_id)
            elif session.is_active:
                active_sessions.append(session)
        
        # Clean up expired sessions
        for session_id in expired_session_ids:
            self.remove_dialogue_session(session_id)
        
        return active_sessions
    
    def get_active_debate_sessions(self) -> List[DebateSession]:
        """
        Get all active debate sessions.
        
        Returns:
            List of active debate sessions
        """
        return [session for session in self.debate_sessions.values() 
                if session.status.value in ["preparing", "active", "paused"]]
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        expired_count = 0
        
        # Clean up dialogue sessions
        expired_dialogue_ids = []
        for session_id, session in self.dialogue_sessions.items():
            if session.is_expired(self.session_timeout):
                expired_dialogue_ids.append(session_id)
        
        for session_id in expired_dialogue_ids:
            self.remove_dialogue_session(session_id)
            expired_count += 1
        
        # Note: Debate sessions don't auto-expire based on time
        # They are managed by their status
        
        if expired_count > 0:
            logger.info(f"Cleaned up {expired_count} expired sessions")
        
        return expired_count
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about current sessions.
        
        Returns:
            Dictionary with session statistics
        """
        active_dialogues = self.get_active_dialogue_sessions()
        active_debates = self.get_active_debate_sessions()
        
        dialogue_philosophers = {}
        for session in active_dialogues:
            philosopher = session.philosopher_name
            dialogue_philosophers[philosopher] = dialogue_philosophers.get(philosopher, 0) + 1
        
        return {
            "total_dialogue_sessions": len(self.dialogue_sessions),
            "active_dialogue_sessions": len(active_dialogues),
            "total_debate_sessions": len(self.debate_sessions),
            "active_debate_sessions": len(active_debates),
            "philosophers_in_use": dialogue_philosophers,
            "session_timeout": self.session_timeout
        }
    
    def end_dialogue_session(self, session_id: str) -> bool:
        """
        End a dialogue session gracefully.
        
        Args:
            session_id: The session ID to end
            
        Returns:
            True if session was ended, False if not found
        """
        session = self.get_dialogue_session(session_id)
        if session:
            session.is_active = False
            session.add_system_message("Session ended by user.")
            logger.info(f"Ended dialogue session {session_id}")
            return True
        return False
    
    def pause_dialogue_session(self, session_id: str) -> bool:
        """
        Pause a dialogue session.
        
        Args:
            session_id: The session ID to pause
            
        Returns:
            True if session was paused, False if not found
        """
        session = self.get_dialogue_session(session_id)
        if session:
            session.is_active = False
            session.add_system_message("Session paused by user.")
            logger.info(f"Paused dialogue session {session_id}")
            return True
        return False
    
    def resume_dialogue_session(self, session_id: str) -> bool:
        """
        Resume a paused dialogue session.
        
        Args:
            session_id: The session ID to resume
            
        Returns:
            True if session was resumed, False if not found
        """
        session = self.get_dialogue_session(session_id)
        if session:
            session.is_active = True
            session.add_system_message("Session resumed by user.")
            logger.info(f"Resumed dialogue session {session_id}")
            return True
        return False
