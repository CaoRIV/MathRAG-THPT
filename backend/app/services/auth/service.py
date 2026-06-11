from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.security import create_access_token, hash_password, verify_password
from app.db.models import User
from app.db.repositories import SqlAlchemyUserRepository
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserResponse


class AuthService:
    def __init__(self, session: Session, settings: Settings):
        self.repository = SqlAlchemyUserRepository(session)
        self.settings = settings

    def register(self, request: RegisterRequest) -> AuthResponse:
        if self.repository.get_by_email(request.email):
            raise ValueError("Email này đã được sử dụng.")
        user = self.repository.add(
            User(
                email=request.email.lower(),
                full_name=request.full_name.strip(),
                password_hash=hash_password(request.password),
                role="user",
            )
        )
        return self._build_response(user)

    def login(self, request: LoginRequest) -> AuthResponse:
        user = self.repository.get_by_email(request.email)
        if not user or not verify_password(request.password, user.password_hash):
            raise ValueError("Email hoặc mật khẩu không chính xác.")
        if not user.is_active:
            raise PermissionError("Tài khoản đã bị vô hiệu hóa.")
        return self._build_response(user)

    def _build_response(self, user: User) -> AuthResponse:
        token, expires_in = create_access_token(user.id, user.role, self.settings)
        return AuthResponse(
            access_token=token,
            expires_in=expires_in,
            user=to_user_response(user),
        )


def to_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
    )
