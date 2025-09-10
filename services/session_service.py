"""
Session persistence service for managing dialogue and debate sessions.
"""
import json
import os
from typing import List, Optional, Dict, Any, Union
from pathlib import Path
from datetime import datetime
import logging

from models.dialogue import DialogueSession
from models.debate import DebateSession
from utils.exceptions import SessionServiceError

logger = logging.getLogger(__name__)

class SessionService:
    """Service for persisting and managing dialogue and debate sessions."""
    
    def __init__(self, sessions_dir: str = "sessions"):
        """
        Initialize the session service.
        
        Args:
            sessions_dir: Directory to store session files
        """
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for different session types
        self.dialogue_dir = self.sessions_dir / "dialogues"
        self.debate_dir = self.sessions_dir / "debates"
        self.dialogue_dir.mkdir(exist_ok=True)
        self.debate_dir.mkdir(exist_ok=True)
    
    def save_dialogue_session(self, session: DialogueSession) -> str:
        """
        Save a dialogue session to disk.
        
        Args:
            session: The dialogue session to save
            
        Returns:
            The file path where the session was saved
        """
        try:
            filename = f"{session.id}.json"
            filepath = self.dialogue_dir / filename
            
            session_data = session.to_dict()
            session_data["session_type"] = "dialogue"
            session_data["saved_at"] = datetime.now().isoformat()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Dialogue session {session.id} saved to {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to save dialogue session {session.id}: {e}")
            raise SessionServiceError(f"Failed to save dialogue session: {e}")
    
    def save_debate_session(self, session: DebateSession) -> str:
        """
        Save a debate session to disk.
        
        Args:
            session: The debate session to save
            
        Returns:
            The file path where the session was saved
        """
        try:
            filename = f"{session.id}.json"
            filepath = self.debate_dir / filename
            
            session_data = session.to_dict()
            session_data["session_type"] = "debate"
            session_data["saved_at"] = datetime.now().isoformat()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Debate session {session.id} saved to {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to save debate session {session.id}: {e}")
            raise SessionServiceError(f"Failed to save debate session: {e}")
    
    def load_dialogue_session(self, session_id: str) -> DialogueSession:
        """
        Load a dialogue session from disk.
        
        Args:
            session_id: The ID of the session to load
            
        Returns:
            The loaded dialogue session
        """
        try:
            filepath = self.dialogue_dir / f"{session_id}.json"
            
            if not filepath.exists():
                raise SessionServiceError(f"Dialogue session {session_id} not found")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Verify it's a dialogue session
            if session_data.get("session_type") != "dialogue":
                raise SessionServiceError(f"File {filepath} is not a dialogue session")
            
            session = DialogueSession.from_dict(session_data)
            logger.debug(f"Dialogue session {session_id} loaded from {filepath}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to load dialogue session {session_id}: {e}")
            raise SessionServiceError(f"Failed to load dialogue session: {e}")
    
    def load_debate_session(self, session_id: str) -> DebateSession:
        """
        Load a debate session from disk.
        
        Args:
            session_id: The ID of the session to load
            
        Returns:
            The loaded debate session
        """
        try:
            filepath = self.debate_dir / f"{session_id}.json"
            
            if not filepath.exists():
                raise SessionServiceError(f"Debate session {session_id} not found")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Verify it's a debate session
            if session_data.get("session_type") != "debate":
                raise SessionServiceError(f"File {filepath} is not a debate session")
            
            session = DebateSession.from_dict(session_data)
            logger.debug(f"Debate session {session_id} loaded from {filepath}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to load debate session {session_id}: {e}")
            raise SessionServiceError(f"Failed to load debate session: {e}")
    
    def list_dialogue_sessions(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List all available dialogue sessions.
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List of session summaries
        """
        try:
            sessions = []
            
            for filepath in self.dialogue_dir.glob("*.json"):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    if session_data.get("session_type") == "dialogue":
                        summary = {
                            "id": session_data.get("id"),
                            "philosopher_name": session_data.get("philosopher_name", "Unknown"),
                            "created_at": session_data.get("created_at"),
                            "last_activity": session_data.get("last_activity"),
                            "message_count": len(session_data.get("messages", [])),
                            "is_active": session_data.get("is_active", False),
                            "saved_at": session_data.get("saved_at")
                        }
                        sessions.append(summary)
                        
                except Exception as e:
                    logger.warning(f"Failed to read session file {filepath}: {e}")
                    continue
            
            # Sort by last activity (most recent first)
            sessions.sort(key=lambda x: x.get("last_activity", ""), reverse=True)
            
            if limit:
                sessions = sessions[:limit]
            
            return sessions
            
        except Exception as e:
            logger.error(f"Failed to list dialogue sessions: {e}")
            raise SessionServiceError(f"Failed to list dialogue sessions: {e}")
    
    def list_debate_sessions(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List all available debate sessions.
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List of session summaries
        """
        try:
            sessions = []
            
            for filepath in self.debate_dir.glob("*.json"):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    if session_data.get("session_type") == "debate":
                        summary = {
                            "id": session_data.get("id"),
                            "topic": session_data.get("topic", "Unknown Topic"),
                            "status": session_data.get("status", "unknown"),
                            "participant_count": len(session_data.get("participants", [])),
                            "participants": [p.get("name", "Unknown") for p in session_data.get("participants", [])],
                            "created_at": session_data.get("created_at"),
                            "last_activity": session_data.get("last_activity"),
                            "message_count": len(session_data.get("messages", [])),
                            "saved_at": session_data.get("saved_at")
                        }
                        sessions.append(summary)
                        
                except Exception as e:
                    logger.warning(f"Failed to read session file {filepath}: {e}")
                    continue
            
            # Sort by last activity (most recent first)
            sessions.sort(key=lambda x: x.get("last_activity", ""), reverse=True)
            
            if limit:
                sessions = sessions[:limit]
            
            return sessions
            
        except Exception as e:
            logger.error(f"Failed to list debate sessions: {e}")
            raise SessionServiceError(f"Failed to list debate sessions: {e}")
    
    def delete_session(self, session_id: str, session_type: str) -> bool:
        """
        Delete a session from disk.
        
        Args:
            session_id: The ID of the session to delete
            session_type: Type of session ("dialogue" or "debate")
            
        Returns:
            True if session was deleted, False if not found
        """
        try:
            if session_type == "dialogue":
                filepath = self.dialogue_dir / f"{session_id}.json"
            elif session_type == "debate":
                filepath = self.debate_dir / f"{session_id}.json"
            else:
                raise SessionServiceError(f"Invalid session type: {session_type}")
            
            if filepath.exists():
                filepath.unlink()
                logger.debug(f"Deleted {session_type} session {session_id}")
                return True
            else:
                logger.debug(f"Session {session_id} not found for deletion")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            raise SessionServiceError(f"Failed to delete session: {e}")
    
    def auto_save_session(self, session: Union[DialogueSession, DebateSession]) -> str:
        """
        Automatically save a session (determines type automatically).
        
        Args:
            session: The session to save
            
        Returns:
            The file path where the session was saved
        """
        if isinstance(session, DialogueSession):
            return self.save_dialogue_session(session)
        elif isinstance(session, DebateSession):
            return self.save_debate_session(session)
        else:
            raise SessionServiceError(f"Unknown session type: {type(session)}")
    
    def search_sessions(self, query: str, session_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for sessions by content or metadata.
        
        Args:
            query: Search query
            session_type: Optional filter by session type ("dialogue" or "debate")
            
        Returns:
            List of matching session summaries
        """
        try:
            matching_sessions = []
            query_lower = query.lower()
            
            # Search dialogue sessions
            if not session_type or session_type == "dialogue":
                for session_summary in self.list_dialogue_sessions():
                    # Search in philosopher name and messages
                    if (query_lower in session_summary.get("philosopher_name", "").lower()):
                        session_summary["session_type"] = "dialogue"
                        matching_sessions.append(session_summary)
            
            # Search debate sessions
            if not session_type or session_type == "debate":
                for session_summary in self.list_debate_sessions():
                    # Search in topic and participant names
                    if (query_lower in session_summary.get("topic", "").lower() or
                        any(query_lower in name.lower() for name in session_summary.get("participants", []))):
                        session_summary["session_type"] = "debate"
                        matching_sessions.append(session_summary)
            
            # Sort by last activity
            matching_sessions.sort(key=lambda x: x.get("last_activity", ""), reverse=True)
            
            return matching_sessions
            
        except Exception as e:
            logger.error(f"Failed to search sessions: {e}")
            raise SessionServiceError(f"Failed to search sessions: {e}")
    
    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """
        Clean up sessions older than specified days.
        
        Args:
            days_old: Number of days after which to consider sessions old
            
        Returns:
            Number of sessions deleted
        """
        try:
            from datetime import timedelta
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            deleted_count = 0
            
            # Check dialogue sessions
            for session_summary in self.list_dialogue_sessions():
                try:
                    last_activity = datetime.fromisoformat(session_summary["last_activity"])
                    if last_activity < cutoff_date:
                        self.delete_session(session_summary["id"], "dialogue")
                        deleted_count += 1
                except Exception as e:
                    logger.warning(f"Failed to process dialogue session {session_summary['id']}: {e}")
            
            # Check debate sessions
            for session_summary in self.list_debate_sessions():
                try:
                    last_activity = datetime.fromisoformat(session_summary["last_activity"])
                    if last_activity < cutoff_date:
                        self.delete_session(session_summary["id"], "debate")
                        deleted_count += 1
                except Exception as e:
                    logger.warning(f"Failed to process debate session {session_summary['id']}: {e}")
            
            logger.debug(f"Cleaned up {deleted_count} old sessions")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old sessions: {e}")
            raise SessionServiceError(f"Failed to cleanup old sessions: {e}")
