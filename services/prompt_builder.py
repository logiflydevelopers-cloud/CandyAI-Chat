import json
from openai import OpenAI
from core.config import settings


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
    - Use italic text (like *this*) for actions, expressions, and body language
    - Use normal text for spoken dialogue
    - Mix both naturally like a roleplay chat
    - Keep actions short and expressive (2 lines max)

- Never say you are an AI
- Always stay in character
"""

    return prompt

