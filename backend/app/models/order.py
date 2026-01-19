import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base
import secrets


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentProvider(str, enum.Enum):
    PAYFAST = "payfast"
    YOCO = "yoco"
    EFT = "eft"
    FREE = "free"  # For promo codes that make order free


def generate_order_number() -> str:
    """Generate a unique order number."""
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    random_part = secrets.token_hex(4).upper()
    return f"RT-{timestamp}-{random_part}"


class Order(Base):
    """One-time purchase orders."""
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    order_number = Column(String(30), unique=True, nullable=False, default=generate_order_number, index=True)

    # Status
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    payment_provider = Column(SQLEnum(PaymentProvider), nullable=True)
    payment_reference = Column(String(100), nullable=True)

    # Pricing (in cents)
    subtotal_zar = Column(Integer, nullable=False)
    discount_zar = Column(Integer, default=0)
    total_zar = Column(Integer, nullable=False)

    # Promo code
    promo_code_id = Column(UUID(as_uuid=True), ForeignKey("promo_codes.id"), nullable=True)

    # Timestamps
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", lazy="joined")
    promo_code = relationship("PromoCode")


class OrderItem(Base):
    """Individual items in an order."""
    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    bundle_id = Column(UUID(as_uuid=True), ForeignKey("bundles.id"), nullable=True)

    # Price at time of purchase (in cents)
    price_zar = Column(Integer, nullable=False)
    quantity = Column(Integer, default=1)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
    bundle = relationship("Bundle")


class UserLibrary(Base):
    """User's purchased products (their library)."""
    __tablename__ = "user_library"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)

    # Usage tracking
    download_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime, nullable=True)
    progress_percent = Column(Integer, default=0)  # Reading progress

    # Timestamps
    purchased_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="library")
    product = relationship("Product", back_populates="library_entries")
    order = relationship("Order")

    __table_args__ = (
        # Ensure user can't have duplicate products
        {"sqlite_autoincrement": True},
    )


class PromoCode(Base):
    """Promotional discount codes."""
    __tablename__ = "promo_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(30), unique=True, nullable=False, index=True)

    # Discount (either percent OR fixed amount)
    discount_percent = Column(Integer, nullable=True)  # e.g., 20 for 20%
    discount_amount_zar = Column(Integer, nullable=True)  # Fixed amount in cents

    # Validity
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    max_uses = Column(Integer, nullable=True)  # None = unlimited
    current_uses = Column(Integer, default=0)

    # Restrictions
    min_order_zar = Column(Integer, nullable=True)  # Minimum order amount
    product_ids = Column(UUID(as_uuid=True), nullable=True)  # Specific product only

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def is_valid(self) -> bool:
        """Check if promo code is currently valid."""
        now = datetime.utcnow()
        if not self.is_active:
            return False
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        if self.max_uses and self.current_uses >= self.max_uses:
            return False
        return True

    def calculate_discount(self, subtotal: int) -> int:
        """Calculate discount amount for a given subtotal."""
        if not self.is_valid:
            return 0
        if self.min_order_zar and subtotal < self.min_order_zar:
            return 0

        if self.discount_percent:
            return int(subtotal * self.discount_percent / 100)
        elif self.discount_amount_zar:
            return min(self.discount_amount_zar, subtotal)
        return 0


# Import Boolean at module level
from sqlalchemy import Boolean
