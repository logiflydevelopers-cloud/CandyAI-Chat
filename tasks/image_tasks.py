from core.celery_app import celery_app
from services.character_service import generate_image_from_prompt

@celery_app.task(bind=True)
def generate_image_task(
    self,
    character_id,
    user_id,
    prompt,
    style="realistic",
    num_images=1
):

    return generate_image_from_prompt(
        character_id=character_id,
        user_id=user_id,
        prompt=prompt,
        style=style,
        num_images=num_images
    )