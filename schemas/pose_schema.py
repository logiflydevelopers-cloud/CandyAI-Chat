from pydantic import BaseModel

class PoseRequest(BaseModel):
    character_id: str
    pose: str
    variation_index: int