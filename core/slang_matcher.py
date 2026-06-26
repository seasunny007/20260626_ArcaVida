import json
import unicodedata
from dataclasses import dataclass
from pathlib import Path

DEFAULT_SLANG_PATH = Path(__file__).resolve().parents[1] / "config" / "slang.json"


@dataclass(frozen=True)
class SlangMatch:
    term: str
    meaning: str
    risk: str


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.lower())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def load_slang(path: Path = DEFAULT_SLANG_PATH) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def match_slang(
    text: str,
    slang: dict[str, dict[str, str]] | None = None,
) -> list[SlangMatch]:
    dictionary = slang or load_slang()
    normalized_text = normalize_text(text)
    matches: list[SlangMatch] = []

    for term, metadata in dictionary.items():
        if normalize_text(term) in normalized_text:
            matches.append(
                SlangMatch(
                    term=term,
                    meaning=metadata.get("meaning", ""),
                    risk=metadata.get("risk", "low"),
                )
            )

    return matches


def format_slang_hint(matches: list[SlangMatch]) -> str | None:
    if not matches:
        return None
    return "; ".join(f"{match.term}: {match.meaning} ({match.risk})" for match in matches)
