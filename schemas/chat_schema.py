from pydantic import BaseModel


class ChatRequest(BaseModel):
    userId: str
    characterId: str
    message: str