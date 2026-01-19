from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional, List
from pydantic import BaseModel
from datetime import date, datetime
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User, Product, UserLibrary, Timetable, TimetableProgress
from app.services.timetable_generator import TimetableGenerator

router = APIRouter()


class TimetableCreateRequest(BaseModel):
    product_id: str
    exam_date: date
    study_days: List[str]  # ["Monday", "Wednesday", "Friday"]
    hours_per_session: float = 1.5
    preferred_time: str = "afternoon"  # morning, afternoon, evening
    pace: str = "normal"  # relaxed, normal, intensive
    start_date: Optional[date] = None
    title: Optional[str] = None


class TimetableResponse(BaseModel):
    id: str
    product_id: str
    product_title: str
    title: Optional[str]
    exam_date: str
    settings: dict
    total_sessions: int
    completed_sessions: int
    completion_percent: int
    is_active: bool
    created_at: str


class TimetableDetailResponse(TimetableResponse):
    schedule: dict


class SessionCompleteRequest(BaseModel):
    time_spent_minutes: Optional[int] = None
    notes: Optional[str] = None
    difficulty_rating: Optional[int] = None
    understanding_rating: Optional[int] = None


@router.post("", response_model=TimetableDetailResponse)
async def create_timetable(
    data: TimetableCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a new study timetable for a purchased guide."""
    # Verify user owns the product
    result = await db.execute(
        select(UserLibrary)
        .options(selectinload(UserLibrary.product))
        .where(
            UserLibrary.user_id == user.id,
            UserLibrary.product_id == data.product_id,
        )
    )
    library_item = result.scalar_one_or_none()

    if not library_item:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must purchase this guide before creating a timetable"
        )

    product = library_item.product

    # Validate inputs
    valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for day in data.study_days:
        if day not in valid_days:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid day: {day}"
            )

    if data.exam_date <= date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exam date must be in the future"
        )

    if data.hours_per_session < 0.5 or data.hours_per_session > 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hours per session must be between 0.5 and 4"
        )

    # Generate timetable
    generator = TimetableGenerator()
    schedule_data = await generator.generate(
        product={"content_json": product.content_json},
        exam_date=data.exam_date,
        study_days=data.study_days,
        hours_per_session=data.hours_per_session,
        preferred_time=data.preferred_time,
        pace=data.pace,
        start_date=data.start_date,
    )

    # Create timetable record
    timetable = Timetable(
        user_id=user.id,
        product_id=product.id,
        title=data.title or f"{product.title} Study Plan",
        exam_date=data.exam_date,
        settings={
            "study_days": data.study_days,
            "hours_per_session": data.hours_per_session,
            "preferred_time": data.preferred_time,
            "pace": data.pace,
            "start_date": (data.start_date or date.today()).isoformat(),
        },
        schedule=schedule_data["schedule"],
        total_sessions=schedule_data["total_sessions"],
        total_hours=int(schedule_data["total_hours"] * 60),  # Store in minutes
    )
    db.add(timetable)
    await db.commit()
    await db.refresh(timetable)

    return TimetableDetailResponse(
        id=str(timetable.id),
        product_id=str(timetable.product_id),
        product_title=product.title,
        title=timetable.title,
        exam_date=timetable.exam_date.isoformat(),
        settings=timetable.settings,
        total_sessions=timetable.total_sessions,
        completed_sessions=timetable.completed_sessions,
        completion_percent=timetable.completion_percent,
        is_active=timetable.is_active,
        created_at=timetable.created_at.isoformat(),
        schedule=timetable.schedule,
    )


@router.get("", response_model=List[TimetableResponse])
async def list_timetables(
    active_only: bool = True,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List user's timetables."""
    query = select(Timetable).options(
        selectinload(Timetable.product)
    ).where(Timetable.user_id == user.id)

    if active_only:
        query = query.where(Timetable.is_active == True)

    query = query.order_by(Timetable.exam_date)

    result = await db.execute(query)
    timetables = result.scalars().all()

    return [
        TimetableResponse(
            id=str(t.id),
            product_id=str(t.product_id),
            product_title=t.product.title,
            title=t.title,
            exam_date=t.exam_date.isoformat(),
            settings=t.settings,
            total_sessions=t.total_sessions,
            completed_sessions=t.completed_sessions,
            completion_percent=t.completion_percent,
            is_active=t.is_active,
            created_at=t.created_at.isoformat(),
        )
        for t in timetables
    ]


@router.get("/{timetable_id}", response_model=TimetableDetailResponse)
async def get_timetable(
    timetable_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific timetable with full schedule."""
    result = await db.execute(
        select(Timetable)
        .options(selectinload(Timetable.product))
        .where(
            Timetable.id == timetable_id,
            Timetable.user_id == user.id,
        )
    )
    timetable = result.scalar_one_or_none()

    if not timetable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timetable not found"
        )

    # Get progress for all sessions
    progress_result = await db.execute(
        select(TimetableProgress).where(TimetableProgress.timetable_id == timetable.id)
    )
    progress_records = {
        (p.session_date.isoformat(), p.session_index): p
        for p in progress_result.scalars().all()
    }

    # Merge progress into schedule
    schedule = timetable.schedule.copy()
    if "sessions" in schedule:
        for i, session in enumerate(schedule["sessions"]):
            key = (session["date"], i)
            if key in progress_records:
                progress = progress_records[key]
                session["completed"] = progress.completed
                session["completed_at"] = progress.completed_at.isoformat() if progress.completed_at else None
                session["time_spent_minutes"] = progress.time_spent_minutes
                session["notes"] = progress.notes

    return TimetableDetailResponse(
        id=str(timetable.id),
        product_id=str(timetable.product_id),
        product_title=timetable.product.title,
        title=timetable.title,
        exam_date=timetable.exam_date.isoformat(),
        settings=timetable.settings,
        total_sessions=timetable.total_sessions,
        completed_sessions=timetable.completed_sessions,
        completion_percent=timetable.completion_percent,
        is_active=timetable.is_active,
        created_at=timetable.created_at.isoformat(),
        schedule=schedule,
    )


@router.post("/{timetable_id}/sessions/{session_index}/complete")
async def complete_session(
    timetable_id: str,
    session_index: int,
    data: SessionCompleteRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a study session as complete."""
    result = await db.execute(
        select(Timetable).where(
            Timetable.id == timetable_id,
            Timetable.user_id == user.id,
        )
    )
    timetable = result.scalar_one_or_none()

    if not timetable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timetable not found"
        )

    # Validate session index
    sessions = timetable.schedule.get("sessions", [])
    if session_index < 0 or session_index >= len(sessions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session index"
        )

    session = sessions[session_index]
    session_date = date.fromisoformat(session["date"])

    # Find or create progress record
    result = await db.execute(
        select(TimetableProgress).where(
            TimetableProgress.timetable_id == timetable.id,
            TimetableProgress.session_date == session_date,
            TimetableProgress.session_index == session_index,
        )
    )
    progress = result.scalar_one_or_none()

    if not progress:
        progress = TimetableProgress(
            timetable_id=timetable.id,
            session_date=session_date,
            session_index=session_index,
        )
        db.add(progress)

    # Update progress
    progress.completed = True
    progress.completed_at = datetime.utcnow()
    if data.time_spent_minutes is not None:
        progress.time_spent_minutes = data.time_spent_minutes
    if data.notes is not None:
        progress.notes = data.notes
    if data.difficulty_rating is not None:
        progress.difficulty_rating = data.difficulty_rating
    if data.understanding_rating is not None:
        progress.understanding_rating = data.understanding_rating

    # Update timetable completed count
    timetable.completed_sessions += 1

    await db.commit()

    return {
        "message": "Session completed",
        "completed_sessions": timetable.completed_sessions,
        "total_sessions": timetable.total_sessions,
        "completion_percent": timetable.completion_percent,
    }


@router.delete("/{timetable_id}")
async def delete_timetable(
    timetable_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete (deactivate) a timetable."""
    result = await db.execute(
        select(Timetable).where(
            Timetable.id == timetable_id,
            Timetable.user_id == user.id,
        )
    )
    timetable = result.scalar_one_or_none()

    if not timetable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timetable not found"
        )

    timetable.is_active = False
    await db.commit()

    return {"message": "Timetable deleted"}


@router.get("/{timetable_id}/ical")
async def export_ical(
    timetable_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export timetable as iCal format."""
    result = await db.execute(
        select(Timetable)
        .options(selectinload(Timetable.product))
        .where(
            Timetable.id == timetable_id,
            Timetable.user_id == user.id,
        )
    )
    timetable = result.scalar_one_or_none()

    if not timetable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timetable not found"
        )

    # Generate iCal
    ical_content = generate_ical(timetable)

    return Response(
        content=ical_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f"attachment; filename=rutiva-{timetable.product.sku}.ics"
        }
    )


def generate_ical(timetable: Timetable) -> str:
    """Generate iCal content for a timetable."""
    from datetime import timedelta
    import uuid

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Rutiva//Study Timetable//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{timetable.title or 'Rutiva Study Plan'}",
    ]

    time_mapping = {
        "morning": "08:00",
        "afternoon": "15:00",
        "evening": "19:00",
    }
    preferred_time = timetable.settings.get("preferred_time", "afternoon")
    base_time = time_mapping.get(preferred_time, "15:00")

    for session in timetable.schedule.get("sessions", []):
        session_date = session["date"]
        duration_minutes = session.get("duration_minutes", 90)

        # Parse date and time
        dt_start = datetime.fromisoformat(f"{session_date}T{base_time}:00")
        dt_end = dt_start + timedelta(minutes=duration_minutes)

        # Get topics for description
        topics = session.get("topics", [])
        topic_names = [t.get("topic", "") for t in topics]
        description = f"Topics: {', '.join(topic_names)}"

        # Tasks
        tasks = session.get("tasks", [])
        if tasks:
            description += f"\\n\\nTasks:\\n" + "\\n".join(f"- {t}" for t in tasks)

        event_uid = str(uuid.uuid4())

        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{event_uid}",
            f"DTSTART:{dt_start.strftime('%Y%m%dT%H%M%S')}",
            f"DTEND:{dt_end.strftime('%Y%m%dT%H%M%S')}",
            f"SUMMARY:Rutiva: {session.get('topic', 'Study Session')}",
            f"DESCRIPTION:{description}",
            "END:VEVENT",
        ])

    lines.append("END:VCALENDAR")

    return "\r\n".join(lines)
