"""
Debate management models for multi-philosopher conversations.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

from .dialogue import Message, MessageType
from .philosopher import PhilosopherType

class DebateStatus(Enum):
    """Status of a debate session."""
    PREPARING = "preparing"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"

@dataclass
class DebateParticipant:
    """Represents a participant in a debate."""
    philosopher_type: PhilosopherType
    name: str
    position: str = ""  # Their stance on the debate topic
    turn_count: int = 0
    last_response_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert participant to dictionary."""
        return {
            "philosopher_type": self.philosopher_type.value,
            "name": self.name,
            "position": self.position,
            "turn_count": self.turn_count,
            "last_response_time": self.last_response_time.isoformat() if self.last_response_time else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DebateParticipant":
        """Create participant from dictionary."""
        return cls(
            philosopher_type=PhilosopherType(data["philosopher_type"]),
            name=data["name"],
            position=data.get("position", ""),
            turn_count=data.get("turn_count", 0),
            last_response_time=datetime.fromisoformat(data["last_response_time"]) if data.get("last_response_time") else None
        )

@dataclass
class DebateSession:
    """Manages a debate session between multiple philosophers."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    topic: str = ""
    description: str = ""
    participants: List[DebateParticipant] = field(default_factory=list)
    messages: List[Message] = field(default_factory=list)
    current_speaker_index: int = 0
    status: DebateStatus = DebateStatus.PREPARING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    last_activity: datetime = field(default_factory=datetime.now)
    max_turns_per_participant: int = 3
    context: Dict[str, Any] = field(default_factory=dict)
    moderator_enabled: bool = True
    
    def add_participant(self, philosopher_type: PhilosopherType, position: str = "") -> DebateParticipant:
        """Add a participant to the debate."""
        from .philosopher import PhilosopherFactory
        
        philosopher = PhilosopherFactory.create_philosopher(philosopher_type)
        participant = DebateParticipant(
            philosopher_type=philosopher_type,
            name=philosopher.name,
            position=position
        )
        self.participants.append(participant)
        return participant
    
    def start_debate(self) -> None:
        """Start the debate session."""
        if len(self.participants) < 2:
            raise ValueError("At least 2 participants required for a debate")
        
        self.status = DebateStatus.ACTIVE
        self.started_at = datetime.now()
        self.last_activity = datetime.now()
        
        # Add opening system message
        opening_msg = f"Debate on '{self.topic}' has begun with {len(self.participants)} participants: {', '.join(p.name for p in self.participants)}"
        self.add_system_message(opening_msg)
    
    def add_message(self, message: Message) -> None:
        """Add a message to the debate."""
        self.messages.append(message)
        self.last_activity = datetime.now()
    
    def add_philosopher_message(self, philosopher_name: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        """Add a philosopher's message to the debate."""
        message = Message(
            type=MessageType.PHILOSOPHER,
            content=content,
            metadata={**(metadata or {}), "speaker": philosopher_name}
        )
        self.add_message(message)
        
        # Update participant turn count
        for participant in self.participants:
            if participant.name == philosopher_name:
                participant.turn_count += 1
                participant.last_response_time = datetime.now()
                break
        
        return message
    
    def add_user_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        """Add a user message to the debate."""
        message = Message(
            type=MessageType.USER,
            content=content,
            metadata=metadata or {}
        )
        self.add_message(message)
        return message
    
    def add_system_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        """Add a system message to the debate."""
        message = Message(
            type=MessageType.SYSTEM,
            content=content,
            metadata=metadata or {}
        )
        self.add_message(message)
        return message
    
    def get_current_speaker(self) -> Optional[DebateParticipant]:
        """Get the current speaker in the debate."""
        if not self.participants or self.status != DebateStatus.ACTIVE:
            return None
        
        return self.participants[self.current_speaker_index]
    
    def advance_speaker(self) -> Optional[DebateParticipant]:
        """Advance to the next speaker."""
        if not self.participants:
            return None
        
        self.current_speaker_index = (self.current_speaker_index + 1) % len(self.participants)
        return self.get_current_speaker()
    
    def is_debate_complete(self) -> bool:
        """Check if the debate should be completed."""
        if self.status != DebateStatus.ACTIVE:
            return False
        
        # Check if all participants have reached max turns
        for participant in self.participants:
            if participant.turn_count < self.max_turns_per_participant:
                return False
        
        return True
    
    def complete_debate(self) -> None:
        """Complete the debate session."""
        self.status = DebateStatus.COMPLETED
        self.completed_at = datetime.now()
        
        # Add closing system message
        closing_msg = f"Debate on '{self.topic}' has concluded. Each participant made {self.max_turns_per_participant} contributions."
        self.add_system_message(closing_msg)
    
    def pause_debate(self) -> None:
        """Pause the debate session."""
        self.status = DebateStatus.PAUSED
    
    def resume_debate(self) -> None:
        """Resume the debate session."""
        if self.status == DebateStatus.PAUSED:
            self.status = DebateStatus.ACTIVE
            self.last_activity = datetime.now()
    
    def get_debate_summary(self) -> Dict[str, Any]:
        """Get a summary of the debate."""
        philosopher_messages = {}
        for message in self.messages:
            if message.type == MessageType.PHILOSOPHER:
                speaker = message.metadata.get("speaker", "Unknown")
                if speaker not in philosopher_messages:
                    philosopher_messages[speaker] = 0
                philosopher_messages[speaker] += 1
        
        return {
            "id": self.id,
            "topic": self.topic,
            "description": self.description,
            "status": self.status.value,
            "participant_count": len(self.participants),
            "participants": [p.name for p in self.participants],
            "message_count": len(self.messages),
            "philosopher_messages": philosopher_messages,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "last_activity": self.last_activity.isoformat(),
            "current_speaker": self.get_current_speaker().name if self.get_current_speaker() else None
        }
    
    def get_conversation_history(self, include_system: bool = True) -> List[Dict[str, str]]:
        """Get conversation history formatted for AI model."""
        history = []
        for message in self.messages:
            if not include_system and message.type == MessageType.SYSTEM:
                continue
            
            if message.type == MessageType.PHILOSOPHER:
                speaker = message.metadata.get("speaker", "Philosopher")
                content = f"[{speaker}]: {message.content}"
            else:
                content = message.content
            
            role = "user" if message.type == MessageType.USER else "assistant"
            history.append({
                "role": role,
                "content": content
            })
        
        return history
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert debate session to dictionary."""
        return {
            "id": self.id,
            "topic": self.topic,
            "description": self.description,
            "participants": [p.to_dict() for p in self.participants],
            "messages": [msg.to_dict() for msg in self.messages],
            "current_speaker_index": self.current_speaker_index,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "last_activity": self.last_activity.isoformat(),
            "max_turns_per_participant": self.max_turns_per_participant,
            "context": self.context,
            "moderator_enabled": self.moderator_enabled
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DebateSession":
        """Create debate session from dictionary."""
        session = cls(
            id=data.get("id", str(uuid.uuid4())),
            topic=data.get("topic", ""),
            description=data.get("description", ""),
            current_speaker_index=data.get("current_speaker_index", 0),
            status=DebateStatus(data.get("status", "preparing")),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            last_activity=datetime.fromisoformat(data.get("last_activity", datetime.now().isoformat())),
            max_turns_per_participant=data.get("max_turns_per_participant", 3),
            context=data.get("context", {}),
            moderator_enabled=data.get("moderator_enabled", True)
        )
        
        # Reconstruct participants
        for participant_data in data.get("participants", []):
            session.participants.append(DebateParticipant.from_dict(participant_data))
        
        # Reconstruct messages
        for msg_data in data.get("messages", []):
            from .dialogue import Message
            session.messages.append(Message.from_dict(msg_data))
        
        return session
