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
from app.models import User, Product, UserLibrary
from app.services.delivery_service import DeliveryService

router = APIRouter()


class LibraryItemResponse(BaseModel):
    id: str
    product_id: str
    sku: str
    title: str
    subject: str
    grade: int
    term: int
    thumbnail_url: Optional[str]
    download_count: int
    progress_percent: int
    purchased_at: str
    last_accessed_at: Optional[str]


class LibraryDetailResponse(LibraryItemResponse):
    content_json: dict
    pdf_available: bool


class DownloadResponse(BaseModel):
    url: str
    expires_at: str
    filename: str


@router.get("", response_model=List[LibraryItemResponse])
async def get_library(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's purchased study guides."""
    result = await db.execute(
        select(UserLibrary)
        .options(selectinload(UserLibrary.product).selectinload(Product.subject))
        .where(UserLibrary.user_id == user.id)
        .order_by(UserLibrary.purchased_at.desc())
    )
    library_items = result.scalars().all()

    return [
        LibraryItemResponse(
            id=str(item.id),
            product_id=str(item.product_id),
            sku=item.product.sku,
            title=item.product.title,
            subject=item.product.subject.name,
            grade=item.product.grade,
            term=item.product.term,
            thumbnail_url=item.product.thumbnail_url,
            download_count=item.download_count,
            progress_percent=item.progress_percent,
            purchased_at=item.purchased_at.isoformat(),
            last_accessed_at=item.last_accessed_at.isoformat() if item.last_accessed_at else None,
        )
        for item in library_items
    ]


@router.get("/{product_id}", response_model=LibraryDetailResponse)
async def get_library_item(
    product_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific purchased study guide with content."""
    result = await db.execute(
        select(UserLibrary)
        .options(selectinload(UserLibrary.product).selectinload(Product.subject))
        .where(
            UserLibrary.user_id == user.id,
            UserLibrary.product_id == product_id,
        )
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found in your library"
        )

    # Update last accessed
    item.last_accessed_at = datetime.utcnow()
    await db.commit()

    return LibraryDetailResponse(
        id=str(item.id),
        product_id=str(item.product_id),
        sku=item.product.sku,
        title=item.product.title,
        subject=item.product.subject.name,
        grade=item.product.grade,
        term=item.product.term,
        thumbnail_url=item.product.thumbnail_url,
        download_count=item.download_count,
        progress_percent=item.progress_percent,
        purchased_at=item.purchased_at.isoformat(),
        last_accessed_at=item.last_accessed_at.isoformat() if item.last_accessed_at else None,
        content_json=item.product.content_json,
        pdf_available=bool(item.product.pdf_url),
    )


@router.get("/{product_id}/pdf", response_model=DownloadResponse)
async def get_pdf_download(
    product_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a signed URL to download the PDF."""
    result = await db.execute(
        select(UserLibrary)
        .options(selectinload(UserLibrary.product))
        .where(
            UserLibrary.user_id == user.id,
            UserLibrary.product_id == product_id,
        )
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found in your library"
        )

    if not item.product.pdf_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not available for this product"
        )

    # Generate signed URL
    delivery = DeliveryService()
    download_info = delivery.generate_download_url(
        user_id=str(user.id),
        product_id=str(product_id),
        file_key=item.product.pdf_url,
    )

    # Update download count
    item.download_count += 1
    item.last_accessed_at = datetime.utcnow()
    await db.commit()

    return DownloadResponse(
        url=download_info["url"],
        expires_at=download_info["expires_at"],
        filename=f"{item.product.sku}.pdf",
    )


@router.post("/{product_id}/progress")
async def update_progress(
    product_id: str,
    progress: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update reading progress for a study guide."""
    if not (0 <= progress <= 100):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Progress must be between 0 and 100"
        )

    result = await db.execute(
        select(UserLibrary).where(
            UserLibrary.user_id == user.id,
            UserLibrary.product_id == product_id,
        )
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found in your library"
        )

    item.progress_percent = progress
    item.last_accessed_at = datetime.utcnow()
    await db.commit()

    return {"message": "Progress updated", "progress_percent": progress}


@router.get("/{product_id}/answers", response_model=DownloadResponse)
async def get_answers_download(
    product_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a signed URL to download the answer key."""
    result = await db.execute(
        select(UserLibrary)
        .options(selectinload(UserLibrary.product))
        .where(
            UserLibrary.user_id == user.id,
            UserLibrary.product_id == product_id,
        )
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found in your library"
        )

    if not item.product.answer_key_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Answer key not available for this product"
        )

    # Generate signed URL
    delivery = DeliveryService()
    download_info = delivery.generate_download_url(
        user_id=str(user.id),
        product_id=str(product_id),
        file_key=item.product.answer_key_url,
    )

    return DownloadResponse(
        url=download_info["url"],
        expires_at=download_info["expires_at"],
        filename=f"{item.product.sku}-answers.pdf",
    )
