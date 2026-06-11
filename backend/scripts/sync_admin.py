from pydantic import EmailStr, TypeAdapter, ValidationError

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.models import User
from app.db.repositories import SqlAlchemyUserRepository
from app.db.session import SessionLocal, create_database


def main() -> None:
    settings = get_settings()
    try:
        email = str(TypeAdapter(EmailStr).validate_python(settings.admin_email)).lower()
    except ValidationError as error:
        raise SystemExit(
            "MATHRAG_ADMIN_EMAIL không hợp lệ. "
            "Hãy dùng địa chỉ đầy đủ, ví dụ admin@mathrag.vn."
        ) from error

    if settings.admin_password == "ChangeMe123!":
        raise SystemExit(
            "MATHRAG_ADMIN_PASSWORD vẫn là mật khẩu mặc định. "
            "Hãy đổi mật khẩu trong backend/.env trước khi đồng bộ."
        )

    create_database()
    with SessionLocal() as session:
        repository = SqlAlchemyUserRepository(session)
        user = repository.get_by_email(email)
        action = "updated"
        if user is None:
            user = User(email=email)
            session.add(user)
            action = "created"

        user.full_name = settings.admin_full_name.strip()
        user.password_hash = hash_password(settings.admin_password)
        user.role = "admin"
        user.is_active = True
        session.commit()

    print(f"Admin account {action}: {email}")


if __name__ == "__main__":
    main()
