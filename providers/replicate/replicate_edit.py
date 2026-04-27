from providers.replicate.replicate_client import replicate_client

# =========================================================
# MODELS
# =========================================================

ANIME_EDIT_MODEL = "lucataco/omnigen2:5b9ea1d0821a60be9c861ebfc3513d121ecd8cab1932d3aa8d703e517988502e"

# =========================================================
# ANIME CHARACTER EDIT
# =========================================================

async def edit_anime(image_url: str, prompt: str):

    output = replicate_client.run(
        ANIME_EDIT_MODEL,
        {
            "cfg_range_end": 1,
            "cfg_range_start": 0,
            "height": 1024,
            "image": image_url,
            "image_guidance_scale": 2,
            "max_input_image_side_length": 2048,
            "max_pixels": 1048576,
            "negative_prompt": "(((deformed))), blurry, over saturation, bad anatomy, disfigured, poorly drawn face, mutation, mutated, (extra_limb), (ugly), (poorly drawn hands), fused fingers, messy drawing, broken legs censor, censored, censor_bar",
            "num_inference_steps": 50,
            "prompt": prompt,
            "scheduler": "euler",
            "seed": -1,
            "text_guidance_scale": 5,
            "width": 832
            }
    )

    # Handle FileOutput correctly
    if isinstance(output, list):
        first = output[0]
        return first.url if hasattr(first, "url") else first

    # Single FileOutput
    if hasattr(output, "url"):
        return output.url

    return output