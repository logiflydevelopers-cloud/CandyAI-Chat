from pydantic import BaseModel


class GenerateImageRequest(BaseModel):
    character_id: str
    prompt: str
    user_id: str
    style: str
    num_images: int