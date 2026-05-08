from pydantic import BaseModel

class PoseRequest(BaseModel):
    character_id: str
    pose: str
    prompt: str
    style: str