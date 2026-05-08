from core.constants.pose_motion_map import POSE_MOTION_MAP

from services.pose_service import PoseService
from services.video_service import VideoService

from services.prompt_builder import (
    build_pose_prompt,
    build_video_prompt
)

from models.model_registry import get_model


def generate_video_pipeline(
    image_url: str,
    motion: str,
    motion_index: int,
    style: str = "realistic"
):

    # =========================================
    # STYLE MODEL MAPS
    # =========================================
    IMAGE_EDIT_MODELS = {
        "realistic": "character_edit",
        "anime": "anime_edit"
    }

    VIDEO_MODELS = {
        "realistic": "character_video",
        "anime": "anime_video"
    }

    # =========================================
    # VALIDATE MOTION
    # =========================================
    if motion not in POSE_MOTION_MAP:
        raise ValueError(f"Invalid motion: {motion}")

    # =========================================
    # GET MODELS
    # =========================================
    image_model_name = IMAGE_EDIT_MODELS.get(style)
    video_model_name = VIDEO_MODELS.get(style)

    if not image_model_name:
        raise ValueError(f"Invalid style: {style}")

    image_editor = get_model(
        feature="image_edit",
        model=image_model_name
    )

    video_generator = get_model(
        feature="image_to_video",
        model=video_model_name
    )

    # =========================================
    # MAP MOTION → POSE
    # =========================================
    mapping = POSE_MOTION_MAP[motion]

    pose = mapping["pose"]
    pose_index = mapping["pose_index"]

    # =========================================
    # GET POSE PROMPT
    # =========================================
    pose_instruction = PoseService.get_pose_prompt(
        pose,
        pose_index
    )

    # =========================================
    # BUILD POSE PROMPT
    # =========================================
    pose_prompt = build_pose_prompt(
        prompt=pose_instruction,
        pose=pose
    )

    # =========================================
    # GENERATE POSE IMAGE
    # =========================================
    edited_image_url = image_editor(
        image_url=image_url,
        prompt=pose_prompt
    )

    if not edited_image_url:
        raise Exception("Image editing failed")

    # =========================================
    # GET VIDEO PROMPT
    # =========================================
    motion_instruction = VideoService.get_video_prompt(
        motion,
        motion_index
    )

    # =========================================
    # BUILD VIDEO PROMPT
    # =========================================
    video_prompt = build_video_prompt(
        motion_instruction
    )

    # =========================================
    # GENERATE VIDEO
    # =========================================
    video_url = video_generator(
        image_url=edited_image_url,
        prompt=video_prompt
    )

    if not video_url:
        raise Exception("Video generation failed")

    # =========================================
    # SUCCESS
    # =========================================
    return {
        "video": video_url,
        "style": style,
        "motion": motion
    }