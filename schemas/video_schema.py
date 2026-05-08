from pydantic import BaseModel

class VideoRequest(BaseModel):
    character_id: str
    motion: str
    motion_index: int
    style: str
    

