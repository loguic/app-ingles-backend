from sqlalchemy.orm import Session

from app.db.models import UserProgress
from app.services.content_service import get_skill_ids_by_exercise_id
from app.schemas.progress import ProgressRecommendation, ProgressRecord, ProgressStats, ReviewRecommendation, SkillMastery, StudentDashboard


def save_progress(record: ProgressRecord, db: Session) -> ProgressRecord:
    item = UserProgress(
        user_id=record.user_id,
        level_id=record.level_id,
        unit_id=record.unit_id,
        lesson_id=record.lesson_id,
        exercise_id=record.exercise_id,
        selected_index=record.selected_index,
        correct=record.correct,
    )

    db.add(item)
    db.commit()

    return record


def get_progress_by_user(user_id: str, db: Session) -> list[ProgressRecord]:
    records = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == user_id)
        .all()
    )

    return [
        ProgressRecord(
            user_id=record.user_id,
            level_id=record.level_id,
            unit_id=record.unit_id,
            lesson_id=record.lesson_id,
            exercise_id=record.exercise_id,
            selected_index=record.selected_index,
            correct=record.correct,
        )
        for record in records
    ]


def get_progress_stats(user_id: str, db: Session) -> ProgressStats:
    records = get_progress_by_user(user_id, db)

    total_attempts = len(records)
    correct_attempts = sum(1 for record in records if record.correct)

    accuracy = (
        correct_attempts / total_attempts
        if total_attempts > 0 else 0.0
    )

    return ProgressStats(
        user_id=user_id,
        total_attempts=total_attempts,
        correct_attempts=correct_attempts,
        accuracy=round(accuracy, 2),
    )


def get_progress_recommendation(user_id: str, db: Session) -> ProgressRecommendation:
    """Generate a basic learning recommendation from user accuracy."""
    stats = get_progress_stats(user_id, db)

    if stats.total_attempts == 0:
        message = "Start with the first lesson to generate your learning progress."
    elif stats.accuracy < 0.70:
        message = "Review weak skills before moving forward."
    else:
        message = "Good progress. Continue with the next lesson."

    return ProgressRecommendation(
        user_id=user_id,
        accuracy=stats.accuracy,
        message=message,
    )


def get_skill_mastery(user_id: str, skill_id: str, db: Session) -> SkillMastery:
    """Calculate the user's mastery score for a specific skill."""
    records = get_progress_by_user(user_id, db)

    related_records = [
        record
        for record in records
        if skill_id in get_skill_ids_by_exercise_id(record.exercise_id)
    ]

    total_attempts = len(related_records)
    correct_attempts = sum(1 for record in related_records if record.correct)

    mastery_score = (
        correct_attempts / total_attempts
        if total_attempts > 0 else 0.0
    )

    return SkillMastery(
        user_id=user_id,
        skill_id=skill_id,
        total_attempts=total_attempts,
        correct_attempts=correct_attempts,
        mastery_score=round(mastery_score, 2),
    )



def get_review_recommendation(
    user_id: str,
    skill_id: str,
    db: Session,
) -> ReviewRecommendation:
    """Return whether a user should review a specific skill."""
    mastery = get_skill_mastery(user_id, skill_id, db)

    should_review = mastery.mastery_score < 0.70

    if should_review:
        message = "Review this skill before moving forward."
    else:
        message = "This skill is ready. Continue with the next lesson."

    return ReviewRecommendation(
        user_id=user_id,
        skill_id=skill_id,
        mastery_score=mastery.mastery_score,
        should_review=should_review,
        message=message,
    )



def get_student_dashboard(user_id: str, db: Session) -> StudentDashboard:
    """Return the basic dashboard data for a student."""
    stats = get_progress_stats(user_id, db)
    recommendation = get_progress_recommendation(user_id, db)

    return StudentDashboard(
        user_id=user_id,
        total_attempts=stats.total_attempts,
        correct_attempts=stats.correct_attempts,
        accuracy=stats.accuracy,
        recommendation=recommendation.message,
    )
