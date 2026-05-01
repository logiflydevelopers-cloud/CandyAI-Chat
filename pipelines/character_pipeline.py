import asyncio
import inspect

from services.prompt_builder import (
    build_base_prompt,
    generate_pipeline_prompts
)

from models.model_registry import get_model


# =========================================================
# UNIVERSAL HANDLER EXECUTOR
# =========================================================

async def run_handler(handler, *args):
    # Case 1: async function
    if inspect.iscoroutinefunction(handler):
        return await handler(*args)

    # Case 2: sync function → run in thread
    result = await asyncio.to_thread(handler, *args)

    # Case 3: sync function RETURNS coroutine (Replicate style)
    if inspect.iscoroutine(result):
        return await result

    return result


# =========================================================
# CHARACTER PIPELINE
# =========================================================

async def generate_character_pipeline(
    user_data: dict,
    style: str,
    role: str = "user"
):

    # -----------------------------------------------------
    # BUILD BASE PROMPT
    # -----------------------------------------------------

    base_prompt = build_base_prompt(user_data)
    print(base_prompt)

    # -----------------------------------------------------
    # GENERATE PROMPTS
    # -----------------------------------------------------

    prompts = generate_pipeline_prompts(base_prompt, role)
    print(prompts)

    base_image_prompt = prompts.get("base_image_prompt")
    edit_prompt_1 = prompts.get("edit_prompt_1")
    edit_prompt_2 = prompts.get("edit_prompt_2")

    video_prompt_1 = prompts.get("video_prompt_1")
    video_prompt_2 = prompts.get("video_prompt_2")

    # -----------------------------------------------------
    # SELECT MODEL
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
    # BASE IMAGE
    # -----------------------------------------------------

    base_image = await run_handler(
        image_handler,
        base_image_prompt
    )

    # -----------------------------------------------------
    # USER FLOW
    # -----------------------------------------------------

    if role == "user":

        edited_image = await run_handler(
            edit_handler,
            base_image,
            edit_prompt_1
        )

        return {
            "base_image": str(base_image),
            "edited_images": [str(edited_image)]
        }

    # -----------------------------------------------------
    # ADMIN FLOW
    # -----------------------------------------------------

    # ---- EDITS ----
    edit_tasks = [
        run_handler(edit_handler, base_image, edit_prompt_1),
        run_handler(edit_handler, base_image, edit_prompt_2)
    ]

    edited_images = await asyncio.gather(*edit_tasks)

    # ---- VIDEOS ----
    video_tasks = [
        run_handler(video_handler, edited_images[0], video_prompt_1),
        run_handler(video_handler, edited_images[1], video_prompt_2)
    ]

    videos = await asyncio.gather(*video_tasks)

    # -----------------------------------------------------
    # RETURN 
    # -----------------------------------------------------

    return {
        "base_image": str(base_image),
        "edited_images": [str(img) for img in edited_images],
        "videos": [str(v) for v in videos]
    }