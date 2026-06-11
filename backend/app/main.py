from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router
from app.container import ServiceContainer
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.security import hash_password
from app.db.models import User
from app.db.repositories import SqlAlchemyUserRepository
from app.db.session import SessionLocal, create_database


def ensure_admin_account() -> None:
    settings = get_settings()
    with SessionLocal() as session:
        repository = SqlAlchemyUserRepository(session)
        if repository.get_by_email(settings.admin_email):
            return
        repository.add(
            User(
                email=settings.admin_email.lower(),
                full_name=settings.admin_full_name,
                password_hash=hash_password(settings.admin_password),
                role="admin",
            )
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging()
    create_database()
    ensure_admin_account()
    container = ServiceContainer(settings)
    await container.initialize()
    app.state.container = container
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Grounded RAG API for Vietnamese high-school mathematics.",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(router, prefix=settings.api_prefix)
    return application


app = create_app()
