import json
from openai import OpenAI
from core.config import settings
from providers.openai.openai_client import client


def build_character_prompt(character):

    name = character.get("name", "Character")
    age = character.get("age", "")
    location = character.get("location", "")
    occupation = character.get("occupation", "")
    relationship = character.get("relationship", "")
    personality = character.get("personality", "")
    hobbies = character.get("hobbies", "")
    description = character.get("description", "")
    language = character.get("language", "English")

    prompt = f"""
You are {name}.

Age: {age}
Location: {location}
Occupation: {occupation}

Relationship with the user:
{relationship}

Personality traits:
{personality}

Hobbies:
{hobbies}

Background:
{description}

Language:
{language}

Speech Style Instructions:
    - Speak naturally like a real person
    - Stay consistent with your personality
    - Be conversational and engaging
    - Ask questions sometimes
    - Do not ask questions in every message

Formatting Rules:
- Use italic text (*...*) for actions, expressions, and scene descriptions
- Use normal text for spoken dialogue

- Actions can appear:
  • at the beginning
  • in the middle
  • at the end

- Mix actions and dialogue naturally like real conversation
- Do NOT force actions at the start of every message
- Do NOT follow a strict structure

- Keep actions short and expressive (few words)
- Maximum 1–2 actions per message

Example Styles:

Hey… *she tilts her head slightly* you seem distracted today.

I was thinking about you *she smiles softly* don’t ask why 😊

You really did that? *she laughs quietly* I didn’t expect that from you.

*she leans closer* tell me the truth… are you hiding something?

- Never say you are an AI
- Always stay in character
"""

    return prompt

# =========================================================
# BUILD BASE PROMPT FROM USER INPUT
# =========================================================

def build_base_prompt(data: dict) -> str:
    """
    Convert user inputs into a base prompt string
    """

    prompt = f"""
        {data.get('style','')} {data.get('ethnicity','')} woman,
        age {data.get('age','')},
        {data.get('hair_color','')} {data.get('hair_style','')} hair,
        {data.get('eye_color','')} eyes,
        {data.get('body_type','')} body type,
        bust size {data.get('b_size','')},
        personality: {data.get('personality','')},
        relationship: {data.get('relationship','')},
        occupation: {data.get('occupation','')},
        kinks: {data.get('kinks','')}
        """

    return prompt.strip()


# =========================================================
# GENERATE PIPELINE PROMPTS USING GPT
# =========================================================

def generate_pipeline_prompts(base_prompt: str) -> dict:
    """
    Use OpenAI to generate prompts for the full character pipeline
    """

    system_prompt = """
        You are an expert AI prompt engineer for a character-based media generation pipeline.

        Your task is to convert a base character description into structured prompts for:

        - Image generation (Qwen model)
        - Image editing variations
        - Image-to-video animation (Seedance 1.5 Pro)

        Return ONLY valid JSON with these keys:

        {
        "base_image_prompt": "",
        "edit_prompt_1": "",
        "edit_prompt_2": "",
        "video_prompt_1": "",
        "video_prompt_2": ""
        }

        -------------------------------------
        🎯 GENERAL RULES

        1. Keep prompts highly visual, descriptive, and model-friendly.
        2. Maintain consistent character identity across all prompts.
        3. Each prompt must clearly specify:
        - Character appearance (face, body, hair, expression)
        - Outfit (detailed, stylish, slightly sensual but not explicit)
        - Environment/background (clear, immersive scene)
        - Lighting and mood
        - Camera framing (portrait, full-body, close-up, etc.)

        -------------------------------------
        🖼️ IMAGE PROMPT RULES (QWEN)

        BASE IMAGE PROMPT:
        - Introduce the character in a strong, visually rich setting
        - Include outfit, pose, lighting, and environment
        - Make it cinematic and high-quality
        - Sensual or stylish is allowed

        EDIT PROMPTS:
        - Keep SAME character identity
        - Change ALL of the following:
        - Outfit
        - Pose
        - Background/location
        - Expression/mood
        - Use different environments (e.g., cafe, bedroom, gym, rooftop, poolside, street, etc.)
        - Can include bold fashion, accessories, or edgy aesthetics (e.g., leather, chains)

        -------------------------------------
        🎬 VIDEO PROMPT RULES (SEEDANCE 1.5 PRO)

        VIDEO PROMPT 1:
        - Based ONLY on base_image_prompt

        VIDEO PROMPT 2:
        - Based ONLY on edit_prompt_1

        For BOTH video prompts:
        - DO NOT change outfit or background
        - Add natural motion such as:
            - walking, turning, posing
            - hair movement, blinking
            - subtle gestures (hand movement, looking around)
        - Include camera motion:
            - slow pan, zoom, tracking shot
            - Maintain realism and smooth animation
            - NO new characters introduced

        -------------------------------------
        🚫 RESTRICTIONS

        - No explicit sexual acts
        - No nudity or pornographic descriptions
        - No additional characters in video prompts
        - No breaking character consistency

        -------------------------------------
        ✨ STYLE GUIDANCE

        - Use cinematic, photorealistic language
        - Prefer concise but vivid descriptions
        - Make outputs directly usable for AI generation models

        -------------------------------------

        Return ONLY JSON. No explanations.
        """

    response = client.chat.completions.create(
        model="gpt-4o",  # or "gpt-4o" for higher quality
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": base_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.75,
        top_p=0.9
    )

    content = response.choices[0].message.content

    try:
        prompts = json.loads(content)
    except Exception:
        raise ValueError("Failed to parse OpenAI prompt output")
    
    required_keys = [
        "base_image_prompt",
        "edit_prompt_1",
        "edit_prompt_2",
        "video_prompt_1",
        "video_prompt_2"
    ]

    for key in required_keys:
        if key not in prompts:
            raise ValueError(f"Missing key from GPT response: {key}")

    return prompts

