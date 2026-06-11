from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import Chunk, Document, Exam, ExamQuestion, Quiz, User


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


class SqlAlchemyExamRepository:
    def __init__(self, session: Session):
        self.session = session

    def list(self) -> list[Exam]:
        statement = (
            select(Exam)
            .options(selectinload(Exam.questions))
            .order_by(Exam.created_at.desc())
        )
        return list(self.session.scalars(statement))

    def get(self, exam_id: str) -> Exam | None:
        statement = (
            select(Exam)
            .where(Exam.id == exam_id)
            .options(selectinload(Exam.questions))
        )
        return self.session.scalar(statement)

    def get_by_document(self, document_id: str) -> Exam | None:
        return self.session.scalar(select(Exam).where(Exam.document_id == document_id))

    def get_question(self, exam_id: str, question_id: str) -> ExamQuestion | None:
        return self.session.scalar(
            select(ExamQuestion).where(
                ExamQuestion.id == question_id,
                ExamQuestion.exam_id == exam_id,
            )
        )
