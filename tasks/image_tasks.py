from core.celery_app import celery_app
from services.character_service import generate_image_from_prompt


@celery_app.task
def generate_image_task(character_id, user_id, prompt):
    return generate_image_from_prompt(
        character_id=character_id,
        user_id=user_id,
        prompt=prompt
    )