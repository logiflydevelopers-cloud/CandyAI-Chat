import asyncio

from services.prompt_builder import (
    build_base_prompt,
    generate_pipeline_prompts
)

from models.model_registry import get_model


# =========================================================
# CHARACTER PIPELINE
# =========================================================

async def generate_character_pipeline(user_data: dict, style: str):

    """
    Full character generation pipeline

    Outputs:
    - base image
    - 2 edited images
    - 2 videos
    """

    # -----------------------------------------------------
    # BUILD BASE PROMPT
    # -----------------------------------------------------

    base_prompt = build_base_prompt(user_data)

    # -----------------------------------------------------
    # GENERATE PIPELINE PROMPTS USING GPT
    # -----------------------------------------------------

    prompts = generate_pipeline_prompts(base_prompt)

    base_image_prompt = prompts["base_image_prompt"]
    edit_prompt_1 = prompts["edit_prompt_1"]
    edit_prompt_2 = prompts["edit_prompt_2"]
    video_prompt_1 = prompts["video_prompt_1"]
    video_prompt_2 = prompts["video_prompt_2"]
    # print(base_image_prompt)
    # print(edit_prompt_1)
    # print(edit_prompt_2)
    # print(video_prompt_1)
    # print(video_prompt_2)

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
    # GET HANDLERS FROM REGISTRY
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
    # GENERATE EDITED IMAGES
    # -----------------------------------------------------

    edit_tasks = [
        asyncio.to_thread(
            edit_handler,
            base_image,
            edit_prompt_1
        ),
        asyncio.to_thread(
            edit_handler,
            base_image,
            edit_prompt_2
        )
    ]

    edited_images = await asyncio.gather(*edit_tasks)

    # -----------------------------------------------------
    # GENERATE VIDEOS
    # -----------------------------------------------------

    video_tasks = [
        asyncio.to_thread(
            video_handler,
            edited_images[0],
            video_prompt_1
        ),
        asyncio.to_thread(
            video_handler,
            edited_images[1],
            video_prompt_2
        )
    ]

    videos = await asyncio.gather(*video_tasks)

    # -----------------------------------------------------
    # RETURN FINAL OUTPUT
    # -----------------------------------------------------

    return {
        "base_image": base_image,
        "edited_images": edited_images,
        "videos": videos
    }