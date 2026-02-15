from fastapi import APIRouter, HTTPException
from app.schemas.content import ExerciseSubmission, ExerciseResult
from app.services.content_service import evaluate_exercise

router = APIRouter()

@router.post("/exercises/{exercise_id}/submit", response_model=ExerciseResult)
def submit_exercise(exercise_id: str, payload: ExerciseSubmission) -> ExerciseResult:
    result = evaluate_exercise(exercise_id, payload.selected_index)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Exercise '{exercise_id}' not found")
    return ExerciseResult(correct=result)
