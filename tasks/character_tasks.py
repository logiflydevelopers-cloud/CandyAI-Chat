from core.celery_app import celery_app
from pipelines.character_pipeline import generate_character_pipeline
from services.character_service import generate_pose_image

@celery_app.task(bind=True)
def generate_character_task(self, user_data, style, role):
    try:
        result = generate_character_pipeline(
            user_data=user_data,
            style=style,
            role=role
        )
        return result
    except Exception as e:
        return {"error": str(e)}

@celery_app.task(bind=True)
def generate_pose_task(self, character_id, pose, variation_index):
    try:
        result = generate_pose_image(
            character_id=character_id,
            pose=pose,
            variation_index=variation_index
        )
        return result
    except Exception as e:
        return {"error": str(e)}