from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from app.core.database import get_db
from app.core.config import settings
from app.api.deps import get_current_user
from app.models import (
    User, Product, Bundle, Order, OrderItem, OrderStatus,
    PaymentProvider, UserLibrary, PromoCode
)

router = APIRouter()


# In-memory cart (in production, use Redis or database)
# For simplicity, we'll use session-based cart stored in DB
class CartItem(BaseModel):
    product_id: Optional[str] = None
    bundle_id: Optional[str] = None
    quantity: int = 1


class CartResponse(BaseModel):
    items: List[dict]
    subtotal_zar: int
    discount_zar: int
    total_zar: int
    promo_code: Optional[str] = None


class AddToCartRequest(BaseModel):
    product_id: Optional[str] = None
    bundle_id: Optional[str] = None


class ApplyPromoRequest(BaseModel):
    code: str


class CheckoutRequest(BaseModel):
    payment_provider: str  # payfast, yoco


class CheckoutResponse(BaseModel):
    order_id: str
    order_number: str
    payment_url: str
    total_zar: int


# Simple in-memory cart storage (replace with Redis in production)
_carts: dict = {}


def get_user_cart(user_id: str) -> dict:
    """Get or create cart for user."""
    if user_id not in _carts:
        _carts[user_id] = {"items": [], "promo_code": None}
    return _carts[user_id]


@router.get("", response_model=CartResponse)
async def get_cart(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's cart."""
    cart = get_user_cart(str(user.id))
    items = []
    subtotal = 0

    for item in cart["items"]:
        if item.get("product_id"):
            result = await db.execute(
                select(Product).options(selectinload(Product.subject))
                .where(Product.id == item["product_id"])
            )
            product = result.scalar_one_or_none()
            if product:
                price = product.current_price
                subtotal += price
                items.append({
                    "type": "product",
                    "id": str(product.id),
                    "sku": product.sku,
                    "title": product.title,
                    "grade": product.grade,
                    "term": product.term,
                    "subject": product.subject.name,
                    "price_zar": price,
                    "thumbnail_url": product.thumbnail_url,
                })
        elif item.get("bundle_id"):
            result = await db.execute(
                select(Bundle).where(Bundle.id == item["bundle_id"])
            )
            bundle = result.scalar_one_or_none()
            if bundle:
                subtotal += bundle.price_zar
                items.append({
                    "type": "bundle",
                    "id": str(bundle.id),
                    "sku": bundle.sku,
                    "title": bundle.title,
                    "price_zar": bundle.price_zar,
                    "thumbnail_url": bundle.thumbnail_url,
                })

    # Calculate discount
    discount = 0
    if cart.get("promo_code"):
        result = await db.execute(
            select(PromoCode).where(PromoCode.code == cart["promo_code"])
        )
        promo = result.scalar_one_or_none()
        if promo and promo.is_valid:
            discount = promo.calculate_discount(subtotal)

    return CartResponse(
        items=items,
        subtotal_zar=subtotal,
        discount_zar=discount,
        total_zar=max(0, subtotal - discount),
        promo_code=cart.get("promo_code"),
    )


@router.post("/items")
async def add_to_cart(
    data: AddToCartRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add item to cart."""
    cart = get_user_cart(str(user.id))

    # Validate product/bundle exists
    if data.product_id:
        result = await db.execute(
            select(Product).where(Product.id == data.product_id, Product.is_published == True)
        )
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Check if already purchased
        library_check = await db.execute(
            select(UserLibrary).where(
                UserLibrary.user_id == user.id,
                UserLibrary.product_id == data.product_id,
            )
        )
        if library_check.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="You already own this product")

        # Check if already in cart
        for item in cart["items"]:
            if item.get("product_id") == data.product_id:
                raise HTTPException(status_code=400, detail="Product already in cart")

        cart["items"].append({"product_id": data.product_id})

    elif data.bundle_id:
        result = await db.execute(
            select(Bundle).where(Bundle.id == data.bundle_id, Bundle.is_published == True)
        )
        bundle = result.scalar_one_or_none()
        if not bundle:
            raise HTTPException(status_code=404, detail="Bundle not found")

        # Check if already in cart
        for item in cart["items"]:
            if item.get("bundle_id") == data.bundle_id:
                raise HTTPException(status_code=400, detail="Bundle already in cart")

        cart["items"].append({"bundle_id": data.bundle_id})
    else:
        raise HTTPException(status_code=400, detail="Product or bundle ID required")

    return {"message": "Item added to cart", "cart_count": len(cart["items"])}


@router.delete("/items/{item_id}")
async def remove_from_cart(
    item_id: str,
    user: User = Depends(get_current_user),
):
    """Remove item from cart."""
    cart = get_user_cart(str(user.id))

    original_count = len(cart["items"])
    cart["items"] = [
        item for item in cart["items"]
        if item.get("product_id") != item_id and item.get("bundle_id") != item_id
    ]

    if len(cart["items"]) == original_count:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    return {"message": "Item removed", "cart_count": len(cart["items"])}


@router.post("/promo")
async def apply_promo_code(
    data: ApplyPromoRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Apply a promo code to cart."""
    result = await db.execute(
        select(PromoCode).where(PromoCode.code == data.code.upper())
    )
    promo = result.scalar_one_or_none()

    if not promo or not promo.is_valid:
        raise HTTPException(status_code=400, detail="Invalid or expired promo code")

    cart = get_user_cart(str(user.id))
    cart["promo_code"] = promo.code

    return {"message": "Promo code applied", "code": promo.code}


@router.delete("/promo")
async def remove_promo_code(user: User = Depends(get_current_user)):
    """Remove promo code from cart."""
    cart = get_user_cart(str(user.id))
    cart["promo_code"] = None
    return {"message": "Promo code removed"}


@router.post("/checkout", response_model=CheckoutResponse)
async def checkout(
    data: CheckoutRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create order and get payment URL."""
    cart = get_user_cart(str(user.id))

    if not cart["items"]:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Calculate totals
    subtotal = 0
    order_items = []

    for item in cart["items"]:
        if item.get("product_id"):
            result = await db.execute(
                select(Product).where(Product.id == item["product_id"])
            )
            product = result.scalar_one_or_none()
            if product:
                price = product.current_price
                subtotal += price
                order_items.append({
                    "product_id": product.id,
                    "price_zar": price,
                })
        elif item.get("bundle_id"):
            result = await db.execute(
                select(Bundle).options(selectinload(Bundle.products))
                .where(Bundle.id == item["bundle_id"])
            )
            bundle = result.scalar_one_or_none()
            if bundle:
                subtotal += bundle.price_zar
                order_items.append({
                    "bundle_id": bundle.id,
                    "price_zar": bundle.price_zar,
                    "products": [p.id for p in bundle.products],
                })

    # Apply promo discount
    discount = 0
    promo_code_id = None
    if cart.get("promo_code"):
        result = await db.execute(
            select(PromoCode).where(PromoCode.code == cart["promo_code"])
        )
        promo = result.scalar_one_or_none()
        if promo and promo.is_valid:
            discount = promo.calculate_discount(subtotal)
            promo_code_id = promo.id

    total = max(0, subtotal - discount)

    # Create order
    order = Order(
        user_id=user.id,
        subtotal_zar=subtotal,
        discount_zar=discount,
        total_zar=total,
        promo_code_id=promo_code_id,
        payment_provider=PaymentProvider(data.payment_provider),
    )
    db.add(order)
    await db.flush()  # Get order ID

    # Create order items
    for item in order_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.get("product_id"),
            bundle_id=item.get("bundle_id"),
            price_zar=item["price_zar"],
        )
        db.add(order_item)

    await db.commit()
    await db.refresh(order)

    # Generate payment URL
    if data.payment_provider == "payfast":
        payment_url = generate_payfast_url(order, user)
    elif data.payment_provider == "yoco":
        payment_url = f"{settings.FRONTEND_URL}/checkout/yoco?order={order.order_number}"
    else:
        raise HTTPException(status_code=400, detail="Invalid payment provider")

    # Clear cart
    _carts[str(user.id)] = {"items": [], "promo_code": None}

    return CheckoutResponse(
        order_id=str(order.id),
        order_number=order.order_number,
        payment_url=payment_url,
        total_zar=total,
    )


def generate_payfast_url(order: Order, user: User) -> str:
    """Generate PayFast payment URL."""
    import hashlib
    from urllib.parse import urlencode

    # PayFast parameters
    data = {
        "merchant_id": settings.PAYFAST_MERCHANT_ID or "10000100",
        "merchant_key": settings.PAYFAST_MERCHANT_KEY or "46f0cd694581a",
        "return_url": f"{settings.FRONTEND_URL}/checkout/success?order={order.order_number}",
        "cancel_url": f"{settings.FRONTEND_URL}/checkout/cancel?order={order.order_number}",
        "notify_url": f"{settings.API_URL}/api/v1/cart/webhook/payfast",
        "name_first": user.first_name,
        "name_last": user.last_name,
        "email_address": user.email,
        "m_payment_id": order.order_number,
        "amount": f"{order.total_zar / 100:.2f}",
        "item_name": f"RUTA Study Guide Order {order.order_number}",
    }

    # Generate signature
    if settings.PAYFAST_PASSPHRASE:
        signature_string = urlencode(data) + f"&passphrase={settings.PAYFAST_PASSPHRASE}"
    else:
        signature_string = urlencode(data)
    data["signature"] = hashlib.md5(signature_string.encode()).hexdigest()

    # Use sandbox or live URL
    base_url = "https://sandbox.payfast.co.za/eng/process" if settings.PAYFAST_SANDBOX else "https://www.payfast.co.za/eng/process"

    return f"{base_url}?{urlencode(data)}"


@router.post("/webhook/payfast")
async def payfast_webhook(
    request_data: dict,
    db: AsyncSession = Depends(get_db),
):
    """Handle PayFast payment notification."""
    # Verify signature (implement proper verification in production)
    payment_id = request_data.get("m_payment_id")
    payment_status = request_data.get("payment_status")

    if not payment_id:
        raise HTTPException(status_code=400, detail="Invalid webhook data")

    # Find order
    result = await db.execute(
        select(Order).where(Order.order_number == payment_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if payment_status == "COMPLETE":
        order.status = OrderStatus.PAID
        order.paid_at = datetime.utcnow()
        order.payment_reference = request_data.get("pf_payment_id")

        # Add products to user's library
        await fulfill_order(order, db)

    elif payment_status == "CANCELLED":
        order.status = OrderStatus.CANCELLED

    await db.commit()

    return {"status": "ok"}


async def fulfill_order(order: Order, db: AsyncSession):
    """Add purchased products to user's library."""
    # Get order items
    result = await db.execute(
        select(OrderItem).options(
            selectinload(OrderItem.bundle).selectinload(Bundle.products)
        ).where(OrderItem.order_id == order.id)
    )
    items = result.scalars().all()

    products_to_add = []

    for item in items:
        if item.product_id:
            products_to_add.append(item.product_id)
        elif item.bundle_id and item.bundle:
            for product in item.bundle.products:
                products_to_add.append(product.id)

    # Add to library (avoid duplicates)
    for product_id in set(products_to_add):
        existing = await db.execute(
            select(UserLibrary).where(
                UserLibrary.user_id == order.user_id,
                UserLibrary.product_id == product_id,
            )
        )
        if not existing.scalar_one_or_none():
            library_entry = UserLibrary(
                user_id=order.user_id,
                product_id=product_id,
                order_id=order.id,
            )
            db.add(library_entry)

    # Update promo code usage
    if order.promo_code_id:
        result = await db.execute(
            select(PromoCode).where(PromoCode.id == order.promo_code_id)
        )
        promo = result.scalar_one_or_none()
        if promo:
            promo.current_uses += 1

    await db.commit()
