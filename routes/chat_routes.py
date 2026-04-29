from fastapi import APIRouter
from schemas.chat_schema import ChatRequest
from services.chat_service import process_chat

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/message")
def chat_with_character(request: ChatRequest):

    reply = process_chat(
        user_id=request.userId,
        character_id=request.characterId,
        user_message=request.question,
        message_doc_id=request.messageDocId
    )

    return {
        "reply": reply
    }