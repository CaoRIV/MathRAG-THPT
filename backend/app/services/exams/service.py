from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Chunk, Document, Exam, ExamQuestion, User
from app.db.repositories import SqlAlchemyExamRepository
from app.schemas.exams import (
    BulkVerificationResult,
    ExamCreate,
    ExamDetail,
    ExamList,
    ExamProcessingStatus,
    ExamQuestionCreate,
    ExamQuestionResponse,
    ExamQuestionUpdate,
    ExamSummary,
    ExamUpdate,
    ExtractionStatus,
    QuestionReviewIssue,
)
from app.services.retrieval.formula import extract_formulas, normalize_formula


class ExamService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = SqlAlchemyExamRepository(session)

    def list_exams(self) -> ExamList:
        exams = self.repository.list()
        return ExamList(
            items=[self._to_summary(exam) for exam in exams],
            total=len(exams),
        )

    def get_exam(self, exam_id: str) -> ExamDetail | None:
        exam = self.repository.get(exam_id)
        return self._to_detail(exam) if exam else None

    def create_exam(self, request: ExamCreate, current_user: User) -> ExamDetail:
        if request.document_id:
            document = self.session.get(Document, request.document_id)
            if not document:
                raise ValueError("Document does not exist.")
            if self.repository.get_by_document(request.document_id):
                raise ValueError("This document is already linked to an exam.")

        exam = Exam(
            document_id=request.document_id,
            title=request.title.strip(),
            year=request.year,
            school=self._clean(request.school),
            province=self._clean(request.province),
            exam_type=request.exam_type.value,
            duration_minutes=request.duration_minutes,
            expected_question_count=request.expected_question_count,
            question_count=0,
            grade=request.grade,
            processing_status=request.processing_status.value,
            description=self._clean(request.description),
            metadata_json=request.metadata,
            created_by=current_user.id,
        )
        self.session.add(exam)
        self.session.commit()
        return self._to_detail(self.repository.get(exam.id) or exam)

    def update_exam(self, exam_id: str, request: ExamUpdate) -> ExamDetail | None:
        exam = self.repository.get(exam_id)
        if not exam:
            return None
        values = request.model_dump(exclude_unset=True)
        if "processing_status" in values:
            status = values["processing_status"]
            if status in {
                ExamProcessingStatus.APPROVED,
                ExamProcessingStatus.INDEXED,
            }:
                if not exam.questions:
                    raise ValueError("An exam without questions cannot be approved.")
                if any(
                    item.extraction_status != ExtractionStatus.VERIFIED for item in exam.questions
                ):
                    raise ValueError("All questions must be verified before approving the exam.")
        field_map = {"metadata": "metadata_json"}
        for field, value in values.items():
            target = field_map.get(field, field)
            if hasattr(value, "value"):
                value = value.value
            if field in {"title", "school", "province", "description"}:
                value = self._clean(value)
            setattr(exam, target, value)
        self.session.commit()
        return self._to_detail(self.repository.get(exam.id) or exam)

    def add_question(
        self,
        exam_id: str,
        request: ExamQuestionCreate,
    ) -> ExamQuestionResponse | None:
        exam = self.repository.get(exam_id)
        if not exam:
            return None
        self._validate_source_chunk(exam, request.source_chunk_id)
        question = ExamQuestion(
            exam_id=exam.id,
            source_chunk_id=request.source_chunk_id,
            question_number=request.question_number,
            question_type=request.question_type.value,
            prompt_markdown=request.prompt_markdown.strip(),
            options_json=[
                {
                    "key": option.key.strip().upper(),
                    "content_markdown": option.content_markdown.strip(),
                }
                for option in request.options
            ],
            correct_answer=self._clean_answer(request.correct_answer),
            solution_markdown=self._clean(request.solution_markdown),
            difficulty=request.difficulty.value if request.difficulty else None,
            topics=self._clean_list(request.topics),
            formulas=[formula.model_dump() for formula in request.formulas],
            page_number=request.page_number,
            extraction_status=request.extraction_status.value,
            extraction_confidence=request.extraction_confidence,
            metadata_json=request.metadata,
        )
        exam.questions.append(question)
        exam.question_count = len(exam.questions)
        try:
            self.session.commit()
        except IntegrityError as error:
            self.session.rollback()
            raise ValueError(
                f"Question number {request.question_number} already exists in this exam."
            ) from error
        self.session.refresh(question)
        return self._to_question(question)

    def update_question(
        self,
        exam_id: str,
        question_id: str,
        request: ExamQuestionUpdate,
    ) -> ExamQuestionResponse | None:
        question = self.repository.get_question(exam_id, question_id)
        if not question:
            return None
        exam = self.repository.get(exam_id)
        if not exam:
            return None

        values = request.model_dump(exclude_unset=True)
        validation_payload = {
            "source_chunk_id": question.source_chunk_id,
            "question_number": question.question_number,
            "question_type": question.question_type,
            "prompt_markdown": question.prompt_markdown,
            "options": question.options_json,
            "correct_answer": question.correct_answer,
            "solution_markdown": question.solution_markdown,
            "difficulty": question.difficulty,
            "topics": question.topics,
            "formulas": question.formulas,
            "page_number": question.page_number,
            "extraction_status": question.extraction_status,
            "extraction_confidence": question.extraction_confidence,
            "metadata": question.metadata_json,
        }
        validation_payload.update(values)
        validated = ExamQuestionCreate.model_validate(validation_payload)
        if values.get("extraction_status") == ExtractionStatus.VERIFIED:
            issues = self._review_issues(validated)
            if issues:
                raise ValueError("Question cannot be verified: " + "; ".join(issues))
        if "source_chunk_id" in values:
            self._validate_source_chunk(exam, values["source_chunk_id"])
        field_map = {
            "options": "options_json",
            "metadata": "metadata_json",
        }
        for field, value in values.items():
            target = field_map.get(field, field)
            if field == "options" and value is not None:
                value = [
                    {
                        "key": option["key"].strip().upper(),
                        "content_markdown": option["content_markdown"].strip(),
                    }
                    for option in value
                ]
            elif field == "formulas" and value is not None:
                value = [
                    formula.model_dump() if hasattr(formula, "model_dump") else formula
                    for formula in value
                ]
            elif field == "topics" and value is not None:
                value = self._clean_list(value)
            elif field == "correct_answer":
                value = self._clean_answer(value)
            elif field in {"prompt_markdown", "solution_markdown"}:
                value = self._clean(value)
            elif hasattr(value, "value"):
                value = value.value
            setattr(question, target, value)
        content_fields = {
            "question_number",
            "question_type",
            "prompt_markdown",
            "options",
            "correct_answer",
            "solution_markdown",
            "topics",
            "formulas",
        }
        if (
            question.extraction_status == ExtractionStatus.VERIFIED
            and content_fields.intersection(values)
            and "extraction_status" not in values
        ):
            question.extraction_status = ExtractionStatus.NEEDS_REVIEW
        if content_fields.intersection(values) and exam.processing_status in {
            ExamProcessingStatus.APPROVED,
            ExamProcessingStatus.INDEXED,
        }:
            exam.processing_status = ExamProcessingStatus.NEEDS_REVIEW
        if (
            "extraction_status" in values
            and question.extraction_status != ExtractionStatus.VERIFIED
            and exam.processing_status
            in {ExamProcessingStatus.APPROVED, ExamProcessingStatus.INDEXED}
        ):
            exam.processing_status = ExamProcessingStatus.NEEDS_REVIEW
        if content_fields.intersection(values) and "formulas" not in values:
            formula_source = "\n".join(
                [
                    question.prompt_markdown,
                    *(item.get("content_markdown", "") for item in question.options_json),
                    question.solution_markdown or "",
                ]
            )
            question.formulas = [
                {
                    "raw_text": formula,
                    "latex": formula,
                    "normalized": normalize_formula(formula),
                }
                for formula in extract_formulas(formula_source)
            ]
        try:
            self.session.commit()
        except IntegrityError as error:
            self.session.rollback()
            raise ValueError(
                f"Question number {request.question_number} already exists in this exam."
            ) from error
        self.session.refresh(question)
        return self._to_question(question)

    def verify_all_ready(self, exam_id: str) -> BulkVerificationResult | None:
        exam = self.repository.get(exam_id)
        if not exam:
            return None
        verified_count = 0
        issues: list[QuestionReviewIssue] = []
        for question in exam.questions:
            if question.extraction_status == ExtractionStatus.REJECTED:
                issues.append(
                    QuestionReviewIssue(
                        question_id=question.id,
                        question_number=question.question_number,
                        issues=["Câu hỏi đang bị từ chối."],
                    )
                )
                continue
            try:
                payload = ExamQuestionCreate.model_validate(
                    self._question_validation_payload(question)
                )
            except ValidationError:
                issues.append(
                    QuestionReviewIssue(
                        question_id=question.id,
                        question_number=question.question_number,
                        issues=["Dữ liệu cấu trúc của câu hỏi chưa hợp lệ."],
                    )
                )
                continue
            question_issues = self._review_issues(payload)
            if question_issues:
                issues.append(
                    QuestionReviewIssue(
                        question_id=question.id,
                        question_number=question.question_number,
                        issues=question_issues,
                    )
                )
                continue
            if question.extraction_status != ExtractionStatus.VERIFIED:
                question.extraction_status = ExtractionStatus.VERIFIED
                verified_count += 1
        exam.processing_status = ExamProcessingStatus.NEEDS_REVIEW
        self.session.commit()
        refreshed = self.repository.get(exam.id) or exam
        return BulkVerificationResult(
            exam_id=exam.id,
            verified_count=verified_count,
            skipped_count=len(issues),
            issues=issues,
            exam=self._to_detail(refreshed),
        )

    def approve_exam(self, exam_id: str) -> ExamDetail | None:
        return self.update_exam(
            exam_id,
            ExamUpdate(processing_status=ExamProcessingStatus.APPROVED),
        )

    @staticmethod
    def _question_validation_payload(question: ExamQuestion) -> dict:
        return {
            "source_chunk_id": question.source_chunk_id,
            "question_number": question.question_number,
            "question_type": question.question_type,
            "prompt_markdown": question.prompt_markdown,
            "options": question.options_json,
            "correct_answer": question.correct_answer,
            "solution_markdown": question.solution_markdown,
            "difficulty": question.difficulty,
            "topics": question.topics,
            "formulas": question.formulas,
            "page_number": question.page_number,
            "extraction_status": question.extraction_status,
            "extraction_confidence": question.extraction_confidence,
            "metadata": question.metadata_json,
        }

    @staticmethod
    def _review_issues(question: ExamQuestionCreate) -> list[str]:
        issues: list[str] = []
        if not question.prompt_markdown.strip():
            issues.append("Thiếu nội dung câu hỏi.")
        option_keys = {option.key.strip().upper() for option in question.options}
        answer = (question.correct_answer or "").strip().upper()
        if question.question_type == "multiple_choice":
            if len(question.options) < 2:
                issues.append("Câu trắc nghiệm cần ít nhất 2 phương án.")
            if not answer or answer not in option_keys:
                issues.append("Đáp án đúng phải trùng với một phương án.")
        elif question.question_type == "true_false":
            if len(question.options) != 4:
                issues.append("Câu đúng/sai cần đủ 4 mệnh đề.")
            normalized_answer = answer.replace("D", "Đ")
            if len(normalized_answer) != 4 or any(
                value not in {"Đ", "S"} for value in normalized_answer
            ):
                issues.append("Đáp án đúng/sai phải gồm 4 ký tự Đ hoặc S.")
        elif not answer:
            issues.append("Câu trả lời ngắn chưa có đáp án.")
        if not (question.solution_markdown or "").strip():
            issues.append("Thiếu lời giải chi tiết.")
        return issues

    def _validate_source_chunk(self, exam: Exam, chunk_id: str | None) -> None:
        if not chunk_id:
            return
        chunk = self.session.scalar(select(Chunk).where(Chunk.id == chunk_id))
        if not chunk:
            raise ValueError("Source chunk does not exist.")
        if exam.document_id and chunk.document_id != exam.document_id:
            raise ValueError("Source chunk must belong to the exam document.")

    @staticmethod
    def _clean(value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @staticmethod
    def _clean_answer(value: str | None) -> str | None:
        cleaned = ExamService._clean(value)
        return cleaned.upper() if cleaned and len(cleaned) <= 10 else cleaned

    @staticmethod
    def _clean_list(values: list[str]) -> list[str]:
        return list(dict.fromkeys(item.strip() for item in values if item.strip()))

    @staticmethod
    def _to_summary(exam: Exam) -> ExamSummary:
        return ExamSummary(
            id=exam.id,
            document_id=exam.document_id,
            title=exam.title,
            year=exam.year,
            school=exam.school,
            province=exam.province,
            exam_type=exam.exam_type,
            duration_minutes=exam.duration_minutes,
            expected_question_count=exam.expected_question_count,
            question_count=exam.question_count,
            grade=exam.grade,
            processing_status=exam.processing_status,
            description=exam.description,
            created_by=exam.created_by,
            created_at=exam.created_at,
            updated_at=exam.updated_at,
        )

    @staticmethod
    def _to_question(question: ExamQuestion) -> ExamQuestionResponse:
        return ExamQuestionResponse(
            id=question.id,
            exam_id=question.exam_id,
            source_chunk_id=question.source_chunk_id,
            question_number=question.question_number,
            question_type=question.question_type,
            prompt_markdown=question.prompt_markdown,
            options=question.options_json,
            correct_answer=question.correct_answer,
            solution_markdown=question.solution_markdown,
            difficulty=question.difficulty,
            topics=question.topics,
            formulas=question.formulas,
            page_number=question.page_number,
            extraction_status=question.extraction_status,
            extraction_confidence=question.extraction_confidence,
            metadata=question.metadata_json,
            created_at=question.created_at,
            updated_at=question.updated_at,
        )

    @classmethod
    def _to_detail(cls, exam: Exam) -> ExamDetail:
        return ExamDetail(
            **cls._to_summary(exam).model_dump(),
            metadata=exam.metadata_json,
            questions=[cls._to_question(question) for question in exam.questions],
        )
