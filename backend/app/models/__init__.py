# Export all models for easy importing
from app.models.user import User, UserRole, OTPCode, ParentChild
from app.models.product import Subject, Product, Bundle, bundle_products
from app.models.order import Order, OrderItem, OrderStatus, PaymentProvider, UserLibrary, PromoCode
from app.models.timetable import Timetable, TimetableProgress
from app.models.tutor import TutorSubscription, TutorPlan, ChatSession, ChatMessage
from app.models.school import School, SchoolAdmin, SchoolOrder, SchoolLicense

__all__ = [
    # User
    "User",
    "UserRole",
    "OTPCode",
    "ParentChild",
    # Product
    "Subject",
    "Product",
    "Bundle",
    "bundle_products",
    # Order
    "Order",
    "OrderItem",
    "OrderStatus",
    "PaymentProvider",
    "UserLibrary",
    "PromoCode",
    # Timetable
    "Timetable",
    "TimetableProgress",
    # Tutor
    "TutorSubscription",
    "TutorPlan",
    "ChatSession",
    "ChatMessage",
    # School
    "School",
    "SchoolAdmin",
    "SchoolOrder",
    "SchoolLicense",
]
