import json
import re
from pathlib import Path
from typing import Optional

_KB_PATH = Path(__file__).parent.parent / "data" / "knowledge_base.json"

_STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "do", "does",
    "what", "how", "when", "where", "why", "which", "can", "will",
    "i", "my", "me", "in", "on", "to", "for", "of", "and", "or",
    "not", "it", "this", "that", "be", "have", "has", "had", "about",
    "please", "help", "need", "get", "tell", "show", "give", "want",
    "like", "looking", "find", "know", "see", "here", "there",
}

_CONFIDENCE_THRESHOLD = 3


def _stem(word: str) -> str:
    if word.endswith("ing") and len(word) >= 6:
        return word[:-3]
    if word.endswith("ies") and len(word) >= 5:
        return word[:-3] + "y"
    if word.endswith("ed") and len(word) >= 5:
        return word[:-2]
    if word.endswith("es") and len(word) >= 5 and word[-3] not in "aeiou":
        return word[:-2]
    if word.endswith("s") and len(word) >= 4 and word[-2] != "s":
        return word[:-1]
    return word


def _tokenize(text: str) -> list[str]:
    raw = re.findall(r"[a-z0-9]+", text.lower())
    return [t for t in raw if t not in _STOP_WORDS and len(t) > 2]


def _load_kb() -> list[dict]:
    try:
        with open(_KB_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []


# Load once at import time; returns [] on any error so search degrades gracefully.
_KB: list[dict] = _load_kb()


def _score_entry(query_tokens: list[str], query_lower: str, entry: dict) -> int:
    combined_str = " ".join([
        entry.get("title", ""),
        entry.get("category", ""),
        " ".join(entry.get("keywords", [])),
        entry.get("content", ""),
    ]).lower()

    combined_tokens = {_stem(w) for w in _tokenize(combined_str)}
    stemmed_query = [_stem(t) for t in query_tokens]

    # +1 per query token that appears (stemmed) in the entry's token set
    score = sum(1 for t in stemmed_query if t in combined_tokens)

    # +1 bonus per keyword phrase found verbatim in the original query
    for kw in entry.get("keywords", []):
        if kw.lower() in query_lower:
            score += 1

    return score


def search(query: str) -> tuple[Optional[dict], int]:
    """Return (best_entry, score). Score < _CONFIDENCE_THRESHOLD means no confident match."""
    if not query.strip() or not _KB:
        return None, 0

    query_lower = query.lower()
    query_tokens = _tokenize(query)
    if not query_tokens:
        return None, 0

    best_entry: Optional[dict] = None
    best_score = 0

    for entry in _KB:
        score = _score_entry(query_tokens, query_lower, entry)
        if score > best_score:
            best_score = score
            best_entry = entry

    return best_entry, best_score


def is_confident(score: int) -> bool:
    return score >= _CONFIDENCE_THRESHOLD
