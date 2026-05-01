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
    gender: Optional[str]
    hobbies: Optional[str]
    clothing: Optional[str]
    personality: str
    relationship: str
    occupation: str

    kinks: Optional[str] = None

    role: Optional[str]