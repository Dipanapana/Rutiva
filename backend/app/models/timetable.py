import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Integer, Text, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base


class Timetable(Base):
    """User's study timetables."""
    __tablename__ = "timetables"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)

    title = Column(String(255), nullable=True)
    exam_date = Column(Date, nullable=False)

    # Generation settings
    settings = Column(JSONB, nullable=False)
    # Example settings:
    # {
    #   "study_days": ["Monday", "Wednesday", "Friday", "Saturday"],
    #   "hours_per_session": 1.5,
    #   "preferred_time": "afternoon",
    #   "pace": "normal",
    #   "start_date": "2025-01-15"
    # }

    # Generated schedule
    schedule = Column(JSONB, nullable=False)
    # Contains the full schedule with sessions, milestones, etc.

    # Statistics
    total_sessions = Column(Integer, default=0)
    completed_sessions = Column(Integer, default=0)
    total_hours = Column(Integer, default=0)  # In minutes

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="timetables")
    product = relationship("Product")
    progress = relationship("TimetableProgress", back_populates="timetable", lazy="dynamic")

    @property
    def completion_percent(self) -> int:
        """Calculate completion percentage."""
        if self.total_sessions == 0:
            return 0
        return int((self.completed_sessions / self.total_sessions) * 100)


class TimetableProgress(Base):
    """Track progress on individual timetable sessions."""
    __tablename__ = "timetable_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timetable_id = Column(UUID(as_uuid=True), ForeignKey("timetables.id"), nullable=False, index=True)

    session_date = Column(Date, nullable=False)
    session_index = Column(Integer, nullable=False)  # Index in the schedule

    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    time_spent_minutes = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)

    # Rating/feedback
    difficulty_rating = Column(Integer, nullable=True)  # 1-5
    understanding_rating = Column(Integer, nullable=True)  # 1-5

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    timetable = relationship("Timetable", back_populates="progress")

    __table_args__ = (
        # Unique constraint on timetable + session
        {"sqlite_autoincrement": True},
    )
