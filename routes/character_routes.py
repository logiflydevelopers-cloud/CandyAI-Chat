from fastapi import APIRouter
from schemas.character_schema import CharacterRequest
from pipelines.character_pipeline import generate_character_pipeline

router = APIRouter(
    prefix="/pipeline",
    tags=["Character Pipeline"]
)


@router.post("/character")
async def generate_character(request: CharacterRequest):

    user_data = request.model_dump()

    result = await generate_character_pipeline(
        user_data=user_data,
        style=request.style
    )

    return result