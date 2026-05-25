import json
import re
from pathlib import Path
from typing import Optional

_INTENTS_PATH = Path(__file__).parent / "data" / "intents.json"

# Threshold: a score below this means no confident intent was detected.
# Calibration:
#   exact example match          → +6  (single strong signal)
#   substring example match      → +4  (partial containment)
#   exact keyword phrase match   → +3  (per keyword)
#   token-level keyword match    → +2  (all keyword tokens present)
#   token overlap with examples  → +1  (per shared meaningful token)
# A threshold of 3 means at minimum one keyword phrase or two token signals.
_CONFIDENCE_THRESHOLD = 3

# Words excluded from token-level comparisons.
# Kept to grammatical/functional words so domain terms remain meaningful.
_STOP_WORDS = {
    # Pronouns
    "i", "me", "my", "we", "us", "you", "your", "he", "she", "they", "it",
    # Articles / determiners
    "the", "a", "an",
    # Copula / auxiliaries
    "is", "are", "was", "were", "be", "been", "being",
    "am", "do", "does", "did",
    "have", "has", "had",
    "will", "would", "can", "could", "should", "may", "might", "shall",
    # Interrogatives
    "what", "how", "when", "where", "why", "which", "who",
    # Demonstratives
    "this", "that", "these", "those",
    # Conjunctions / prepositions
    "and", "or", "but", "not",
    "in", "on", "at", "to", "for", "of", "with", "about", "from", "by",
    "up", "out", "if", "so", "yet", "as",
    # Common fillers
    "just", "there", "here", "more", "some", "also", "please", "yes", "no",
    # Contraction fragments (split from apostrophe: "don't"→"don"+"t", "i'm"→"i"+"m")
    "ve", "re", "ll", "nt", "don",
}

# Phrases that confirm the user is asking about *their own* results, not
# asking for general information about the Digital Health Record feature.
_RESULTS_GATE_PATTERNS = [
    "my result",
    "my test result",
    "my lab result",
    "my health result",
    "my health data",
    "my dashboard",
    "previous result",
    "view result",
    "view my",
    "see my",
    "check my",
    "access my",
    "show my",
    "find my result",
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def normalize_text(text: str) -> str:
    """
    Return a cleaned, lowercased version of *text* suitable for comparison.

    Steps:
    - Replace curly/smart apostrophes with straight apostrophes.
    - Lowercase.
    - Remove all punctuation except apostrophes (preserves contractions).
    - Remove apostrophes that are not between two word characters.
    - Collapse repeated spaces and trim.
    """
    # Smart quotes → plain equivalents
    text = text.replace("‘", "'").replace("’", "'")
    text = text.replace("“", '"').replace("”", '"')
    text = text.lower()
    # Strip punctuation, keep alphanumerics, whitespace, and apostrophes
    text = re.sub(r"[^\w\s']", " ", text)
    # Remove apostrophes that are not part of a contraction (e.g. trailing ' )
    text = re.sub(r"(?<!\w)'|'(?!\w)", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def load_intents() -> list[dict]:
    """Load intents from intents.json. Returns [] if the file is missing or invalid."""
    try:
        with open(_INTENTS_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []


def score_intent(message: str, intent: dict) -> int:
    """
    Return a numeric score for how well *message* matches *intent*.

    Scoring layers (highest to lowest weight):
    1. Exact example match           +6  — normalized message equals a known example
    2. Substring example match       +4  — one contains the other (min length 5)
    3. Exact keyword phrase match    +3  — keyword phrase appears verbatim in message
    4. Token-level keyword match     +2  — all meaningful tokens of a keyword phrase
                                          are present in the message
    5. Token overlap with examples   +1  — per shared meaningful token
    """
    norm_msg = normalize_text(message)
    score = 0

    examples = [normalize_text(e) for e in intent.get("examples", [])]
    keywords = [normalize_text(k) for k in intent.get("keywords", [])]

    # --- Layer 1 & 2: example matching ---
    if norm_msg in examples:
        score += 6
    else:
        for ex in examples:
            if len(ex) >= 5 and (ex in norm_msg or norm_msg in ex):
                score += 4
                break  # count only the first substring match

    # --- Layers 3 & 4: keyword matching ---
    msg_tokens = _tokenize(norm_msg)

    for kw in keywords:
        if not kw:
            continue
        # Layer 3: exact phrase present in the message
        if kw in norm_msg:
            score += 3
        # Layer 4: all meaningful tokens of the keyword are in the message
        kw_tokens = _tokenize(kw)
        if kw_tokens and kw_tokens.issubset(msg_tokens):
            score += 2

    # --- Layer 5: token overlap with all example tokens combined ---
    example_tokens: set[str] = set()
    for ex in examples:
        example_tokens |= _tokenize(ex)
    score += len(msg_tokens & example_tokens)

    return score


def detect_intent(
    message: str,
    user_branch: Optional[str] = None,
) -> Optional[str]:
    """
    Return the ``route_to_step`` of the best-matching intent, or ``None`` if
    no intent reaches the confidence threshold.

    Special rules applied after scoring:
    - ``previous_results`` is only returned when the message contains a
      first-person result-access phrase (e.g. "my results", "view my …").
      Informational questions about the Digital Health Record feature fall
      through to the KB retriever.
    - Virtual-care routes are swapped when the inferred branch contradicts
      the user's known branch (new vs. returning).
    """
    if not message or not message.strip():
        return None

    norm_msg = normalize_text(message)
    intents = load_intents()
    if not intents:
        return None

    best_route: Optional[str] = None
    best_score = 0

    for intent in intents:
        s = score_intent(message, intent)
        if s > best_score:
            best_score = s
            best_route = intent.get("route_to_step")

    if best_score < _CONFIDENCE_THRESHOLD or best_route is None:
        return None

    # Guard: previous_results only for clearly personal result-access phrasing
    if best_route == "previous_results" and not _passes_results_gate(norm_msg):
        return None

    # Adjust virtual care route to match the known user branch
    if best_route == "virtual_care_new" and user_branch == "returning_user":
        return "virtual_care_returning"
    if best_route == "virtual_care_returning" and user_branch != "returning_user":
        return "virtual_care_new"

    return best_route


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> set[str]:
    """Split *text* into a set of meaningful lowercase tokens, removing stop words."""
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return {t for t in tokens if t not in _STOP_WORDS and len(t) > 1}


def _passes_results_gate(norm_msg: str) -> bool:
    """Return True only if the message is clearly asking to view personal data."""
    return any(pattern in norm_msg for pattern in _RESULTS_GATE_PATTERNS)
