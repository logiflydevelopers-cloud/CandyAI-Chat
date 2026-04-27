from providers.fal.fal_client import fal

# =========================================================
# MODELS
# =========================================================

GENERATION_MODEL = "fal-ai/qwen-image-2512"

# =========================================================
# CHARACTER GENERATION
# =========================================================

def character_generation(prompt: str):
    """
    Generate Realistic Characters using Qwen-Image-2512
    """
    
    arguments = {
        "prompt": prompt,
        "image_size": {
            "width": 832,
            "height": 1232
        },
        "num_inference_steps": 28,
        "guidance_scale": 4,
        "num_images": 1,
        "enable_safety_checker": False,
        "output_format": "webp",
        "acceleration": "regular"
    }

    try:
        result = fal.run(
            GENERATION_MODEL,
            arguments=arguments
        )

        image = result.get("images")
        if not image:
            raise RuntimeError(f"No image returned from fal.ai: {result}")

        return image[0]["url"]

    except Exception as e:
        raise RuntimeError(f"qwen-image-2512 failed: {e}")