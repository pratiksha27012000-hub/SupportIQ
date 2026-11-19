
from fastapi import APIRouter
from pydantic import BaseModel

from backend.app.services.chat_service import process_guest_question

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

class ChatRequest(BaseModel):
    question: str
    conversation_id: str
    audience: str = "Guest"


@router.get("/test")
def test_chat():
    return {
        "message": "SupportIQ Chat API is working!",
        "status": "success"
    }


@router.post("/ask")
def ask_question(request: ChatRequest):
    return process_guest_question(
        question=request.question,
        conversation_id=request.conversation_id,
        audience=request.audience
    )
