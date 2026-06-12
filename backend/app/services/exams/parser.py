from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import Chunk, Document, Exam, ExamQuestion, User
from app.ingestion.parsers import parse_document
from app.ingestion.parsers.exams import ExamParseResult, ParsedExamQuestion, parse_exam_sections
from app.schemas.exams import ExamParseReport, ExamProcessingStatus, ExtractionStatus

PARSER_VERSION = "exam-parser-v1"


class ExamParsingService:
    def __init__(self, session: Session):
        self.session = session

    def parse_document(self, document_id: str, current_user: User) -> ExamParseReport:
        document = self.session.scalar(
            select(Document)
            .where(Document.id == document_id)
            .options(selectinload(Document.chunks), selectinload(Document.exam))
        )
        if not document:
            raise ValueError("Document does not exist.")
        if document.content_type != "exam":
            raise ValueError("Only documents with content type 'exam' can be parsed.")
        if not document.source_path:
            raise ValueError("The original document file is unavailable.")

        source_path = Path(document.source_path)
        if not source_path.exists():
            raise ValueError("The original document file no longer exists.")

        exam = document.exam or Exam(
            document_id=document.id,
            title=document.title,
            grade=document.grade,
            description=document.description,
            processing_status=ExamProcessingStatus.UPLOADED,
            created_by=current_user.id,
            metadata_json={},
        )
        if not document.exam:
            self.session.add(exam)
            self.session.flush()

        exam.processing_status = ExamProcessingStatus.PARSING
        self._merge_metadata(
            exam,
            {
                "parser_version": PARSER_VERSION,
                "parse_error": None,
            },
        )
        self.session.commit()

        try:
            content = source_path.read_bytes()
            sections = parse_document(source_path, content)
            result = parse_exam_sections(sections)
            if not result.questions:
                raise ValueError(
                    "No exam questions were detected. Use labels such as 'Câu 1.' in the file."
                )
            report = self._persist_result(document, exam, result)
            self.session.commit()
            return report
        except Exception as error:
            self.session.rollback()
            failed_exam = self.session.get(Exam, exam.id)
            if failed_exam:
                failed_exam.processing_status = ExamProcessingStatus.FAILED
                self._merge_metadata(
                    failed_exam,
                    {
                        "parser_version": PARSER_VERSION,
                        "parse_error": str(error),
                    },
                )
                self.session.commit()
            if isinstance(error, ValueError):
                raise
            raise ValueError("Unable to parse the exam document.") from error

    def _persist_result(
        self,
        document: Document,
        exam: Exam,
        result: ExamParseResult,
    ) -> ExamParseReport:
        refreshed_exam = self.session.scalar(
            select(Exam).where(Exam.id == exam.id).options(selectinload(Exam.questions))
        )
        if not refreshed_exam:
            raise ValueError("Exam record disappeared during parsing.")
        exam = refreshed_exam
        existing = {item.question_number: item for item in exam.questions}
        detected_numbers = {item.question_number for item in result.questions}
        chunks_by_page = self._chunks_by_page(document.chunks)

        created = 0
        updated = 0
        preserved = 0
        removed = 0
        all_warnings = list(result.warnings)

        for parsed in result.questions:
            all_warnings.extend(parsed.warnings)
            question = existing.get(parsed.question_number)
            if question and question.extraction_status == ExtractionStatus.VERIFIED:
                preserved += 1
                continue
            source_chunk_id = self._source_chunk_id(parsed.page_number, chunks_by_page)
            if question:
                self._apply_parsed_question(question, parsed, source_chunk_id)
                updated += 1
            else:
                exam.questions.append(self._new_question(exam.id, parsed, source_chunk_id))
                created += 1

        for question in list(exam.questions):
            if (
                question.question_number not in detected_numbers
                and question.extraction_status != ExtractionStatus.VERIFIED
            ):
                exam.questions.remove(question)
                self.session.delete(question)
                removed += 1

        self.session.flush()
        active_questions = list(exam.questions)
        exam.question_count = len(active_questions)
        needs_review = sum(
            item.extraction_status != ExtractionStatus.VERIFIED for item in active_questions
        )
        exam.processing_status = ExamProcessingStatus.NEEDS_REVIEW

        report_data = {
            "detected_questions": len(result.questions),
            "answers_matched": result.answer_count,
            "solutions_matched": result.solution_count,
            "formulas_detected": result.formula_count,
            "created_questions": created,
            "updated_questions": updated,
            "preserved_verified_questions": preserved,
            "removed_stale_questions": removed,
            "questions_needing_review": needs_review,
            "warnings": all_warnings,
        }
        self._merge_metadata(
            exam,
            {
                "parser_version": PARSER_VERSION,
                "parse_error": None,
                "last_parse_report": report_data,
            },
        )
        return ExamParseReport(
            exam_id=exam.id,
            document_id=document.id,
            processing_status=exam.processing_status,
            **report_data,
        )

    @staticmethod
    def _new_question(
        exam_id: str,
        parsed: ParsedExamQuestion,
        source_chunk_id: str | None,
    ) -> ExamQuestion:
        question = ExamQuestion(exam_id=exam_id)
        ExamParsingService._apply_parsed_question(
            question,
            parsed,
            source_chunk_id,
        )
        return question

    @staticmethod
    def _apply_parsed_question(
        question: ExamQuestion,
        parsed: ParsedExamQuestion,
        source_chunk_id: str | None,
    ) -> None:
        question.source_chunk_id = source_chunk_id
        question.question_number = parsed.question_number
        question.question_type = parsed.question_type
        question.prompt_markdown = parsed.prompt_markdown
        question.options_json = parsed.options
        question.correct_answer = parsed.correct_answer
        question.solution_markdown = parsed.solution_markdown
        question.difficulty = None
        question.topics = parsed.topics
        question.formulas = parsed.formulas
        question.page_number = parsed.page_number
        question.extraction_status = ExtractionStatus.NEEDS_REVIEW
        question.extraction_confidence = parsed.confidence
        question.metadata_json = {
            "parser_version": PARSER_VERSION,
            "warnings": parsed.warnings,
        }

    @staticmethod
    def _chunks_by_page(chunks: list[Chunk]) -> dict[int | None, list[Chunk]]:
        result: dict[int | None, list[Chunk]] = {}
        for chunk in sorted(chunks, key=lambda item: item.chunk_order):
            result.setdefault(chunk.page_number, []).append(chunk)
        return result

    @staticmethod
    def _source_chunk_id(
        page_number: int | None,
        chunks_by_page: dict[int | None, list[Chunk]],
    ) -> str | None:
        same_page = chunks_by_page.get(page_number)
        if same_page:
            return same_page[0].id
        for chunks in chunks_by_page.values():
            if chunks:
                return chunks[0].id
        return None

    @staticmethod
    def _merge_metadata(exam: Exam, values: dict) -> None:
        exam.metadata_json = {**(exam.metadata_json or {}), **values}
