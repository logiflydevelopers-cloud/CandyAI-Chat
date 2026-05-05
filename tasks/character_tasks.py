import asyncio
from celery import shared_task
from pipelines.character_pipeline import generate_character_pipeline
from services.character_service import generate_pose_image

@shared_task(bind=True)
def generate_character_task(self, user_data, style, role):
    try:
        # --------------------------------------------------
        # START TASK
        # --------------------------------------------------
        self.update_state(
            state="STARTED",
            meta={"step": "initializing"}
        )

        # --------------------------------------------------
        # RUN PIPELINE
        # --------------------------------------------------
        result = asyncio.run(
            generate_character_pipeline(
                user_data=user_data,
                style=style,
                role=role
            )
        )

        # --------------------------------------------------
        # VALIDATE RESULT
        # --------------------------------------------------
        if not isinstance(result, dict):
            raise ValueError("Invalid pipeline result format")

        # Optional sanity checks
        if "base_image" not in result:
            raise ValueError("Missing base_image in result")

        # --------------------------------------------------
        # COMPLETE
        # --------------------------------------------------
        return result

    except Exception as e:
        # --------------------------------------------------
        # FAILURE STATE (IMPORTANT)
        # --------------------------------------------------
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )

        return {
            "error": str(e),
            "type": e.__class__.__name__
        }

@shared_task(bind=True)
def generate_pose_task(self, character_id, pose, variation_index):
    try:
        result = asyncio.run(
            generate_pose_image(
            character_id=character_id,
            pose=pose,
            variation_index=variation_index
        ))
        return result
    except Exception as e:
        return {"error": str(e)}