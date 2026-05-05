from providers.replicate.replicate_client import replicate_client

# =========================================================
# MODELS
# =========================================================

ANIME_GENERATION_MODEL = "aisha-ai-official/wai-nsfw-illustrious-v12:0fc0fa9885b284901a6f9c0b4d67701fd7647d157b88371427d63f8089ce140e"

# =========================================================
# ANIME CHARACTER GENERATION
# =========================================================

async def anime_generation(prompt: str):

    if not prompt:
        raise ValueError("Prompt is Required")
    
    output = replicate_client.run(
        ANIME_GENERATION_MODEL,
        {
            "vae": "default",
            "seed": -1,
            "model": "WAI-NSFW-Illustrious-SDXL-v12",
            "steps": 30,
            "width": 832,
            "height": 1232,
            "prompt": prompt,
            "cfg_scale": 7,
            "clip_skip": 2,
            "pag_scale": 0,
            "scheduler": "Euler a",
            "batch_size": 1,
            "negative_prompt": "blurry, low quality, extra limbs, extra fingers, distorted face, bad anatomy, watermark, text, logo, cropped, duplicate body parts",
            "guidance_rescale": 1,
            "prepend_preprompt": True
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

