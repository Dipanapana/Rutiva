from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import (
    User, Product, UserLibrary, TutorSubscription, TutorPlan,
    ChatSession, ChatMessage
)
from app.services.ai_service import AIService

router = APIRouter()


class TutorPlanResponse(BaseModel):
    plan: str
    name: str
    questions_limit: Optional[int]
    price_zar: int
    description: str


class TutorUsageResponse(BaseModel):
    has_subscription: bool
    plan: Optional[str]
    questions_used: int
    questions_limit: Optional[int]
    questions_remaining: Optional[int]
    can_ask: bool
    subscription_ends_at: Optional[str]


class StartSessionRequest(BaseModel):
    product_id: Optional[str] = None
    subject: Optional[str] = None
    grade: Optional[int] = None
    topic: Optional[str] = None


class SessionResponse(BaseModel):
    id: str
    subject: Optional[str]
    grade: Optional[int]
    topic: Optional[str]
    question_count: int
    started_at: str
    last_message_at: Optional[str]


class SendMessageRequest(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: str


TUTOR_PLANS = [
    TutorPlanResponse(
        plan="starter",
        name="Starter",
        questions_limit=15,
        price_zar=4900,
        description="15 AI tutor questions per month",
    ),
    TutorPlanResponse(
        plan="standard",
        name="Standard",
        questions_limit=40,
        price_zar=8900,
        description="40 AI tutor questions per month",
    ),
    TutorPlanResponse(
        plan="unlimited",
        name="Unlimited",
        questions_limit=None,
        price_zar=14900,
        description="Unlimited AI tutor questions",
    ),
]


@router.get("/plans", response_model=List[TutorPlanResponse])
async def get_tutor_plans():
    """Get available AI tutor subscription plans."""
    return TUTOR_PLANS


@router.get("/usage", response_model=TutorUsageResponse)
async def get_tutor_usage(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's AI tutor usage."""
    result = await db.execute(
        select(TutorSubscription).where(TutorSubscription.user_id == user.id)
    )
    subscription = result.scalar_one_or_none()

    if not subscription or not subscription.is_active:
        return TutorUsageResponse(
            has_subscription=False,
            plan=None,
            questions_used=0,
            questions_limit=None,
            questions_remaining=None,
            can_ask=False,
            subscription_ends_at=None,
        )

    return TutorUsageResponse(
        has_subscription=True,
        plan=subscription.plan.value,
        questions_used=subscription.questions_used,
        questions_limit=subscription.questions_limit,
        questions_remaining=subscription.questions_remaining,
        can_ask=subscription.can_ask_question,
        subscription_ends_at=subscription.ends_at.isoformat(),
    )


@router.post("/sessions", response_model=SessionResponse)
async def start_chat_session(
    data: StartSessionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start a new chat session with the AI tutor."""
    # Check subscription
    result = await db.execute(
        select(TutorSubscription).where(TutorSubscription.user_id == user.id)
    )
    subscription = result.scalar_one_or_none()

    if not subscription or not subscription.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AI tutor subscription required"
        )

    # Get context from product if provided
    subject = data.subject
    grade = data.grade or user.grade
    topic = data.topic

    if data.product_id:
        # Verify user owns the product
        result = await db.execute(
            select(UserLibrary)
            .options(selectinload(UserLibrary.product).selectinload(Product.subject))
            .where(
                UserLibrary.user_id == user.id,
                UserLibrary.product_id == data.product_id,
            )
        )
        library_item = result.scalar_one_or_none()
        if library_item:
            subject = library_item.product.subject.name
            grade = library_item.product.grade
            # Topic could be set from context

    # Create session
    session = ChatSession(
        user_id=user.id,
        product_id=data.product_id,
        subject=subject,
        grade=grade,
        topic=topic,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    return SessionResponse(
        id=str(session.id),
        subject=session.subject,
        grade=session.grade,
        topic=session.topic,
        question_count=session.question_count,
        started_at=session.started_at.isoformat(),
        last_message_at=None,
    )


@router.get("/sessions", response_model=List[SessionResponse])
async def list_sessions(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List user's recent chat sessions."""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == user.id)
        .order_by(ChatSession.started_at.desc())
        .limit(20)
    )
    sessions = result.scalars().all()

    return [
        SessionResponse(
            id=str(s.id),
            subject=s.subject,
            grade=s.grade,
            topic=s.topic,
            question_count=s.question_count,
            started_at=s.started_at.isoformat(),
            last_message_at=s.last_message_at.isoformat() if s.last_message_at else None,
        )
        for s in sessions
    ]


@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
async def get_session_messages(
    session_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all messages in a chat session."""
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == user.id,
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )
    messages = result.scalars().all()

    return [
        MessageResponse(
            id=str(m.id),
            role=m.role,
            content=m.content,
            created_at=m.created_at.isoformat(),
        )
        for m in messages
    ]


@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: str,
    data: SendMessageRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a message and get AI response (streaming)."""
    # Verify session
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == user.id,
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Check subscription
    result = await db.execute(
        select(TutorSubscription).where(TutorSubscription.user_id == user.id)
    )
    subscription = result.scalar_one_or_none()

    if not subscription or not subscription.can_ask_question:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No questions remaining. Please upgrade your plan."
        )

    # Validate message length
    if len(data.content) > 2000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message too long (max 2000 characters)"
        )

    # Save user message
    user_message = ChatMessage(
        session_id=session.id,
        role="user",
        content=data.content,
    )
    db.add(user_message)

    # Get conversation history
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
        .limit(20)  # Limit context
    )
    history = result.scalars().all()

    # Update session
    session.question_count += 1
    session.last_message_at = datetime.utcnow()

    # Update subscription usage
    if subscription.questions_limit is not None:
        subscription.questions_used += 1

    await db.commit()

    # Generate AI response (streaming)
    ai_service = AIService()

    async def generate():
        full_response = ""
        async for chunk in ai_service.chat_completion(
            messages=[{"role": m.role, "content": m.content} for m in history] + [{"role": "user", "content": data.content}],
            grade=session.grade or user.grade or 10,
            subject=session.subject,
            topic=session.topic,
        ):
            full_response += chunk
            yield f"data: {chunk}\n\n"

        # Save assistant message
        async with db.begin():
            assistant_message = ChatMessage(
                session_id=session.id,
                role="assistant",
                content=full_response,
            )
            db.add(assistant_message)

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
