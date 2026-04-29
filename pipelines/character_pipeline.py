import asyncio

from services.prompt_builder import (
    build_base_prompt,
    generate_pipeline_prompts
)

from models.model_registry import get_model

# =========================================================
# CHARACTER PIPELINE
# =========================================================

async def generate_character_pipeline(
    user_data: dict,
    style: str,
    role: str = "user"
):
    """
    Character generation pipeline

    USER:
    - base image
    - 1 edited image

    ADMIN:
    - base image
    - 2 edited images
    - 2 videos
    """

    # -----------------------------------------------------
    # BUILD BASE PROMPT
    # -----------------------------------------------------

    base_prompt = build_base_prompt(user_data)

    # -----------------------------------------------------
    # GENERATE PROMPTS (ROLE-BASED)
    # -----------------------------------------------------

    prompts = generate_pipeline_prompts(base_prompt, role)

    base_image_prompt = prompts.get("base_image_prompt")
    edit_prompt_1 = prompts.get("edit_prompt_1")
    edit_prompt_2 = prompts.get("edit_prompt_2")

    video_prompt_1 = prompts.get("video_prompt_1")
    video_prompt_2 = prompts.get("video_prompt_2")

    # -----------------------------------------------------
    # SELECT MODEL BASED ON STYLE
    # -----------------------------------------------------

    if style == "anime":
        base_model = "anime_character"
        edit_model = "anime_edit"
        video_model = "anime_video"
    else:
        base_model = "realistic_character"
        edit_model = "character_edit"
        video_model = "character_video"

    # -----------------------------------------------------
    # GET HANDLERS
    # -----------------------------------------------------

    image_handler = get_model("image_generation", base_model)
    edit_handler = get_model("image_edit", edit_model)
    video_handler = get_model("image_to_video", video_model)

    # -----------------------------------------------------
    # GENERATE BASE IMAGE
    # -----------------------------------------------------

    base_image = await asyncio.to_thread(
        image_handler,
        base_image_prompt
    )

    # -----------------------------------------------------
    # USER FLOW (LIGHTWEIGHT)
    # -----------------------------------------------------

    if role == "user":

        edited_image = await asyncio.to_thread(
            edit_handler,
            base_image,
            edit_prompt_1
        )

        return {
            "base_image": base_image,
            "edited_images": [edited_image]
        }

    # -----------------------------------------------------
    # ADMIN FLOW (FULL PIPELINE)
    # -----------------------------------------------------

    # ---- EDITS ----
    edit_tasks = [
        asyncio.to_thread(edit_handler, base_image, edit_prompt_1),
        asyncio.to_thread(edit_handler, base_image, edit_prompt_2)
    ]

    edited_images = await asyncio.gather(*edit_tasks)

    # ---- VIDEOS ----
    video_tasks = [
        asyncio.to_thread(video_handler, edited_images[0], video_prompt_1),
        asyncio.to_thread(video_handler, edited_images[1], video_prompt_2)
    ]

    videos = await asyncio.gather(*video_tasks)

    # -----------------------------------------------------
    # RETURN
    # -----------------------------------------------------

    return {
        "base_image": base_image,
        "edited_images": edited_images,
        "videos": videos
    }

