import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Date, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class UserRole(str, enum.Enum):
    STUDENT = "student"
    PARENT = "parent"
    SCHOOL_ADMIN = "school_admin"
    SUPER_ADMIN = "super_admin"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.STUDENT)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    grade = Column(Integer, nullable=True)  # 6-12 for students
    date_of_birth = Column(Date, nullable=True)
    province = Column(String(50), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)

    # Relationships
    orders = relationship("Order", back_populates="user", lazy="dynamic")
    library = relationship("UserLibrary", back_populates="user", lazy="dynamic")
    timetables = relationship("Timetable", back_populates="user", lazy="dynamic")
    tutor_subscription = relationship("TutorSubscription", back_populates="user", uselist=False)
    chat_sessions = relationship("ChatSession", back_populates="user", lazy="dynamic")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class OTPCode(Base):
    """Store OTP codes for verification."""
    __tablename__ = "otp_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    code = Column(String(10), nullable=False)
    purpose = Column(String(20), nullable=False)  # "email_verify", "password_reset", "login"
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ParentChild(Base):
    """Link parents to their children."""
    __tablename__ = "parent_children"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    child_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    relationship = Column(String(20), default="parent")
    created_at = Column(DateTime, default=datetime.utcnow)
