from providers.fal.fal_client import fal

# =========================================================
# MODELS
# =========================================================

EDIT_MODEL = "fal-ai/qwen-image-2/pro/edit"

# =========================================================
# CHARACTER EDIT
# =========================================================

def edit_character(image_url: list[str], prompt: str):
    """
    Edit Characters Using Qwen-Image-2 Edit model
    """
    
    arguments = {
        "prompt": prompt,
        "negative_prompt": "low resolution, error, worst quality, low quality, deformed",
        "enable_prompt_expansion": True,
        "enable_safety_checker": False,
        "num_images": 1,
        "output_format": "webp",
        "image_urls": [image_url],
        "image_size": {
            "width": 832,
            "height": 1232
        }
    }
    
    try:
        result = fal.run(
            EDIT_MODEL,
            arguments=arguments
        )

        image = result.get("images")
        if not image:
            raise RuntimeError(f"No image returned from fal.ai: {result}")

        return image[0]["url"]

    except Exception as e:
        raise RuntimeError(f"qwen-image-Edit failed: {e}")
    