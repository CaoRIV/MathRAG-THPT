from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.api.v1.routes import (
    admin,
    auth,
    chat,
    documents,
    exams,
    health,
    quizzes,
    search,
    topics,
)

router = APIRouter()
router.include_router(health.router, tags=["system"])
router.include_router(auth.router, prefix="/auth", tags=["authentication"])
router.include_router(admin.router, prefix="/admin", tags=["admin"])
router.include_router(exams.router, prefix="/admin/exams", tags=["admin exams"])
authenticated = [Depends(get_current_user)]
router.include_router(chat.router, prefix="/chat", tags=["chat"], dependencies=authenticated)
router.include_router(
    search.router,
    prefix="/search",
    tags=["search"],
    dependencies=authenticated,
)
router.include_router(
    quizzes.router,
    prefix="/quizzes",
    tags=["quizzes"],
    dependencies=authenticated,
)
router.include_router(
    documents.router,
    prefix="/documents",
    tags=["documents"],
    dependencies=authenticated,
)
router.include_router(
    topics.router,
    prefix="/topics",
    tags=["topics"],
    dependencies=authenticated,
)
