from .schemas import Option, CTA

# Each node: message, options list, optional CTA
FLOW: dict[str, dict] = {
    "welcome": {
        "message": (
            "Hi, I'm Health Genie. I can help you get started, explore wellness options, "
            "and guide you through the Health Vibe experience."
        ),
        "options": [
            Option(label="I'm new and need help getting started", value="new_user"),
            Option(label="I'm returning and need assistance", value="returning_user"),
        ],
        "cta": None,
    },

    # ── New user ─────────────────────────────────────────────────────────────
    "new_user": {
        "message": "What would you like help with today?",
        "options": [
            Option(label="General wellness", value="general_wellness"),
            Option(label="Nutrition or supplement guidance", value="nutrition"),
            Option(label="Virtual care", value="virtual_care_new"),
            Option(label="I'm not sure where to start", value="not_sure"),
        ],
        "cta": None,
    },

    # General wellness sub-options
    "general_wellness": {
        "message": (
            "Great — let's help you understand your overall wellness. "
            "What best describes your goal today?"
        ),
        "options": [
            Option(label="Learn more about my health", value="learn_health"),
            Option(label="Build healthier habits", value="healthier_habits"),
            Option(label="Understand possible deficiencies", value="deficiencies"),
            Option(label="Just exploring", value="just_exploring"),
        ],
        "cta": None,
    },
    "learn_health": {
        "message": (
            "The wellness assessment is the best place to begin. "
            "It helps create a more personalized experience based on your goals."
        ),
        "options": [],
        "cta": CTA(label="Start Wellness Assessment", url="/placeholder/wellness-assessment"),
    },
    "healthier_habits": {
        "message": (
            "The wellness assessment is the best place to begin. "
            "It helps create a more personalized experience based on your goals."
        ),
        "options": [],
        "cta": CTA(label="Start Wellness Assessment", url="/placeholder/wellness-assessment"),
    },
    "deficiencies": {
        "message": (
            "The wellness assessment is the best place to begin. "
            "It helps create a more personalized experience based on your goals."
        ),
        "options": [],
        "cta": CTA(label="Start Wellness Assessment", url="/placeholder/wellness-assessment"),
    },
    "just_exploring": {
        "message": (
            "The wellness assessment is the best place to begin. "
            "It helps create a more personalized experience based on your goals."
        ),
        "options": [],
        "cta": CTA(label="Start Wellness Assessment", url="/placeholder/wellness-assessment"),
    },

    # Nutrition sub-options
    "nutrition": {
        "message": (
            "I can help guide you toward nutrition and supplement recommendations. "
            "What would you like support with?"
        ),
        "options": [
            Option(label="Energy and focus", value="energy_focus"),
            Option(label="General wellness", value="nutrition_general"),
            Option(label="Fitness and recovery", value="fitness_recovery"),
            Option(label="Sleep and recovery", value="sleep_recovery"),
            Option(label="Not sure yet", value="nutrition_not_sure"),
        ],
        "cta": None,
    },
    "energy_focus": {
        "message": (
            "The wellness assessment can help personalize recommendations "
            "based on your goals and interests."
        ),
        "options": [],
        "cta": CTA(label="Continue to Assessment", url="/placeholder/wellness-assessment"),
    },
    "nutrition_general": {
        "message": (
            "The wellness assessment can help personalize recommendations "
            "based on your goals and interests."
        ),
        "options": [],
        "cta": CTA(label="Continue to Assessment", url="/placeholder/wellness-assessment"),
    },
    "fitness_recovery": {
        "message": (
            "The wellness assessment can help personalize recommendations "
            "based on your goals and interests."
        ),
        "options": [],
        "cta": CTA(label="Continue to Assessment", url="/placeholder/wellness-assessment"),
    },
    "sleep_recovery": {
        "message": (
            "The wellness assessment can help personalize recommendations "
            "based on your goals and interests."
        ),
        "options": [],
        "cta": CTA(label="Continue to Assessment", url="/placeholder/wellness-assessment"),
    },
    "nutrition_not_sure": {
        "message": (
            "The wellness assessment can help personalize recommendations "
            "based on your goals and interests."
        ),
        "options": [],
        "cta": CTA(label="Continue to Assessment", url="/placeholder/wellness-assessment"),
    },

    # Virtual care (new user path)
    "virtual_care_new": {
        "message": "Virtual care can connect you with a provider for more personalized guidance.",
        "options": [
            Option(label="Learn more about virtual care", value="learn_virtual_care"),
            Option(label="Speak with a provider", value="speak_provider"),
        ],
        "cta": None,
    },
    "learn_virtual_care": {
        "message": "You can continue to virtual care when you're ready.",
        "options": [],
        "cta": CTA(label="Explore Virtual Care", url="/placeholder/virtual-care"),
    },
    "speak_provider": {
        "message": "You can continue to virtual care when you're ready.",
        "options": [],
        "cta": CTA(label="Explore Virtual Care", url="/placeholder/virtual-care"),
    },

    # Not sure
    "not_sure": {
        "message": (
            "That's completely okay — most people are not sure where to begin. "
            "The wellness assessment is designed to help identify the best next steps "
            "based on your goals and interests."
        ),
        "options": [],
        "cta": CTA(label="Start Wellness Assessment", url="/placeholder/wellness-assessment"),
    },

    # ── Returning user ────────────────────────────────────────────────────────
    "returning_user": {
        "message": "Welcome back. What would you like help with today?",
        "options": [
            Option(label="View previous results", value="previous_results"),
            Option(label="Register my kit", value="register_kit"),
            Option(label="Virtual care", value="virtual_care_returning"),
            Option(label="Repurchase supplements", value="repurchase_supplements"),
            Option(label="Contact support", value="contact_support"),
        ],
        "cta": None,
    },
    "previous_results": {
        "message": "You can view your previous results from your account dashboard.",
        "options": [],
        "cta": CTA(label="View Results", url="/placeholder/results"),
    },
    "register_kit": {
        "message": "You can register your kit using the kit ID included with your package.",
        "options": [],
        "cta": CTA(label="Register Kit", url="/placeholder/register-kit"),
    },
    "virtual_care_returning": {
        "message": "Virtual care can help you review your questions with a provider.",
        "options": [],
        "cta": CTA(label="Explore Virtual Care", url="/placeholder/virtual-care"),
    },
    "repurchase_supplements": {
        "message": "You can revisit your supplement recommendations and reorder when needed.",
        "options": [],
        "cta": CTA(label="Repurchase Supplements", url="/placeholder/supplements"),
    },
    "contact_support": {
        "message": (
            "I can help route you to support for account, order, kit, or general questions."
        ),
        "options": [],
        "cta": CTA(label="Contact Support", url="/placeholder/support"),
    },

    # ── Continuation / end ───────────────────────────────────────────────────
    "continue_help_new_user": {
        "message": "What would you like help with today?",
        "options": [
            Option(label="General wellness", value="general_wellness"),
            Option(label="Nutrition or supplement guidance", value="nutrition"),
            Option(label="Virtual care", value="virtual_care_new"),
            Option(label="I'm not sure where to start", value="not_sure"),
        ],
        "cta": None,
    },
    "continue_help_returning_user": {
        "message": "What would you like help with today?",
        "options": [
            Option(label="View previous results", value="previous_results"),
            Option(label="Register my kit", value="register_kit"),
            Option(label="Virtual care", value="virtual_care_returning"),
            Option(label="Repurchase supplements", value="repurchase_supplements"),
            Option(label="Contact support", value="contact_support"),
        ],
        "cta": None,
    },
    "end_chat": {
        "message": "Have a great rest of your day!",
        "options": [],
        "cta": None,
    },

    # ── Fallback ──────────────────────────────────────────────────────────────
    "fallback": {
        "message": (
            "I can help with getting started, wellness assessment guidance, "
            "kit registration, virtual care, supplements, or support."
        ),
        "options": [
            Option(label="I'm new and need help getting started", value="new_user"),
            Option(label="I'm returning and need assistance", value="returning_user"),
        ],
        "cta": None,
    },
}


def resolve_step(
    current_step: str | None,
    selected_option: str | None,
    user_branch: str | None = None,
) -> str:
    """Return the next step key given the current step and the chosen option."""
    if current_step is None and selected_option is None:
        return "welcome"

    # Route continue_help to the branch-appropriate node
    if selected_option == "continue_help":
        if user_branch == "new_user":
            return "continue_help_new_user"
        if user_branch == "returning_user":
            return "continue_help_returning_user"
        return "fallback"

    # All other option values map directly to a step key
    if selected_option and selected_option in FLOW:
        return selected_option

    return "fallback"


def get_node(step: str) -> dict:
    return FLOW.get(step, FLOW["fallback"])
