import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base


# Association table for bundle products
bundle_products = Table(
    "bundle_products",
    Base.metadata,
    Column("bundle_id", UUID(as_uuid=True), ForeignKey("bundles.id"), primary_key=True),
    Column("product_id", UUID(as_uuid=True), ForeignKey("products.id"), primary_key=True),
)


class Subject(Base):
    """Subject catalog (Mathematics, Physical Sciences, etc.)"""
    __tablename__ = "subjects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)  # MATH, PHYS, ENG, etc.
    description = Column(Text, nullable=True)
    icon_url = Column(String(500), nullable=True)
    color = Column(String(7), nullable=True)  # Hex color
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    products = relationship("Product", back_populates="subject", lazy="dynamic")


class Product(Base):
    """Study guide products."""
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku = Column(String(50), unique=True, nullable=False, index=True)  # e.g., "MATH-GR10-T1-2025"
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    short_description = Column(String(500), nullable=True)

    # Classification
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    grade = Column(Integer, nullable=False)  # 6-12
    term = Column(Integer, nullable=False)  # 1, 2, 3, 4 (0 for full year)
    year = Column(Integer, nullable=False)  # 2025, 2026, etc.

    # Pricing (in cents)
    price_zar = Column(Integer, nullable=False)
    sale_price_zar = Column(Integer, nullable=True)
    is_on_sale = Column(Boolean, default=False)

    # Content
    content_json = Column(JSONB, nullable=False)  # Full course breakdown
    pdf_url = Column(String(500), nullable=True)
    answer_key_url = Column(String(500), nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    preview_url = Column(String(500), nullable=True)  # Sample PDF for preview

    # Metadata
    total_pages = Column(Integer, nullable=True)
    total_hours = Column(Integer, nullable=True)  # Estimated study hours
    difficulty_level = Column(String(20), default="standard")  # foundation, standard, extended

    # Status
    is_published = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subject = relationship("Subject", back_populates="products")
    bundles = relationship("Bundle", secondary=bundle_products, back_populates="products")
    library_entries = relationship("UserLibrary", back_populates="product", lazy="dynamic")

    @property
    def current_price(self) -> int:
        """Get current price (sale or regular)."""
        if self.is_on_sale and self.sale_price_zar:
            return self.sale_price_zar
        return self.price_zar

    @property
    def discount_percent(self) -> int:
        """Calculate discount percentage if on sale."""
        if self.is_on_sale and self.sale_price_zar:
            return int(((self.price_zar - self.sale_price_zar) / self.price_zar) * 100)
        return 0


class Bundle(Base):
    """Product bundles (e.g., full year, all subjects)."""
    __tablename__ = "bundles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Pricing (in cents)
    price_zar = Column(Integer, nullable=False)
    original_price_zar = Column(Integer, nullable=True)  # Sum of individual products

    thumbnail_url = Column(String(500), nullable=True)
    is_published = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    products = relationship("Product", secondary=bundle_products, back_populates="bundles")

    @property
    def savings(self) -> int:
        """Calculate savings compared to buying individually."""
        if self.original_price_zar:
            return self.original_price_zar - self.price_zar
        return 0

    @property
    def discount_percent(self) -> int:
        """Calculate discount percentage."""
        if self.original_price_zar:
            return int(((self.original_price_zar - self.price_zar) / self.original_price_zar) * 100)
        return 0
