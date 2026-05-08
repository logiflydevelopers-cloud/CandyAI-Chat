from database.mongo import (
    characters_collection,
    usercharacters_collection
)

from bson import ObjectId
from bson.errors import InvalidId


def get_all_characters():
    return list(characters_collection.find())


def get_character_by_id(character_id):
    try:
        character = None

        # -----------------------------------
        # Try MongoDB ObjectId search
        # -----------------------------------
        try:
            character = characters_collection.find_one({
                "_id": ObjectId(character_id)
            })

            # Search usercharacters_collection
            if not character:
                character = usercharacters_collection.find_one({
                    "_id": ObjectId(character_id)
                })

        except InvalidId:
            pass

        # -----------------------------------
        # Fallback: uniqueId search
        # -----------------------------------
        if not character:
            character = characters_collection.find_one({
                "uniqueId": character_id
            })

        if not character:
            character = usercharacters_collection.find_one({
                "uniqueId": character_id
            })

        return character

    except Exception as e:
        print("GET CHARACTER ERROR:", e)
        return None


def generate_pose_image(
    character_id,
    pose,
    prompt,
    style="realistic"
):
    from services.prompt_builder import build_pose_prompt
    from models.model_registry import get_model

    # =========================================
    # STYLE → MODEL MAP
    # =========================================
    STYLE_MODEL_MAP = {
        "realistic": "character_edit",
        "anime": "anime_edit"
    }

    # =========================================
    # FETCH CHARACTER
    # =========================================
    character = get_character_by_id(character_id)

    if character is None:
        return {
            "error": f"Character not found for ID: {character_id}"
        }

    # =========================================
    # GET BASE IMAGE
    # =========================================
    images = character.get("images", [])

    if not images:
        return {
            "error": "No base image found for character"
        }

    base_image = images[0]

    # =========================================
    # BUILD FINAL PROMPT
    # =========================================
    final_prompt = build_pose_prompt(
        prompt=prompt,
        pose=pose
    )

    # =========================================
    # GET MODEL NAME
    # =========================================
    model_name = STYLE_MODEL_MAP.get(style)

    if not model_name:
        return {
            "error": f"Invalid style: {style}"
        }

    # =========================================
    # GET MODEL HANDLER
    # =========================================
    try:
        model_handler = get_model(
            feature="image_edit",
            model=model_name
        )

    except Exception as e:
        return {
            "error": str(e)
        }

    # =========================================
    # GENERATE IMAGE
    # =========================================
    try:
        result = model_handler(
            image_url=base_image,
            prompt=final_prompt
        )

    except Exception as e:
        return {
            "error": f"Generation failed: {str(e)}"
        }

    # =========================================
    # VALIDATE RESULT
    # =========================================
    if not result:
        return {
            "error": "Image generation failed"
        }

    # =========================================
    # SUCCESS RESPONSE
    # =========================================
    return {
        "image_url": result,
        "style": style,
        "pose": pose
    }

def generate_image_from_prompt(character_id, user_id, prompt):
    from providers.fal.fal_edit import edit_character

    # Fetch character
    character = get_character_by_id(character_id)

    if not character:
        return {"error": "Character not found"}

    # Extract base image
    images = character.get("images", [])

    if not images:
        return {"error": "No base image found"}

    base_image = images[0]

    # Generate image
    result = edit_character(
        image_url=base_image,
        prompt=prompt
    )

    if not result:
        return {"error": "Image generation failed"}

    return {
        "image_url": result,
        "user_id": user_id,
    }