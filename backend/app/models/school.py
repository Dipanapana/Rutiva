import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class School(Base):
    """Schools for bulk purchases."""
    __tablename__ = "schools"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    emis_number = Column(String(20), unique=True, nullable=True)  # SA school identifier

    # Location
    province = Column(String(50), nullable=False)
    district = Column(String(100), nullable=True)
    address = Column(String(500), nullable=True)

    # Contact
    contact_name = Column(String(100), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(20), nullable=True)

    # Branding
    logo_url = Column(String(500), nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    orders = relationship("SchoolOrder", back_populates="school", lazy="dynamic")
    admins = relationship("SchoolAdmin", back_populates="school", lazy="dynamic")


class SchoolAdmin(Base):
    """Link users as school administrators."""
    __tablename__ = "school_admins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role = Column(String(20), default="admin")  # admin, teacher
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    school = relationship("School", back_populates="admins")
    user = relationship("User")


class SchoolOrder(Base):
    """Bulk orders for schools."""
    __tablename__ = "school_orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)

    # Order details
    learner_count = Column(Integer, nullable=False)
    price_per_learner_zar = Column(Integer, nullable=False)  # In cents
    total_zar = Column(Integer, nullable=False)  # In cents

    # Term info
    term = Column(Integer, nullable=True)  # 1, 2, 3, 4
    year = Column(Integer, nullable=False)

    # Payment
    payment_status = Column(String(20), default="pending")  # pending, paid, failed
    payment_reference = Column(String(100), nullable=True)
    invoice_url = Column(String(500), nullable=True)

    # Timestamps
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    school = relationship("School", back_populates="orders")
    product = relationship("Product")
    licenses = relationship("SchoolLicense", back_populates="order", lazy="dynamic")


class SchoolLicense(Base):
    """Individual learner licenses from bulk purchases."""
    __tablename__ = "school_licenses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("school_orders.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Assigned learner

    # License code for claiming
    license_code = Column(String(20), unique=True, nullable=False)
    is_claimed = Column(Boolean, default=False)
    claimed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    order = relationship("SchoolOrder", back_populates="licenses")
    user = relationship("User")
