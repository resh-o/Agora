"""
Dialogue management models for the Philosopher Chat application.
"""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

class MessageType(Enum):
    """Types of messages in a dialogue."""
    USER = "user"
    PHILOSOPHER = "philosopher"
    SYSTEM = "system"

@dataclass
class Message:
    """Represents a single message in a dialogue."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType = MessageType.USER
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create message from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            type=MessageType(data.get("type", "user")),
            content=data.get("content", ""),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            metadata=data.get("metadata", {})
        )

@dataclass
class DialogueSession:
    """Manages a dialogue session with a philosopher."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    philosopher_name: str = ""
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    
    def add_message(self, message: Message) -> None:
        """Add a message to the session."""
        self.messages.append(message)
        self.last_activity = datetime.now()
    
    def add_user_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        """Add a user message to the session."""
        message = Message(
            type=MessageType.USER,
            content=content,
            metadata=metadata or {}
        )
        self.add_message(message)
        return message
    
    def add_philosopher_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        """Add a philosopher message to the session."""
        message = Message(
            type=MessageType.PHILOSOPHER,
            content=content,
            metadata=metadata or {}
        )
        self.add_message(message)
        return message
    
    def add_system_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        """Add a system message to the session."""
        message = Message(
            type=MessageType.SYSTEM,
            content=content,
            metadata=metadata or {}
        )
        self.add_message(message)
        return message
    
    def get_recent_messages(self, limit: int = 10) -> List[Message]:
        """Get the most recent messages."""
        return self.messages[-limit:] if len(self.messages) > limit else self.messages
    
    def get_conversation_history(self, include_system: bool = False) -> List[Dict[str, str]]:
        """Get conversation history formatted for AI model."""
        history = []
        for message in self.messages:
            if not include_system and message.type == MessageType.SYSTEM:
                continue
            
            role = "user" if message.type == MessageType.USER else "assistant"
            history.append({
                "role": role,
                "content": message.content
            })
        
        return history
    
    def clear_history(self) -> None:
        """Clear all messages from the session."""
        self.messages.clear()
        self.last_activity = datetime.now()
    
    def is_expired(self, timeout_seconds: int) -> bool:
        """Check if session has expired."""
        time_diff = datetime.now() - self.last_activity
        return time_diff.total_seconds() > timeout_seconds
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the session."""
        user_messages = len([m for m in self.messages if m.type == MessageType.USER])
        philosopher_messages = len([m for m in self.messages if m.type == MessageType.PHILOSOPHER])
        
        return {
            "id": self.id,
            "philosopher_name": self.philosopher_name,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "message_count": len(self.messages),
            "user_messages": user_messages,
            "philosopher_messages": philosopher_messages,
            "is_active": self.is_active,
            "context": self.context
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "id": self.id,
            "philosopher_name": self.philosopher_name,
            "messages": [msg.to_dict() for msg in self.messages],
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "context": self.context,
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DialogueSession":
        """Create session from dictionary."""
        session = cls(
            id=data.get("id", str(uuid.uuid4())),
            philosopher_name=data.get("philosopher_name", ""),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            last_activity=datetime.fromisoformat(data.get("last_activity", datetime.now().isoformat())),
            context=data.get("context", {}),
            is_active=data.get("is_active", True)
        )
        
        # Reconstruct messages
        for msg_data in data.get("messages", []):
            session.messages.append(Message.from_dict(msg_data))
        
        return session
