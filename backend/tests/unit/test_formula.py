from app.services.retrieval.formula import extract_formulas, normalize_formula


def test_normalize_formula_removes_visual_noise() -> None:
    assert normalize_formula(r"\left( x \right) \cdot 2") == "(x)*2"


def test_extract_formulas_from_inline_latex() -> None:
    assert extract_formulas(r"Tính $\int x^2 dx$ và $x+1$.") == [
        r"\int x^2 dx",
        "x+1",
    ]

