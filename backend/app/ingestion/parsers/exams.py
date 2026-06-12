import re
from dataclasses import dataclass, field

from app.ingestion.models import ParsedSection
from app.ingestion.normalizers import normalize_text
from app.services.retrieval.formula import extract_formulas, normalize_formula

QUESTION_PATTERN = re.compile(r"(?im)^\s*(?:câu|bài)\s*(\d{1,3})(?:\s*[\.\):\-]\s*|\s+)")
MAJOR_SECTION_PATTERN = re.compile(
    r"(?im)^\s*(?:phần\s+[IVX\d]+[.:\-]?\s*)?"
    r"(?:đáp\s+án|bảng\s+đáp\s+án|"
    r"lời\s+giải|hướng\s+dẫn\s+giải|giải\s+chi\s+tiết)\s*:?\s*$"
)
ANSWER_SECTION_PATTERN = re.compile(
    r"(?im)^\s*(?:phần\s+[IVX\d]+[.:\-]?\s*)?"
    r"(?:đáp\s+án|bảng\s+đáp\s+án)\s*:?\s*$"
)
SOLUTION_SECTION_PATTERN = re.compile(
    r"(?im)^\s*(?:phần\s+[IVX\d]+[.:\-]?\s*)?"
    r"(?:lời\s+giải|hướng\s+dẫn\s+giải|"
    r"giải\s+chi\s+tiết)\s*:?\s*$"
)
MULTIPLE_CHOICE_OPTION_PATTERN = re.compile(
    r"(?ms)(?:(?<=^)|(?<=\n)|(?<=\s))([A-D])\s*[\.\):]\s*"
    r"(.+?)(?=(?:(?<=\n)|(?<=\s))[A-D]\s*[\.\):]\s*|\Z)"
)
TRUE_FALSE_OPTION_PATTERN = re.compile(
    r"(?ms)(?:(?<=^)|(?<=\n)|(?<=\s))([a-d])\s*[\.\):]\s*"
    r"(.+?)(?=(?:(?<=\n)|(?<=\s))[a-d]\s*[\.\):]\s*|\Z)"
)
ANSWER_PAIR_PATTERN = re.compile(r"(?i)(?<!\d)(\d{1,3})\s*[\.\):\-]?\s*([A-D])\b")
ANSWER_SEQUENCE_PATTERN = re.compile(r"(?i)(?<!\d)(\d{1,3})\s*[\.\):\-]?\s*((?:Đ|S|D){4})\b")
SHORT_ANSWER_PATTERN = re.compile(r"(?im)(?:^|\s)(?:câu\s*)?(\d{1,3})\s*[:=]\s*([^\s;|]{1,100})")
UNICODE_MATH_PATTERN = re.compile(r"[∫√π≤≥≠≈∑∞]|[A-Za-z]\s*[=<>]\s*[^,.;\n]{1,120}")


@dataclass
class ParsedExamQuestion:
    question_number: int
    question_type: str
    prompt_markdown: str
    options: list[dict[str, str]]
    correct_answer: str | None
    solution_markdown: str | None
    topics: list[str]
    formulas: list[dict[str, str | None]]
    page_number: int | None
    confidence: float
    warnings: list[str] = field(default_factory=list)


@dataclass
class ExamParseResult:
    questions: list[ParsedExamQuestion]
    answer_count: int
    solution_count: int
    formula_count: int
    warnings: list[str]


@dataclass(frozen=True)
class TextRange:
    start: int
    end: int
    page_number: int | None


def parse_exam_sections(sections: list[ParsedSection]) -> ExamParseResult:
    text, ranges = _join_sections(sections)
    if not text:
        return ExamParseResult([], 0, 0, 0, ["Tài liệu không có nội dung văn bản."])

    first_major_section = MAJOR_SECTION_PATTERN.search(text)
    question_region_end = first_major_section.start() if first_major_section else len(text)
    question_region = text[:question_region_end]
    answer_region = _section_content(text, ANSWER_SECTION_PATTERN, SOLUTION_SECTION_PATTERN)
    solution_region = _section_content(text, SOLUTION_SECTION_PATTERN, None)
    answers = _parse_answers(answer_region)
    solutions = _parse_numbered_blocks(solution_region)

    matches = list(QUESTION_PATTERN.finditer(question_region))
    questions: list[ParsedExamQuestion] = []
    global_warnings: list[str] = []
    seen_numbers: set[int] = set()

    for index, match in enumerate(matches):
        number = int(match.group(1))
        if number in seen_numbers:
            global_warnings.append(f"Phát hiện câu {number} bị lặp trong tài liệu.")
            continue
        seen_numbers.add(number)
        end = matches[index + 1].start() if index + 1 < len(matches) else len(question_region)
        block = normalize_text(question_region[match.end() : end])
        if not block:
            global_warnings.append(f"Câu {number} không có nội dung.")
            continue
        page_number = _page_at_offset(match.start(), ranges)
        parsed = _parse_question_block(
            number=number,
            block=block,
            answer=answers.get(number),
            solution=solutions.get(number),
            page_number=page_number,
        )
        questions.append(parsed)

    if not matches:
        global_warnings.append(
            "Không nhận diện được câu hỏi. Tài liệu cần có nhãn như 'Câu 1.' hoặc 'Bài 1:'."
        )

    questions.sort(key=lambda item: item.question_number)
    formula_count = sum(len(item.formulas) for item in questions)
    return ExamParseResult(
        questions=questions,
        answer_count=sum(item.correct_answer is not None for item in questions),
        solution_count=sum(item.solution_markdown is not None for item in questions),
        formula_count=formula_count,
        warnings=global_warnings,
    )


def _parse_question_block(
    number: int,
    block: str,
    answer: str | None,
    solution: str | None,
    page_number: int | None,
) -> ParsedExamQuestion:
    true_false_matches = list(TRUE_FALSE_OPTION_PATTERN.finditer(block))
    true_false = len(true_false_matches) >= 2 or bool(
        re.search(r"(?i)(đúng|sai).{0,40}(mệnh đề|ý)|mỗi\s+ý\s+[a-d]", block)
    )
    option_matches = (
        true_false_matches if true_false else list(MULTIPLE_CHOICE_OPTION_PATTERN.finditer(block))
    )
    options = [
        {
            "key": match.group(1).upper(),
            "content_markdown": normalize_text(match.group(2)),
        }
        for match in option_matches
        if normalize_text(match.group(2))
    ]
    prompt_end = option_matches[0].start() if option_matches else len(block)
    prompt = normalize_text(block[:prompt_end])
    question_type = (
        "true_false" if true_false else "multiple_choice" if len(options) >= 2 else "short_answer"
    )

    warnings: list[str] = []
    if question_type == "multiple_choice" and len(options) < 4:
        warnings.append(f"Câu {number} chỉ nhận diện được {len(options)} phương án.")
    if question_type == "true_false" and len(options) < 4:
        warnings.append(f"Câu {number} chưa nhận diện đủ 4 mệnh đề đúng/sai.")
    if not answer:
        warnings.append(f"Câu {number} chưa ghép được đáp án.")
    if not solution:
        warnings.append(f"Câu {number} chưa ghép được lời giải.")

    full_content = "\n".join(
        part for part in [prompt, *(item["content_markdown"] for item in options), solution] if part
    )
    formulas = _extract_formula_records(full_content)
    confidence = 0.35
    confidence += 0.25 if len(options) >= 4 else 0.12 if len(options) >= 2 else 0
    confidence += 0.15 if answer else 0
    confidence += 0.1 if solution else 0
    confidence += 0.1 if len(prompt) >= 20 else 0
    confidence += 0.05 if page_number else 0

    return ParsedExamQuestion(
        question_number=number,
        question_type=question_type,
        prompt_markdown=prompt,
        options=options,
        correct_answer=answer,
        solution_markdown=solution,
        topics=_detect_topics(full_content),
        formulas=formulas,
        page_number=page_number,
        confidence=min(confidence, 1.0),
        warnings=warnings,
    )


def _join_sections(sections: list[ParsedSection]) -> tuple[str, list[TextRange]]:
    parts: list[str] = []
    ranges: list[TextRange] = []
    offset = 0
    for section in sections:
        content = normalize_text(section.content)
        if not content:
            continue
        heading = normalize_text(section.heading or "")
        if heading and not re.fullmatch(r"(?i)trang\s+\d+", heading):
            content = f"{heading}\n{content}"
        if parts:
            parts.append("\n\n")
            offset += 2
        start = offset
        parts.append(content)
        offset += len(content)
        ranges.append(TextRange(start=start, end=offset, page_number=section.page_number))
    return "".join(parts), ranges


def _section_content(
    text: str,
    start_pattern: re.Pattern[str],
    end_pattern: re.Pattern[str] | None,
) -> str:
    start = start_pattern.search(text)
    if not start:
        return ""
    end = end_pattern.search(text, start.end()) if end_pattern else None
    return text[start.end() : end.start() if end else len(text)]


def _parse_answers(text: str) -> dict[int, str]:
    answers: dict[int, str] = {}
    for match in ANSWER_PAIR_PATTERN.finditer(text):
        answers[int(match.group(1))] = match.group(2).upper()
    for match in ANSWER_SEQUENCE_PATTERN.finditer(text):
        answers[int(match.group(1))] = match.group(2).upper().replace("D", "Đ")
    for match in SHORT_ANSWER_PATTERN.finditer(text):
        answers.setdefault(int(match.group(1)), match.group(2).strip())
    return answers


def _parse_numbered_blocks(text: str) -> dict[int, str]:
    matches = list(QUESTION_PATTERN.finditer(text))
    blocks: dict[int, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        content = normalize_text(text[match.end() : end])
        if content:
            blocks[int(match.group(1))] = content
    return blocks


def _page_at_offset(offset: int, ranges: list[TextRange]) -> int | None:
    for item in ranges:
        if item.start <= offset <= item.end:
            return item.page_number
    previous = [item for item in ranges if item.start <= offset]
    return previous[-1].page_number if previous else None


def _extract_formula_records(text: str) -> list[dict[str, str | None]]:
    records: list[dict[str, str | None]] = []
    seen: set[str] = set()
    for formula in extract_formulas(text):
        normalized = normalize_formula(formula)
        if normalized and normalized not in seen:
            seen.add(normalized)
            records.append(
                {
                    "raw_text": formula,
                    "latex": formula,
                    "normalized": normalized,
                }
            )
    for match in UNICODE_MATH_PATTERN.finditer(text):
        raw = normalize_text(match.group(0))
        normalized = normalize_formula(raw)
        if raw and normalized and normalized not in seen:
            seen.add(normalized)
            records.append(
                {
                    "raw_text": raw,
                    "latex": None,
                    "normalized": normalized,
                }
            )
    return records[:100]


def _detect_topics(text: str) -> list[str]:
    normalized = text.lower()
    rules = [
        ("Hàm số", ("đạo hàm", "đồng biến", "nghịch biến", "cực trị", "tiệm cận")),
        ("Mũ và logarit", ("logarit", "lôgarit", "hàm số mũ", "phương trình mũ")),
        ("Nguyên hàm - Tích phân", ("nguyên hàm", "tích phân", "\\int", "∫")),
        ("Hình học không gian", ("oxyz", "mặt phẳng", "mặt cầu", "khối chóp", "thể tích")),
        ("Xác suất", ("xác suất", "biến cố", "chỉnh hợp", "tổ hợp")),
        ("Số phức", ("số phức", "môđun", "mặt phẳng phức")),
        ("Dãy số", ("cấp số cộng", "cấp số nhân", "dãy số")),
    ]
    return [
        topic for topic, keywords in rules if any(keyword in normalized for keyword in keywords)
    ]
