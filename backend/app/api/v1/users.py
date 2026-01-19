from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User, UserRole

router = APIRouter()


class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    role: str
    grade: Optional[int]
    phone: Optional[str]
    province: Optional[str]
    avatar_url: Optional[str]
    email_verified: bool

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    grade: Optional[int] = None
    province: Optional[str] = None
    avatar_url: Optional[str] = None


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(user: User = Depends(get_current_user)):
    """Get current user's profile."""
    return UserResponse(
        id=str(user.id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role.value,
        grade=user.grade,
        phone=user.phone,
        province=user.province,
        avatar_url=user.avatar_url,
        email_verified=user.email_verified,
    )


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    data: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's profile."""
    # Update fields
    if data.first_name is not None:
        user.first_name = data.first_name
    if data.last_name is not None:
        user.last_name = data.last_name
    if data.phone is not None:
        user.phone = data.phone
    if data.province is not None:
        user.province = data.province
    if data.avatar_url is not None:
        user.avatar_url = data.avatar_url

    # Grade validation for students
    if data.grade is not None:
        if user.role == UserRole.STUDENT:
            if not (6 <= data.grade <= 12):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Grade must be between 6 and 12"
                )
            user.grade = data.grade

    await db.commit()
    await db.refresh(user)

    return UserResponse(
        id=str(user.id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role.value,
        grade=user.grade,
        phone=user.phone,
        province=user.province,
        avatar_url=user.avatar_url,
        email_verified=user.email_verified,
    )


@router.get("/me/stats")
async def get_user_stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's statistics."""
    from app.models import UserLibrary, Timetable, TimetableProgress

    # Count purchased products
    library_count = await db.execute(
        select(UserLibrary).where(UserLibrary.user_id == user.id)
    )
    purchased_count = len(library_count.scalars().all())

    # Count active timetables
    timetables = await db.execute(
        select(Timetable).where(
            Timetable.user_id == user.id,
            Timetable.is_active == True
        )
    )
    active_timetables = len(timetables.scalars().all())

    # Calculate overall progress
    # TODO: Implement proper progress calculation

    return {
        "purchased_guides": purchased_count,
        "active_timetables": active_timetables,
        "study_streak": 0,  # TODO: Implement streak tracking
        "total_study_hours": 0,  # TODO: Calculate from timetable progress
    }
