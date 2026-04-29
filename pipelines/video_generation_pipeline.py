from core.constants.pose_motion_map import POSE_MOTION_MAP
from services.pose_service import PoseService
from services.video_service import VideoService
from services.prompt_builder import build_pose_prompt, build_video_prompt
from providers.fal.fal_edit import edit_character
from providers.fal.fal_video import generate_character_video

def generate_video_pipeline(
    image_url: str,
    motion: str,
    motion_index: int
):
    # Step 0: Validate motion
    if motion not in POSE_MOTION_MAP:
        raise ValueError(f"Invalid motion: {motion}")

    # Step 1: Map motion → pose
    mapping = POSE_MOTION_MAP[motion]
    pose = mapping["pose"]
    pose_index = mapping["pose_index"]

    # Step 2: Get pose instruction
    pose_instruction = PoseService.get_pose_prompt(pose, pose_index)

    # Step 3: Build pose prompt
    pose_prompt = build_pose_prompt(pose_instruction)

    # Step 4: Generate edited image (Qwen Edit)
    edited_image_url = edit_character(
        image_url=image_url,
        prompt=pose_prompt
    )

    if not edited_image_url:
        raise Exception("Image editing failed")

    # Step 5: Get motion instruction
    motion_instruction = VideoService.get_video_prompt(motion, motion_index)

    # Step 6: Build video prompt
    video_prompt = build_video_prompt(motion_instruction)

    # Step 7: Generate video (Seedance)
    video_url = generate_character_video(
        image_url=edited_image_url,
        prompt=video_prompt
    )

    if not video_url:
        raise Exception("Video generation failed")

    return {
        "pose_used": pose,
        "edited_image": edited_image_url,
        "video": video_url
    }