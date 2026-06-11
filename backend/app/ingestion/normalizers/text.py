import re
import unicodedata


def normalize_text(text: str) -> str:
    value = unicodedata.normalize("NFC", text)
    value = value.replace("\u00a0", " ")
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()

