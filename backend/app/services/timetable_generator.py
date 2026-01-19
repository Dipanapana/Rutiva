from datetime import date, timedelta
from typing import Optional, List, AsyncGenerator
import json


class TimetableGenerator:
    """
    Generates personalized study timetables based on:
    - Study guide content structure
    - User's exam date
    - Available study time
    - Learning pace preference
    """

    async def generate(
        self,
        product: dict,
        exam_date: date,
        study_days: List[str],
        hours_per_session: float = 1.5,
        preferred_time: str = "afternoon",
        pace: str = "normal",
        start_date: Optional[date] = None
    ) -> dict:
        """Generate a complete study timetable."""

        start = start_date or date.today()
        content = product.get("content_json", {})

        # Calculate available time
        days_until_exam = (exam_date - start).days
        weeks_available = max(1, days_until_exam // 7)
        sessions_per_week = len(study_days)
        total_sessions = weeks_available * sessions_per_week

        # Get content units and topics
        units = content.get("units", [])
        all_topics = []

        for unit in units:
            for topic in unit.get("topics", []):
                all_topics.append({
                    "unit": unit.get("title", ""),
                    "topic": topic.get("title", ""),
                    "hours": topic.get("hours", 2),
                    "sections": topic.get("content_sections", []),
                    "difficulty": topic.get("difficulty", "core"),
                    "key_formulas": topic.get("key_formulas", []),
                    "exam_tips": topic.get("exam_tips", []),
                })

        # If no topics found, create default sessions
        if not all_topics:
            all_topics = [
                {"unit": "Study", "topic": f"Session {i+1}", "hours": hours_per_session, "sections": [], "difficulty": "core"}
                for i in range(total_sessions)
            ]

        # Distribute topics across sessions
        schedule = self._distribute_topics(
            topics=all_topics,
            total_sessions=total_sessions,
            hours_per_session=hours_per_session,
            pace=pace
        )

        # Map to calendar
        calendar = self._map_to_calendar(
            schedule=schedule,
            start_date=start,
            study_days=study_days,
            preferred_time=preferred_time,
            exam_date=exam_date
        )

        # Add milestones (practice tests, revision)
        calendar = self._add_milestones(
            calendar=calendar,
            weeks_available=weeks_available,
            units=units
        )

        return {
            "total_weeks": weeks_available,
            "total_sessions": len(calendar.get("sessions", [])),
            "total_hours": sum(s.get("duration_minutes", 0) for s in calendar.get("sessions", [])) / 60,
            "schedule": calendar
        }

    def _distribute_topics(
        self,
        topics: List[dict],
        total_sessions: int,
        hours_per_session: float,
        pace: str
    ) -> List[dict]:
        """Distribute topics across available sessions."""
        pace_multipliers = {
            "relaxed": 0.7,
            "normal": 0.85,
            "intensive": 1.0
        }

        multiplier = pace_multipliers.get(pace, 0.85)
        effective_hours = hours_per_session * multiplier

        sessions = []
        current_session = {"topics": [], "hours": 0}

        for topic in topics:
            topic_hours = topic.get("hours", 2)

            # Split large topics across sessions
            while topic_hours > 0:
                space_left = effective_hours - current_session["hours"]

                if space_left >= topic_hours:
                    current_session["topics"].append({
                        **topic,
                        "allocated_hours": topic_hours
                    })
                    current_session["hours"] += topic_hours
                    topic_hours = 0
                else:
                    if space_left > 0:
                        current_session["topics"].append({
                            **topic,
                            "allocated_hours": space_left,
                            "partial": True
                        })
                        current_session["hours"] += space_left
                        topic_hours -= space_left

                # Start new session if full
                if current_session["hours"] >= effective_hours * 0.9:
                    sessions.append(current_session)
                    current_session = {"topics": [], "hours": 0}

        # Add remaining session
        if current_session["topics"]:
            sessions.append(current_session)

        return sessions

    def _map_to_calendar(
        self,
        schedule: List[dict],
        start_date: date,
        study_days: List[str],
        preferred_time: str,
        exam_date: date
    ) -> dict:
        """Map sessions to actual calendar dates."""
        day_mapping = {
            "Monday": 0, "Tuesday": 1, "Wednesday": 2,
            "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6
        }

        time_slots = {
            "morning": "08:00",
            "afternoon": "15:00",
            "evening": "19:00"
        }

        study_day_indices = [day_mapping[d] for d in study_days if d in day_mapping]
        base_time = time_slots.get(preferred_time, "15:00")

        calendar_sessions = []
        current_date = start_date
        session_index = 0
        week_number = 1

        while session_index < len(schedule) and current_date < exam_date:
            if current_date.weekday() in study_day_indices:
                session = schedule[session_index]
                topics = session.get("topics", [])

                # Get primary topic name
                primary_topic = topics[0].get("topic", "Study Session") if topics else "Study Session"

                calendar_sessions.append({
                    "date": current_date.isoformat(),
                    "day": current_date.strftime("%A"),
                    "week": week_number,
                    "time": base_time,
                    "duration_minutes": int(session.get("hours", 1.5) * 60),
                    "topic": primary_topic,
                    "topics": topics,
                    "tasks": self._generate_tasks(topics),
                    "completed": False
                })
                session_index += 1

            current_date += timedelta(days=1)

            # Update week number
            if current_date.weekday() == 0:  # Monday
                week_number += 1

        return {"sessions": calendar_sessions}

    def _generate_tasks(self, topics: List[dict]) -> List[str]:
        """Generate task list for a session."""
        tasks = []

        for topic in topics[:2]:  # Limit to 2 topics
            topic_name = topic.get("topic", "")

            # Add reading task
            tasks.append(f"Study: {topic_name}")

            sections = topic.get("sections", [])
            for section in sections[:2]:
                section_title = section.get("title", "")
                if section_title:
                    tasks.append(f"Review: {section_title}")

                worked_examples = section.get("worked_examples", 0)
                if worked_examples:
                    tasks.append(f"Work through {worked_examples} examples")

                practice_problems = section.get("practice_problems", 0)
                if practice_problems:
                    tasks.append(f"Complete practice problems")

            # Add exam tips if available
            exam_tips = topic.get("exam_tips", [])
            if exam_tips:
                tasks.append("Review exam tips")

        return tasks[:6]  # Max 6 tasks per session

    def _add_milestones(
        self,
        calendar: dict,
        weeks_available: int,
        units: List[dict]
    ) -> dict:
        """Add practice tests and revision milestones."""
        milestones = []

        # Mid-point practice test
        if weeks_available >= 4:
            milestones.append({
                "week": weeks_available // 2,
                "type": "practice_test",
                "title": "Mid-term Practice Test",
                "description": "Complete a timed practice test covering topics studied so far"
            })

        # Final revision week
        if weeks_available >= 3:
            milestones.append({
                "week": weeks_available - 1,
                "type": "revision",
                "title": "Full Revision",
                "description": "Review all topics, focus on weak areas identified during study"
            })

        # Exam prep
        milestones.append({
            "week": weeks_available,
            "type": "exam_prep",
            "title": "Final Exam Prep",
            "description": "Past papers, exam techniques, and final review"
        })

        calendar["milestones"] = milestones
        return calendar
