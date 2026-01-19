from fastapi import APIRouter
from app.api.v1 import auth, users, products, cart, library, timetable, chat

router = APIRouter()

# Include all route modules
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(products.router, prefix="/products", tags=["Products"])
router.include_router(cart.router, prefix="/cart", tags=["Cart & Checkout"])
router.include_router(library.router, prefix="/library", tags=["Library"])
router.include_router(timetable.router, prefix="/timetables", tags=["Timetables"])
router.include_router(chat.router, prefix="/chat", tags=["AI Tutor"])
