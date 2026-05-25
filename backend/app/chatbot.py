from typing import Optional

from .schemas import ChatResponse, Option
from .guardrails import check_emergency, check_medical
from .intent_router import detect_intent
from .retriever import search, is_confident
from .flow import FLOW, get_node

_DEFAULT_OPTIONS = [
    Option(label="Start health journey", value="new_user"),
    Option(label="Register Kit", value="register_kit"),
    Option(label="Contact Support", value="contact_support"),
]

_UNKNOWN_RESPONSE = (
    "I don't have that information in the Health Vibe knowledge base yet. "
    "I can help with test packages, biomarkers, Digital Health Record, virtual care, "
    "registering a kit, starting your health journey, or contacting support."
)


def handle_chat_message(
    message: str,
    session_id: str,
    current_step: Optional[str],
    user_branch: Optional[str],
) -> Optional[ChatResponse]:
    """
    Handle a free-text user message.

    Pipeline:
      1. Empty check              — return None so caller falls through to guided flow
      2. Emergency guardrail      — crisis language → immediate safe refusal
      3. Intent router            — phrasing maps to a guided-flow step
      4. Non-emergency medical    — diagnosis/treatment language → tiered safe refusal
      5. KB retrieval             — grounded answer from knowledge_base.json
      6. Unknown fallback         — helpful prompt with default navigation options
    """
    if not message or not message.strip():
        return None

    # ── Step 1: Emergency guardrail ───────────────────────────────────────────
    emergency_result = check_emergency(message)
    if emergency_result:
        g_message, g_options = emergency_result
        return ChatResponse(
            session_id=session_id,
            step="kb_answer",
            message=g_message,
            options=g_options,
            cta=None,
            user_branch=user_branch,
        )

    # ── Step 2: Intent routing ────────────────────────────────────────────────
    # detect_intent returns a route_to_step from intents.json, or None.
    routed_step = detect_intent(message, user_branch)
    if routed_step and routed_step in FLOW:
        node = get_node(routed_step)

        # Update the branch whenever the intent establishes which path the user is on
        new_branch = user_branch
        if routed_step == "new_user":
            new_branch = "new_user"
        elif routed_step == "returning_user":
            new_branch = "returning_user"

        return ChatResponse(
            session_id=session_id,
            step=routed_step,
            message=node["message"],
            options=node["options"],
            cta=node["cta"],
            user_branch=new_branch,
        )

    # ── Step 3: Non-emergency medical guardrail ───────────────────────────────
    # Runs after intent routing so legitimate wellness intents (learn_health,
    # general_wellness, etc.) are handled by the guided flow first.
    medical_result = check_medical(message)
    if medical_result:
        g_message, g_options = medical_result
        return ChatResponse(
            session_id=session_id,
            step="kb_answer",
            message=g_message,
            options=g_options,
            cta=None,
            user_branch=user_branch,
        )

    # ── Step 4: KB retrieval ──────────────────────────────────────────────────
    entry, score = search(message)
    if is_confident(score) and entry is not None:
        return ChatResponse(
            session_id=session_id,
            step="kb_answer",
            message=entry["content"],
            options=_DEFAULT_OPTIONS,
            cta=None,
            user_branch=user_branch,
        )

    # ── Step 5: Unknown fallback ──────────────────────────────────────────────
    return ChatResponse(
        session_id=session_id,
        step="kb_answer",
        message=_UNKNOWN_RESPONSE,
        options=_DEFAULT_OPTIONS,
        cta=None,
        user_branch=user_branch,
    )
