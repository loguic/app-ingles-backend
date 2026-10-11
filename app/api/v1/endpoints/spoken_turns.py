from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.spoken_turn import (
    SpokenTurnEvaluationRequest,
    SpokenTurnEvaluationResponse,
)
from app.services.experience_attempt_service import get_experience_attempt_state
from app.services.production_audio_storage_service import (
    resolve_production_audio_path,
)
from app.services.spoken_turn_evaluation_service import (
    OllamaSpokenTurnRuntimeError,
    evaluate_spoken_turn,
)


router = APIRouter()


@router.post(
    "/spoken-turn-evaluations",
    response_model=SpokenTurnEvaluationResponse,
)
def evaluate_current_spoken_turn(
    request: SpokenTurnEvaluationRequest,
    db: Session = Depends(get_db),
) -> SpokenTurnEvaluationResponse:
    """Return non-authoritative A1 coaching from real turn evidence."""
    try:
        if request.experience_attempt_id is not None:
            attempt = get_experience_attempt_state(request.experience_attempt_id, db)
            if attempt is None:
                raise ValueError("Experience attempt does not exist")
            if attempt.status != "in_progress":
                raise ValueError("Spoken turn requires an in-progress experience attempt")
        if request.audio_reference is not None:
            resolve_production_audio_path(request.audio_reference)
        return evaluate_spoken_turn(request)
    except OllamaSpokenTurnRuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except (RuntimeError, ValueError, FileNotFoundError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
