from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_otp,
)
from app.core.config import settings
from app.models import User, UserRole, OTPCode

router = APIRouter()


# Pydantic Schemas
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: UserRole = UserRole.STUDENT
    grade: Optional[int] = None
    phone: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class OTPRequest(BaseModel):
    email: EmailStr
    purpose: str = "email_verify"  # email_verify, password_reset, login


class OTPVerify(BaseModel):
    email: EmailStr
    code: str
    purpose: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    email: EmailStr
    code: str
    new_password: str


@router.post("/register", response_model=TokenResponse)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    # Check if email exists
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Validate grade for students
    if data.role == UserRole.STUDENT and data.grade:
        if not (6 <= data.grade <= 12):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Grade must be between 6 and 12"
            )

    # Create user
    user = User(
        email=data.email,
        password_hash=get_password_hash(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        role=data.role,
        grade=data.grade,
        phone=data.phone,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Generate tokens
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role.value,
            "grade": user.grade,
        }
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login with email and password."""
    # Find user
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )

    # Update last login
    user.last_login_at = datetime.utcnow()
    await db.commit()

    # Generate tokens
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role.value,
            "grade": user.grade,
        }
    )


@router.post("/otp/request")
async def request_otp(data: OTPRequest, db: AsyncSession = Depends(get_db)):
    """Request an OTP code."""
    # Find user
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user:
        # Don't reveal if email exists
        return {"message": "If the email exists, an OTP has been sent"}

    # Generate OTP
    code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    # Save OTP
    otp = OTPCode(
        user_id=user.id,
        code=code,
        purpose=data.purpose,
        expires_at=expires_at,
    )
    db.add(otp)
    await db.commit()

    # TODO: Send OTP via email/SMS
    # For development, return the code
    if settings.DEBUG:
        return {"message": "OTP sent", "debug_code": code}

    return {"message": "If the email exists, an OTP has been sent"}


@router.post("/otp/verify")
async def verify_otp(data: OTPVerify, db: AsyncSession = Depends(get_db)):
    """Verify an OTP code."""
    # Find user
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )

    # Find valid OTP
    result = await db.execute(
        select(OTPCode).where(
            OTPCode.user_id == user.id,
            OTPCode.code == data.code,
            OTPCode.purpose == data.purpose,
            OTPCode.used == False,
            OTPCode.expires_at > datetime.utcnow(),
        )
    )
    otp = result.scalar_one_or_none()

    if not otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )

    # Mark OTP as used
    otp.used = True

    # Handle different purposes
    if data.purpose == "email_verify":
        user.email_verified = True

    await db.commit()

    # For login OTP, return tokens
    if data.purpose == "login":
        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user={
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role.value,
                "grade": user.grade,
            }
        )

    return {"message": "OTP verified successfully"}


@router.post("/refresh")
async def refresh_token(request: Request, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token."""
    # Get refresh token from header or body
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required"
        )

    # Decode and validate
    payload = decode_token(token)
    if not payload or payload.type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Find user
    result = await db.execute(select(User).where(User.id == payload.sub))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Generate new tokens
    access_token = create_access_token(str(user.id))
    new_refresh_token = create_refresh_token(str(user.id))

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.post("/password/reset")
async def password_reset(data: PasswordResetConfirm, db: AsyncSession = Depends(get_db)):
    """Reset password using OTP."""
    # Find user
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request"
        )

    # Find valid OTP
    result = await db.execute(
        select(OTPCode).where(
            OTPCode.user_id == user.id,
            OTPCode.code == data.code,
            OTPCode.purpose == "password_reset",
            OTPCode.used == False,
            OTPCode.expires_at > datetime.utcnow(),
        )
    )
    otp = result.scalar_one_or_none()

    if not otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired code"
        )

    # Update password
    user.password_hash = get_password_hash(data.new_password)
    otp.used = True
    await db.commit()

    return {"message": "Password reset successfully"}


@router.post("/logout")
async def logout(response: Response):
    """Logout user (client should discard tokens)."""
    # For JWT, logout is handled client-side by discarding tokens
    # If using httpOnly cookies, clear them here
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}
