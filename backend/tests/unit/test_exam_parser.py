from app.ingestion.models import ParsedSection
from app.ingestion.parsers.exams import parse_exam_sections


def test_parse_multiple_choice_questions_answers_solutions_and_formulas() -> None:
    sections = [
        ParsedSection(
            heading="Trang 1",
            page_number=1,
            content=r"""
ĐỀ THI THỬ TỐT NGHIỆP THPT
Câu 1. Tính tích phân $\int_0^1 x^2\,dx$.
A. $\frac{1}{3}$ B. $\frac{1}{2}$ C. $1$ D. $2$
Câu 2. Hàm số nào sau đây đồng biến trên $\mathbb{R}$?
A. $y=x^3$ B. $y=-x$ C. $y=-x^2$ D. $y=\frac{1}{x}$
""",
        ),
        ParsedSection(
            heading="Trang 2",
            page_number=2,
            content=r"""
ĐÁP ÁN
1 A  2 A

LỜI GIẢI
Câu 1. Ta có $\int_0^1 x^2\,dx=\frac{1}{3}$.
Câu 2. Hàm số $y=x^3$ có đạo hàm không âm trên $\mathbb{R}$.
""",
        ),
    ]

    result = parse_exam_sections(sections)

    assert len(result.questions) == 2
    assert result.answer_count == 2
    assert result.solution_count == 2
    assert result.formula_count >= 2
    first = result.questions[0]
    assert first.question_number == 1
    assert first.question_type == "multiple_choice"
    assert [option["key"] for option in first.options] == ["A", "B", "C", "D"]
    assert first.correct_answer == "A"
    assert first.page_number == 1
    assert "Nguyên hàm - Tích phân" in first.topics
    assert first.formulas[0]["normalized"]


def test_parse_true_false_and_report_missing_answer() -> None:
    sections = [
        ParsedSection(
            heading="Trang 3",
            page_number=3,
            content="""
Câu 3. Xét tính đúng sai của các mệnh đề sau:
a) Hàm số liên tục trên R.
b) Hàm số có cực đại.
c) Đạo hàm luôn dương.
d) Đồ thị có tiệm cận đứng.
""",
        )
    ]

    result = parse_exam_sections(sections)

    assert len(result.questions) == 1
    question = result.questions[0]
    assert question.question_type == "true_false"
    assert len(question.options) == 4
    assert question.correct_answer is None
    assert any("chưa ghép được đáp án" in warning for warning in question.warnings)


def test_parser_returns_warning_when_question_markers_are_missing() -> None:
    result = parse_exam_sections(
        [
            ParsedSection(
                heading="Trang 1",
                page_number=1,
                content="Đây là tài liệu lý thuyết không chứa cấu trúc đề thi.",
            )
        ]
    )

    assert result.questions == []
    assert result.warnings


def test_parse_short_answer_from_answer_key() -> None:
    result = parse_exam_sections(
        [
            ParsedSection(
                heading="Trang 1",
                page_number=1,
                content="""
Câu 5: Tìm giá trị nhỏ nhất của biểu thức đã cho.

ĐÁP ÁN
Câu 5: 2,5
""",
            )
        ]
    )

    assert len(result.questions) == 1
    assert result.questions[0].question_type == "short_answer"
    assert result.questions[0].correct_answer == "2,5"
