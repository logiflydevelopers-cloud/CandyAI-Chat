from database.mongo import characters_collection

def get_all_characters():
    return list(characters_collection.find())

def get_character_by_id(uniqueId):
    return characters_collection.find_one({"uniqueId": uniqueId})

def generate_pose_image(character, pose, variation_index):
    from services.pose_service import PoseService
    from services.prompt_builder import build_pose_prompt
    from providers.fal.fal_edit import edit_character

    base_image = character.get("images", [None])[0]

    if not base_image:
        raise ValueError("No base image found for character")

    pose_instruction = PoseService.get_pose_prompt(pose, variation_index)
    final_prompt = build_pose_prompt(pose_instruction)

    return edit_character(
        image_url=base_image,
        prompt=final_prompt
    )

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

