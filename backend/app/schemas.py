from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    current_step: Optional[str] = None
    selected_option: Optional[str] = None
    user_branch: Optional[str] = None
    message: Optional[str] = None


class Option(BaseModel):
    label: str
    value: str


class CTA(BaseModel):
    label: str
    url: str


class ChatResponse(BaseModel):
    session_id: str
    step: str
    message: str
    options: list[Option]
    cta: Optional[CTA] = None
    user_branch: Optional[str] = None
