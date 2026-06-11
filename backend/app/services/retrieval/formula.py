import re
import unicodedata

from app.services.retrieval.types import RankedResult, RetrievalDocument

LATEX_PATTERN = re.compile(
    r"\$\$(.+?)\$\$|\\\[(.+?)\\\]|\\\((.+?)\\\)|(?<!\\)\$(.+?)(?<!\\)\$",
    re.DOTALL,
)
COMMAND_PATTERN = re.compile(r"\\(?:frac|sqrt|sin|cos|tan|log|ln|int|sum|lim|vec|overline)\b")


def extract_formulas(text: str) -> list[str]:
    formulas: list[str] = []
    for match in LATEX_PATTERN.finditer(text):
        value = next((group for group in match.groups() if group is not None), "")
        if value.strip():
            formulas.append(value.strip())
    if not formulas and COMMAND_PATTERN.search(text):
        formulas.append(text.strip())
    return list(dict.fromkeys(formulas))


def normalize_formula(formula: str) -> str:
    value = unicodedata.normalize("NFKC", formula).lower()
    replacements = {
        "\\left": "",
        "\\right": "",
        "\\,": "",
        "\\!": "",
        "\\cdot": "*",
        "\\times": "*",
        "−": "-",
        "–": "-",
        " ": "",
    }
    for source, target in replacements.items():
        value = value.replace(source, target)
    value = re.sub(r"\\mathrm\{([^{}]+)\}", r"\1", value)
    value = re.sub(r"\s+", "", value)
    return value


def formula_tokens(formula: str) -> set[str]:
    normalized = normalize_formula(formula)
    return set(re.findall(r"\\[a-z]+|[a-z]+|\d+|[+\-*/=^_{}()[\]]", normalized))


class FormulaRetriever:
    def __init__(self, documents: list[RetrievalDocument]):
        self.documents = documents

    def search(self, query: str, limit: int = 20) -> list[RankedResult]:
        queries = extract_formulas(query)
        if not queries:
            return []
        query_tokens = set().union(*(formula_tokens(item) for item in queries))
        results: list[RankedResult] = []
        for document in self.documents:
            candidates = document.formulas or extract_formulas(document.content)
            document_tokens = (
                set().union(*(formula_tokens(item) for item in candidates))
                if candidates
                else set()
            )
            union = query_tokens | document_tokens
            score = len(query_tokens & document_tokens) / len(union) if union else 0
            if score:
                results.append(
                    RankedResult(
                        document=document,
                        score=score,
                        scores={"formula": score},
                    )
                )
        return sorted(results, key=lambda item: item.score, reverse=True)[:limit]
