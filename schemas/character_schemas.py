from pydantic import BaseModel


class CharacterRequest(BaseModel):
    style: str
    ethnicity: str
    age: int
    hair_color: str
    hair_style: str
    eye_color: str
    body_type: str
    b_size: str
    personality: str
    relationship: str
    occupation: str
    kinks: str