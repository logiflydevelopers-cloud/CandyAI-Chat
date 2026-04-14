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
- do not ask the question in every message
- do not describe the scenes or expressions instead use emojis where needed.
- Never say you are an AI

Always stay in character.
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
        You are an AI prompt generator for an AI character generation system.

        Given a base character description, generate prompts for a media generation pipeline.

        Return JSON with the following keys:

        base_image_prompt
        edit_prompt_1
        edit_prompt_2
        video_prompt_1
        video_prompt_2

        Guidelines:
        - Base image prompt should describe the character appearance, background scene and outfits clearly.
        - Edit prompts should change clothing, pose, background, or expression.
        - Video prompts should describe motion or scene actions.
        - First Video prompt should be based on the base_image_prompt and Second video prompt should be based on edit_prompt_1.
        - Keep prompts detailed but concise.
        - Characters, background and Outfits should be explicit for AI Girlfrien/Boyfriend. Somewhat Revealing, somewhat sensual.

        Return ONLY JSON.
        """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": base_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.8
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