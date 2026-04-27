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

    return " ".join(prompt.split())

def build_system_prompt(role: str) -> str:
    base = """
You are an expert AI prompt engineer for a character-based media generation pipeline.

Follow all cinematic, visual, and consistency rules.
Ensure STRICT valid JSON output. No extra text.

IMPORTANT:
- Maintain SAME character identity across all prompts.
- Each prompt must be visually rich, cinematic, and detailed.
"""

    if role == "admin":
        return base + """
Generate FULL pipeline:

{
"base_image_prompt": "",
"edit_prompt_1": "",
"edit_prompt_2": "",
"video_prompt_1": "",
"video_prompt_2": ""
}

-------------------------------------
EDIT PROMPT RULES (VERY IMPORTANT):

Each edit prompt MUST be COMPLETELY DIFFERENT from the base image and from each other.

You MUST change ALL of the following:

1. Outfit:
   - Completely new clothing style (e.g., casual → gym → party → swimwear → streetwear)
   - Different colors, textures, accessories

2. Background / Location:
   - Entirely different setting
   - Examples: cafe, bedroom, gym, rooftop, beach, poolside, street, nightclub

3. Pose:
   - Different body positioning (standing, sitting, lying, walking, leaning, etc.)

4. Expression / Mood:
   - Different emotional tone (smiling, serious, playful, seductive, confident, shy, etc.)

5. Camera framing:
   - Change angle or shot type (close-up, full body, side angle, over-shoulder, etc.)

STRICT RULES:
- NO repetition of outfit, pose, or background
- Each edit must feel like a completely new scene
- Keep same character identity (face, hair, body)

-------------------------------------
VIDEO RULES:

- video_prompt_1 → based ONLY on base_image_prompt
- video_prompt_2 → based ONLY on edit_prompt_1
- DO NOT change outfit or background in videos
- Add motion + camera movement only
"""

    else:
        return base + """
Generate LIMITED pipeline:

{
"base_image_prompt": "",
"edit_prompt_1": ""
}

-------------------------------------
EDIT PROMPT RULES:

edit_prompt_1 MUST be clearly DIFFERENT from base_image_prompt.

You MUST change:
- outfit
- background
- pose
- expression

Make it a completely new scene but same character.

DO NOT include any other keys.
"""


USER_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "user_pipeline",
        "schema": {
            "type": "object",
            "properties": {
                "base_image_prompt": {"type": "string"},
                "edit_prompt_1": {"type": "string"}
            },
            "required": ["base_image_prompt", "edit_prompt_1"],
            "additionalProperties": False
        }
    }
}

ADMIN_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "admin_pipeline",
        "schema": {
            "type": "object",
            "properties": {
                "base_image_prompt": {"type": "string"},
                "edit_prompt_1": {"type": "string"},
                "edit_prompt_2": {"type": "string"},
                "video_prompt_1": {"type": "string"},
                "video_prompt_2": {"type": "string"}
            },
            "required": [
                "base_image_prompt",
                "edit_prompt_1",
                "edit_prompt_2",
                "video_prompt_1",
                "video_prompt_2"
            ],
            "additionalProperties": False
        }
    }
}



# =========================================================
# GENERATE PIPELINE PROMPTS USING GPT
# =========================================================

def generate_pipeline_prompts(base_prompt: str, role: str = "user") -> dict:
    """
    Generate prompts based on role (user/admin)
    """

    system_prompt = build_system_prompt(role)
    schema = ADMIN_SCHEMA if role == "admin" else USER_SCHEMA

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": base_prompt}
        ],
        response_format=schema,
        temperature=0.75,
        top_p=0.9
    )

    content = response.choices[0].message.content

    try:
        prompts = json.loads(content)
    except Exception:
        raise ValueError("Failed to parse OpenAI prompt output")

    # 🔒 Final Safety Filter (IMPORTANT)
    if role == "user":
        prompts = {
            "base_image_prompt": prompts.get("base_image_prompt"),
            "edit_prompt_1": prompts.get("edit_prompt_1")
        }

        print(prompts)

    return prompts
