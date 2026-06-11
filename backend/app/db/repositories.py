from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import Chunk, Document, Quiz, User


class DocumentRepository(Protocol):
    def list_documents(self) -> list[Document]: ...

    def get_document(self, document_id: str) -> Document | None: ...

    def list_chunks(self) -> list[Chunk]: ...


class SqlAlchemyDocumentRepository:
    def __init__(self, session: Session):
        self.session = session

    def list_documents(self) -> list[Document]:
        return list(self.session.scalars(select(Document).order_by(Document.title)))

    def get_document(self, document_id: str) -> Document | None:
        statement = (
            select(Document)
            .where(Document.id == document_id)
            .options(selectinload(Document.chunks))
        )
        return self.session.scalar(statement)

    def list_chunks(self) -> list[Chunk]:
        statement = select(Chunk).options(selectinload(Chunk.document))
        return list(self.session.scalars(statement))


class SqlAlchemyQuizRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, quiz: Quiz) -> Quiz:
        self.session.add(quiz)
        self.session.commit()
        self.session.refresh(quiz)
        return quiz

    def get(self, quiz_id: str) -> Quiz | None:
        return self.session.get(Quiz, quiz_id)


class SqlAlchemyUserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_email(self, email: str) -> User | None:
        return self.session.scalar(select(User).where(User.email == email.lower()))

    def get(self, user_id: str) -> User | None:
        return self.session.get(User, user_id)

    def add(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
