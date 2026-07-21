from fastapi import APIRouter
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.levels import router as levels_router
from app.api.v1.endpoints.content import router as content_router
from app.api.v1.endpoints.exercises import router as exercises_router
from app.api.v1.endpoints.progress import router as progress_router
from app.api.v1.endpoints.conversation_attempts import router as conversation_attempts_router

router = APIRouter(prefix="/api/v1")

router.include_router(health_router)
router.include_router(levels_router)
router.include_router(content_router)
router.include_router(exercises_router)
router.include_router(progress_router)
router.include_router(conversation_attempts_router)
