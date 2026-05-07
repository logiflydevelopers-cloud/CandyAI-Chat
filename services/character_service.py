from database.mongo import characters_collection
from bson import ObjectId

def get_all_characters():
    return list(characters_collection.find())

def get_character_by_id(character_id):
    try:
        # Try searching by MongoDB _id
        character = characters_collection.find_one({
            "_id": ObjectId(character_id)
        })

        # Fallback: search by uniqueId
        if not character:
            character = characters_collection.find_one({
                "uniqueId": character_id
            })

        return character

    except Exception as e:
        print("GET CHARACTER ERROR:", e)
        return None

def generate_pose_image(character_id, pose, prompt):
    from services.prompt_builder import build_pose_prompt
    from providers.fal.fal_edit import edit_character
    from services.character_service import get_character_by_id

    # Fetch character
    character = get_character_by_id(character_id)

    # Validate character
    if character is None:
        return {
            "error": f"Character not found for ID: {character_id}"
        }

    # Get images safely
    images = character.get("images", [])

    if not images:
        return {
            "error": "No base image found for character"
        }

    base_image = images[0]

    # Build final prompt
    final_prompt = build_pose_prompt(prompt)

    # Generate image
    result = edit_character(
        image_url=base_image,
        prompt=final_prompt
    )

    # Validate result
    if not result:
        return {
            "error": "Image generation failed"
        }

    return {
        "image_url": result.get("image_url"),
        "pose": pose,
        "prompt": prompt
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

    # Use user prompt directly
    final_prompt = prompt

    # Generate image
    result = edit_character(
        image_url=base_image,
        prompt=final_prompt
    )

    generated_image_url = result.get("image_url")

    if not generated_image_url:
        return {"error": "Image generation failed"}

    # Return response
    return {
        "image_url": generated_image_url,
        "character_id": character_id,
        "user_id": user_id,
        "prompt": prompt
    }

