from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from pydantic import BaseModel
from app.core.database import get_db
from app.api.deps import get_current_user_optional
from app.models import Product, Subject, Bundle, User

router = APIRouter()


# Pydantic Schemas
class SubjectResponse(BaseModel):
    id: str
    name: str
    code: str
    description: Optional[str]
    icon_url: Optional[str]
    color: Optional[str]

    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    id: str
    sku: str
    title: str
    description: Optional[str]
    short_description: Optional[str]
    subject: SubjectResponse
    grade: int
    term: int
    year: int
    price_zar: int
    sale_price_zar: Optional[int]
    is_on_sale: bool
    current_price: int
    discount_percent: int
    thumbnail_url: Optional[str]
    preview_url: Optional[str]
    total_pages: Optional[int]
    total_hours: Optional[int]
    is_featured: bool

    class Config:
        from_attributes = True


class ProductDetailResponse(ProductResponse):
    content_json: dict  # Full course breakdown

    class Config:
        from_attributes = True


class BundleResponse(BaseModel):
    id: str
    sku: str
    title: str
    description: Optional[str]
    price_zar: int
    original_price_zar: Optional[int]
    savings: int
    discount_percent: int
    thumbnail_url: Optional[str]
    products: List[ProductResponse]

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total: int
    page: int
    page_size: int


@router.get("/subjects", response_model=List[SubjectResponse])
async def list_subjects(db: AsyncSession = Depends(get_db)):
    """List all subjects."""
    result = await db.execute(
        select(Subject).where(Subject.is_active == True).order_by(Subject.name)
    )
    subjects = result.scalars().all()
    return [
        SubjectResponse(
            id=str(s.id),
            name=s.name,
            code=s.code,
            description=s.description,
            icon_url=s.icon_url,
            color=s.color,
        )
        for s in subjects
    ]


@router.get("", response_model=ProductListResponse)
async def list_products(
    grade: Optional[int] = Query(None, ge=6, le=12),
    subject: Optional[str] = Query(None),
    term: Optional[int] = Query(None, ge=1, le=4),
    year: Optional[int] = Query(None),
    featured: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List published study guides with filters."""
    query = select(Product).options(selectinload(Product.subject)).where(
        Product.is_published == True
    )

    # Apply filters
    if grade:
        query = query.where(Product.grade == grade)
    if term:
        query = query.where(Product.term == term)
    if year:
        query = query.where(Product.year == year)
    if featured is not None:
        query = query.where(Product.is_featured == featured)
    if subject:
        query = query.join(Subject).where(
            or_(Subject.code == subject.upper(), Subject.name.ilike(f"%{subject}%"))
        )
    if search:
        query = query.where(
            or_(
                Product.title.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%"),
            )
        )

    # Count total
    count_query = select(Product).where(Product.is_published == True)
    # Apply same filters to count
    if grade:
        count_query = count_query.where(Product.grade == grade)
    if term:
        count_query = count_query.where(Product.term == term)

    total_result = await db.execute(count_query)
    total = len(total_result.scalars().all())

    # Pagination
    offset = (page - 1) * page_size
    query = query.order_by(Product.grade, Product.term).offset(offset).limit(page_size)

    result = await db.execute(query)
    products = result.scalars().all()

    return ProductListResponse(
        products=[
            ProductResponse(
                id=str(p.id),
                sku=p.sku,
                title=p.title,
                description=p.description,
                short_description=p.short_description,
                subject=SubjectResponse(
                    id=str(p.subject.id),
                    name=p.subject.name,
                    code=p.subject.code,
                    description=p.subject.description,
                    icon_url=p.subject.icon_url,
                    color=p.subject.color,
                ),
                grade=p.grade,
                term=p.term,
                year=p.year,
                price_zar=p.price_zar,
                sale_price_zar=p.sale_price_zar,
                is_on_sale=p.is_on_sale,
                current_price=p.current_price,
                discount_percent=p.discount_percent,
                thumbnail_url=p.thumbnail_url,
                preview_url=p.preview_url,
                total_pages=p.total_pages,
                total_hours=p.total_hours,
                is_featured=p.is_featured,
            )
            for p in products
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/grade/{grade}", response_model=List[ProductResponse])
async def list_products_by_grade(
    grade: int,
    db: AsyncSession = Depends(get_db),
):
    """List all products for a specific grade."""
    if not (6 <= grade <= 12):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Grade must be between 6 and 12"
        )

    result = await db.execute(
        select(Product)
        .options(selectinload(Product.subject))
        .where(
            Product.is_published == True,
            Product.grade == grade,
        )
        .order_by(Product.term)
    )
    products = result.scalars().all()

    return [
        ProductResponse(
            id=str(p.id),
            sku=p.sku,
            title=p.title,
            description=p.description,
            short_description=p.short_description,
            subject=SubjectResponse(
                id=str(p.subject.id),
                name=p.subject.name,
                code=p.subject.code,
                description=p.subject.description,
                icon_url=p.subject.icon_url,
                color=p.subject.color,
            ),
            grade=p.grade,
            term=p.term,
            year=p.year,
            price_zar=p.price_zar,
            sale_price_zar=p.sale_price_zar,
            is_on_sale=p.is_on_sale,
            current_price=p.current_price,
            discount_percent=p.discount_percent,
            thumbnail_url=p.thumbnail_url,
            preview_url=p.preview_url,
            total_pages=p.total_pages,
            total_hours=p.total_hours,
            is_featured=p.is_featured,
        )
        for p in products
    ]


@router.get("/{sku}", response_model=ProductDetailResponse)
async def get_product(
    sku: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a single product by SKU with full content breakdown."""
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.subject))
        .where(Product.sku == sku.upper())
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    if not product.is_published:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return ProductDetailResponse(
        id=str(product.id),
        sku=product.sku,
        title=product.title,
        description=product.description,
        short_description=product.short_description,
        subject=SubjectResponse(
            id=str(product.subject.id),
            name=product.subject.name,
            code=product.subject.code,
            description=product.subject.description,
            icon_url=product.subject.icon_url,
            color=product.subject.color,
        ),
        grade=product.grade,
        term=product.term,
        year=product.year,
        price_zar=product.price_zar,
        sale_price_zar=product.sale_price_zar,
        is_on_sale=product.is_on_sale,
        current_price=product.current_price,
        discount_percent=product.discount_percent,
        thumbnail_url=product.thumbnail_url,
        preview_url=product.preview_url,
        total_pages=product.total_pages,
        total_hours=product.total_hours,
        is_featured=product.is_featured,
        content_json=product.content_json,
    )


@router.get("/bundles", response_model=List[BundleResponse])
async def list_bundles(db: AsyncSession = Depends(get_db)):
    """List all available bundles."""
    result = await db.execute(
        select(Bundle)
        .options(selectinload(Bundle.products).selectinload(Product.subject))
        .where(Bundle.is_published == True)
        .order_by(Bundle.price_zar)
    )
    bundles = result.scalars().all()

    return [
        BundleResponse(
            id=str(b.id),
            sku=b.sku,
            title=b.title,
            description=b.description,
            price_zar=b.price_zar,
            original_price_zar=b.original_price_zar,
            savings=b.savings,
            discount_percent=b.discount_percent,
            thumbnail_url=b.thumbnail_url,
            products=[
                ProductResponse(
                    id=str(p.id),
                    sku=p.sku,
                    title=p.title,
                    description=p.description,
                    short_description=p.short_description,
                    subject=SubjectResponse(
                        id=str(p.subject.id),
                        name=p.subject.name,
                        code=p.subject.code,
                        description=p.subject.description,
                        icon_url=p.subject.icon_url,
                        color=p.subject.color,
                    ),
                    grade=p.grade,
                    term=p.term,
                    year=p.year,
                    price_zar=p.price_zar,
                    sale_price_zar=p.sale_price_zar,
                    is_on_sale=p.is_on_sale,
                    current_price=p.current_price,
                    discount_percent=p.discount_percent,
                    thumbnail_url=p.thumbnail_url,
                    preview_url=p.preview_url,
                    total_pages=p.total_pages,
                    total_hours=p.total_hours,
                    is_featured=p.is_featured,
                )
                for p in b.products
            ],
        )
        for b in bundles
    ]


@router.get("/bundles/{sku}", response_model=BundleResponse)
async def get_bundle(sku: str, db: AsyncSession = Depends(get_db)):
    """Get a bundle by SKU."""
    result = await db.execute(
        select(Bundle)
        .options(selectinload(Bundle.products).selectinload(Product.subject))
        .where(Bundle.sku == sku.upper())
    )
    bundle = result.scalar_one_or_none()

    if not bundle or not bundle.is_published:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bundle not found"
        )

    return BundleResponse(
        id=str(bundle.id),
        sku=bundle.sku,
        title=bundle.title,
        description=bundle.description,
        price_zar=bundle.price_zar,
        original_price_zar=bundle.original_price_zar,
        savings=bundle.savings,
        discount_percent=bundle.discount_percent,
        thumbnail_url=bundle.thumbnail_url,
        products=[
            ProductResponse(
                id=str(p.id),
                sku=p.sku,
                title=p.title,
                description=p.description,
                short_description=p.short_description,
                subject=SubjectResponse(
                    id=str(p.subject.id),
                    name=p.subject.name,
                    code=p.subject.code,
                    description=p.subject.description,
                    icon_url=p.subject.icon_url,
                    color=p.subject.color,
                ),
                grade=p.grade,
                term=p.term,
                year=p.year,
                price_zar=p.price_zar,
                sale_price_zar=p.sale_price_zar,
                is_on_sale=p.is_on_sale,
                current_price=p.current_price,
                discount_percent=p.discount_percent,
                thumbnail_url=p.thumbnail_url,
                preview_url=p.preview_url,
                total_pages=p.total_pages,
                total_hours=p.total_hours,
                is_featured=p.is_featured,
            )
            for p in bundle.products
        ],
    )
