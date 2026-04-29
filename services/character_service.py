from database.mongo import characters_collection

def get_all_characters():
    return list(characters_collection.find())

def get_character_by_id(uniqueId):
    return characters_collection.find_one({"uniqueId": uniqueId})

def generate_pose_image(character, pose, variation_index):
    from services.pose_service import PoseService
    from services.prompt_builder import build_pose_prompt
    from providers.fal.fal_edit import edit_character

    base_image = character.base_image_url

    pose_instruction = PoseService.get_pose_prompt(pose, variation_index)

    final_prompt = build_pose_prompt(pose_instruction)

    return edit_character(
        image_url=base_image,
        prompt=final_prompt
    )

