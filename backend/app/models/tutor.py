import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class TutorPlan(str, enum.Enum):
    STARTER = "starter"      # 15 questions/month
    STANDARD = "standard"    # 40 questions/month
    UNLIMITED = "unlimited"  # Unlimited


class TutorSubscription(Base):
    """Optional AI tutor subscription."""
    __tablename__ = "tutor_subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)

    plan = Column(SQLEnum(TutorPlan), nullable=False)
    questions_limit = Column(Integer, nullable=True)  # None for unlimited
    questions_used = Column(Integer, default=0)

    # Pricing (in cents)
    price_zar = Column(Integer, nullable=False)

    # Status
    status = Column(String(20), default="active")  # active, cancelled, expired
    payment_provider = Column(String(20), nullable=True)
    payment_reference = Column(String(100), nullable=True)

    # Billing period
    starts_at = Column(DateTime, nullable=False)
    ends_at = Column(DateTime, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="tutor_subscription")

    @property
    def questions_remaining(self) -> int | None:
        """Get remaining questions (None if unlimited)."""
        if self.questions_limit is None:
            return None
        return max(0, self.questions_limit - self.questions_used)

    @property
    def is_active(self) -> bool:
        """Check if subscription is currently active."""
        now = datetime.utcnow()
        return (
            self.status == "active" and
            self.starts_at <= now <= self.ends_at
        )

    @property
    def can_ask_question(self) -> bool:
        """Check if user can ask another question."""
        if not self.is_active:
            return False
        if self.questions_limit is None:
            return True  # Unlimited
        return self.questions_used < self.questions_limit


class ChatSession(Base):
    """AI tutor chat sessions."""
    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)

    # Context
    subject = Column(String(100), nullable=True)
    grade = Column(Integer, nullable=True)
    topic = Column(String(255), nullable=True)

    # Stats
    question_count = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)

    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    last_message_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    product = relationship("Product")
    messages = relationship("ChatMessage", back_populates="session", lazy="dynamic", order_by="ChatMessage.created_at")


class ChatMessage(Base):
    """Individual messages in a chat session."""
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False, index=True)

    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)

    # Token tracking
    tokens_used = Column(Integer, default=0)

    # Safety
    is_flagged = Column(Boolean, default=False)
    flag_reason = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")
