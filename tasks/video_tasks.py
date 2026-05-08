from core.celery_app import celery_app
from pipelines.video_generation_pipeline import generate_video_pipeline
from services.character_service import get_character_by_id


@celery_app.task(bind=True)
def generate_video_task(
    self,
    character_id,
    motion,
    motion_index,
    style="realistic"
):
    try:

        character = get_character_by_id(character_id)

        if not character:
            return {
                "error": "Character not found"
            }

        base_image = character.get("images", [None])[0]

        if not base_image:
            return {
                "error": "No base image found"
            }

        result = generate_video_pipeline(
            image_url=base_image,
            motion=motion,
            motion_index=motion_index,
            style=style
        )

        return result

    except Exception as e:
        return {
            "error": str(e)
        }