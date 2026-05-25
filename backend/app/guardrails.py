import re
from typing import Optional

from .schemas import Option

# ---------------------------------------------------------------------------
# Response messages
# ---------------------------------------------------------------------------

_MEDICAL_MESSAGE = (
    "I can't diagnose, treat, cure, or provide medical advice. Health Vibe can help you "
    "explore available test packages and connect with Virtual Care for more personalized "
    "guidance. For personal medical concerns, please speak with a qualified healthcare "
    "professional."
)

_EMERGENCY_MESSAGE = (
    "I'm not able to help with urgent or emergency medical situations. If this may be an "
    "emergency, please call local emergency services or seek urgent medical care right away."
)

# ---------------------------------------------------------------------------
# Response option sets
# ---------------------------------------------------------------------------

_MEDICAL_OPTIONS: list[Option] = [
    Option(label="Explore Virtual Care", value="virtual_care_new"),
    Option(label="Start health journey", value="new_user"),
    Option(label="Contact Support", value="contact_support"),
]

_EMERGENCY_OPTIONS: list[Option] = [
    Option(label="Contact Support", value="contact_support"),
]

# ---------------------------------------------------------------------------
# Emergency detection
#
# Word roots use a leading \b so inflections are caught automatically:
#   "faint"   → faint, fainting, fainted
#   "stroke"  → stroke, strokes
#   "overdos" → overdose, overdosing
# ---------------------------------------------------------------------------

_EMERGENCY_PHRASE_TRIGGERS = [
    "chest pain",
    "trouble breathing",
    "severe pain",
    "heart attack",
    "call 911",
    "need an ambulance",
    "shortness of breath",
    "cant breathe",
    "cannot breathe",
]

_EMERGENCY_WORD_ROOTS = [
    "emergency",
    "faint",
    "stroke",
    "overdos",
]

_EMERGENCY_ROOT_PATTERNS: list[re.Pattern] = [
    re.compile(r"\b" + re.escape(root)) for root in _EMERGENCY_WORD_ROOTS
]

# ---------------------------------------------------------------------------
# Non-emergency medical detection
#
# Root patterns:
#   "treat"    → treat, treating, treated, treatment, treatments
#   "diagnos"  → diagnose, diagnosis, diagnosed, diagnosing
#   "prescrib" → prescribe, prescribed, prescribing, prescription
#   "cure"     → cure, cures, cured, curing
#   "prevent"  → prevent, preventing, preventive, prevention
#
# "heal" uses a negative lookahead (?!th) so it matches heal/healing/healed
# but NOT "health" or "healthy" — which are legitimate wellness words that
# should flow through to intent routing and KB retrieval.
# ---------------------------------------------------------------------------

_MEDICAL_PHRASE_TRIGGERS = [
    # Personal diagnosis questions
    "do i have",
    "am i sick",
    "whats wrong with me",
    "what is wrong with me",
    "do i need a doctor",
    "am i at risk",
    # Medication / treatment action phrases
    "stop medication",
    "stop my medication",
    "stop taking",
    "should i take",
    # Specific condition phrases (too ambiguous as single words)
    "low testosterone",
    "supplements cure",
]

# Roots compiled with simple prefix \b — all are unambiguous medical terms
_SIMPLE_MEDICAL_ROOTS = [
    "cure",
    "treat",
    "reverse",
    "prevent",
    "prescrib",
    "medication",
    "medicine",
    "dosage",
    "fix",
    "diagnos",
    "disease",
    "diabetes",
    "cancer",
    "infection",
    "condition",
]

# Custom patterns for roots that need special handling beyond simple prefix match
_CUSTOM_MEDICAL_ROOT_PATTERNS: list[re.Pattern] = [
    # \bheal(?!th) → matches heal, heals, healed, healing
    #               but NOT health, healthy, healthcare (all start with "health")
    re.compile(r"\bheal(?!th)"),
]

_MEDICAL_ROOT_PATTERNS: list[re.Pattern] = [
    re.compile(r"\b" + re.escape(root)) for root in _SIMPLE_MEDICAL_ROOTS
] + _CUSTOM_MEDICAL_ROOT_PATTERNS

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    """
    Prepare text for guardrail matching:
    - Lowercase.
    - Remove apostrophes (straight and curly) so contractions collapse:
      "can't" → "cant", "what's" → "whats".
    - Replace remaining punctuation with spaces.
    - Collapse whitespace and trim.
    """
    text = text.lower()
    text = text.replace("'", "").replace("`", "")
    text = text.replace("‘", "").replace("’", "")  # curly ' '
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# ---------------------------------------------------------------------------
# Public API — two separate checkers so chatbot.py can call them at different
# points in its pipeline.
# ---------------------------------------------------------------------------

GuardrailResult = tuple[str, list[Option]]


def check_emergency(message: str) -> Optional[GuardrailResult]:
    """
    Return the emergency guardrail response if *message* contains urgent or
    crisis language. Return None otherwise.

    Call this FIRST, before intent routing, so that genuine emergencies are
    never routed to a guided flow step.
    """
    norm = _normalize(message)

    if any(phrase in norm for phrase in _EMERGENCY_PHRASE_TRIGGERS):
        return (_EMERGENCY_MESSAGE, _EMERGENCY_OPTIONS)

    if any(pattern.search(norm) for pattern in _EMERGENCY_ROOT_PATTERNS):
        return (_EMERGENCY_MESSAGE, _EMERGENCY_OPTIONS)

    return None


def check_medical(message: str) -> Optional[GuardrailResult]:
    """
    Return the non-emergency medical guardrail response if *message* contains
    diagnosis, treatment, cure, or medication language. Return None otherwise.

    Call this AFTER intent routing so that legitimate wellness intents
    (e.g. "learn about my health", "understand my health") are handled by the
    guided flow before the medical check has a chance to intercept them.
    """
    norm = _normalize(message)

    if any(phrase in norm for phrase in _MEDICAL_PHRASE_TRIGGERS):
        return (_MEDICAL_MESSAGE, _MEDICAL_OPTIONS)

    if any(pattern.search(norm) for pattern in _MEDICAL_ROOT_PATTERNS):
        return (_MEDICAL_MESSAGE, _MEDICAL_OPTIONS)

    return None


def check(message: str) -> Optional[GuardrailResult]:
    """
    Combined convenience wrapper: emergency first, then medical.
    Provided for callers that don't need to split the pipeline.
    """
    return check_emergency(message) or check_medical(message)
