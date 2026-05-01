from pydantic import BaseModel, Field
from typing import Optional


class CharacterRequest(BaseModel):
    style: str = Field(..., example="realistic, cinematic")
    ethnicity: str = Field(..., example="Indian")
    age: int = Field(..., ge=18, le=60)

    hair_color: str
    hair_style: str
    eye_color: str

    body_type: str
    b_size: Optional[str] = None 
    gender: Optional[str] = None
    hobbies: Optional[str] = None
    clothing: Optional[str] = None

    personality: str
    relationship: str
    occupation: str

    kinks: Optional[str] = None
    role: Optional[str] = None
    nudity: str