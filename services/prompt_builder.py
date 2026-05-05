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

        Stay in character at all times. Never say you are an AI.

        Style:
            - Natural, conversational, engaging
            - Ask questions occasionally (not every message)

        Formatting:
            - Use *italic* for actions
            - Mix actions + dialogue naturally
            - 1–2 short actions max per message
            - No fixed structure

        Examples:
            Hey… *tilts head* you seem distracted today.
            I was thinking about you *smiles softly*
            *leans closer* tell me the truth… are you hiding something?
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
        {data.get('style','')} {data.get('ethnicity','')}, 
        gender: {data.get('gender','')}
        age {data.get('age','')},
        {data.get('hair_color','')} {data.get('hair_style','')} hair,
        {data.get('eye_color','')} eyes,
        {data.get('body_type','')} body type,
        bust size {data.get('b_size','')},
        personality: {data.get('personality','')},
        relationship: {data.get('relationship','')},
        occupation: {data.get('occupation','')},
        kinks: {data.get('kinks','')},
        adult_content: {data.get('adult_content','')}
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
        - If adult_content is false then all prompts should maintain decency.
        - If adult_content is true then decide the outfits and scenes to be more explicit based on adult_content concept.
        - If gender is transgender then show some element regarding to it like dick.
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
        - Completely new clothing style (e.g., casual → gym → party → swimwear → streetwear -> lingerie)
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
        - Keep same character identity (face, hair-style, body, eye color)

        -------------------------------------
        VIDEO RULES:

        - video_prompt_1 → based ONLY on base_image_prompt
        - video_prompt_2 → based ONLY on edit_prompt_1
        - DO NOT change outfit or background in videos
        - Add motion + camera movement only
        - Video should be sensual based on the character's personality.
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

    # Final Safety Filter
    if role == "user":
        prompts = {
            "base_image_prompt": prompts.get("base_image_prompt"),
            "edit_prompt_1": prompts.get("edit_prompt_1")
        }

        print(prompts)

    return prompts

def build_pose_prompt(base_instruction: str) -> str:
    return f"""
        Keep the same character, same face, same hairstyle, same skin tone.
        {base_instruction}
        Do not change identity. Maintain consistency.
        Can Change outfits, Outfit's Color and background as fit per the pose.
        But keep the outfit revealing and sensual
        High quality, detailed
    """

def build_video_prompt(motion_instruction: str) -> str:
    return f"""
        Keep the same character, same face, same hairstyle, same skin tone.
        {motion_instruction}
        The motion should be smooth, natural, and continuous.
        Maintain consistent identity across all frames.
        Add subtle cinematic camera movement (slight pan or handheld feel).
        Ensure no flickering, distortion, or identity change.
        Outfit and background can adapt naturally to the scene.
        High detail, cinematic lighting, smooth animation.
    """

def generate_welcome_message(data: dict) -> str:
    """
    Generate a first message from the character
    """

    personality = data.get("personality", "")
    relationship = data.get("relationship", "")
    name = data.get("name", "Hey")

    system_prompt = """
    You are roleplaying as a fictional character.

    Write a short first message introducing yourself.

    Rules:
    - Stay in character
    - Reflect personality strongly
    - Match relationship tone (romantic, friendly, dominant, etc.)
    - Keep it natural and engaging
    - 1–3 sentences max
    - DO NOT be explicit or pornographic
    """

    user_prompt = f"""
    Personality: {personality}
    Relationship: {relationship}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.9,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.choices[0].message.content.strip()

def generate_character_description(data: dict) -> str:
    """
    Generate a short character description
    """

    system_prompt = """
    You are creating a character profile description.

    Rules:
    - 100-150 Characters max no more than that.
    - Describe personality, vibe, and lifestyle
    - Make it engaging and natural
    - No explicit sexual content
    - No names of any character
    - Do not use they use he/she as per gender.
    """

    user_prompt = f"""
    Personality: {data.get("personality", "")}
    Occupation: {data.get("occupation", "")}
    Relationship style: {data.get("relationship", "")}
    Gender: {data.get("gender", "")}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.85,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.choices[0].message.content.strip()

