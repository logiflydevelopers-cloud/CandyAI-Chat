from core.celery_app import celery_app
from pipelines.video_generation_pipeline import generate_video_pipeline
from services.character_service import get_character_by_id


@celery_app.task(bind=True)
def generate_video_task(self, character_id, motion, motion_index):
    try:
        character = get_character_by_id(character_id)

        if not character:
            return {"error": "Character not found"}

        result = generate_video_pipeline(
            image_url=character.base_image_url,
            motion=motion,
            motion_index=motion_index
        )

        return result

    except Exception as e:
        return {"error": str(e)}