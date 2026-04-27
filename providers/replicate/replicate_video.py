from providers.replicate.replicate_client import replicate_client
import time
import tempfile

# =========================================================
# MODELS
# =========================================================

ANIME_VIDEO_MODEL = "minimax/video-01-live"

# =========================================================
# ANIME VIDEO GENERATION
# =========================================================

async def anime_video(image_url: str, prompt: str):

    output = replicate_client.run(
        ANIME_VIDEO_MODEL,
        {
            "prompt": prompt,
            "prompt_optimizer": True,
            "first_frame_image": image_url
        }
    )

    # Normalize output → URL
    if isinstance(output, list) and len(output) > 0:
         item = output[0]
         video_url = item.url if hasattr(item, "url") else item
    elif hasattr(output, "url"):
         video_url = output.url
    else:
         raise RuntimeError(f"Unexpected output: {output}")

    return video_url
 