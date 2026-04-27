from providers.fal.fal_client import fal

# =========================================================
# MODELS
# =========================================================

CHARACTER_VIDEO_MODEL = "fal-ai/bytedance/seedance/v1.5/pro/image-to-video"

# =========================================================
# CHARACTER IMAGE-TO-VIDEO
# =========================================================

def generate_character_video(image_url: str, prompt: str):
    
    arguments = {
    "prompt": prompt,
    "aspect_ratio": "9:16",
    "resolution": "720p",
    "duration": "5",
    "enable_safety_checker": False,
    "generate_audio": False,
    "image_url": image_url
    }
    
    try:
        result = fal.run(
            CHARACTER_VIDEO_MODEL,
            arguments=arguments
        )

        video = result.get("video")
        if not video:
            raise RuntimeError(f"No image returned from fal.ai: {result}")

        return video["url"]

    except Exception as e:
        raise RuntimeError(f"Seedance Model failed: {e}")