from fastapi import APIRouter
from schemas.generate_image_schema import GenerateImageRequest
from services.character_service import generate_image_from_prompt

router = APIRouter()


@router.post("/generate-image")
def generate_image_api(request: GenerateImageRequest):
    result = generate_image_from_prompt(
        character_id=request.character_id,
        user_id=request.user_id,
        prompt=request.prompt
    )

    return result