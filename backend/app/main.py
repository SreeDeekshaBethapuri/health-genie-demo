import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .schemas import ChatRequest, ChatResponse
from .flow import resolve_step, get_node
from .chatbot import handle_chat_message

app = FastAPI(title="Health Genie API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3005",
                   "http://127.0.0.1:3005",],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(body: ChatRequest):
    session_id = body.session_id or str(uuid.uuid4())

    # Free-text message → knowledge-base layer (guardrails + retriever)
    if body.message and body.message.strip():
        response = handle_chat_message(
            message=body.message,
            session_id=session_id,
            current_step=body.current_step,
            user_branch=body.user_branch,
        )
        if response is not None:
            return response

    # Option-button guided flow (unchanged)
    step = resolve_step(body.current_step, body.selected_option, body.user_branch)
    node = get_node(step)

    user_branch = body.user_branch
    if body.selected_option in ("new_user", "returning_user"):
        user_branch = body.selected_option

    return ChatResponse(
        session_id=session_id,
        step=step,
        message=node["message"],
        options=node["options"],
        cta=node["cta"],
        user_branch=user_branch,
    )
