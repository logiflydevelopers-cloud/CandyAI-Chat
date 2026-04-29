from core.constants.pose_constants import POSES

class PoseService:

    @staticmethod
    def get_pose_prompt(pose: str, index: int) -> str:
        if pose not in POSES:
            raise ValueError("Invalid pose")

        variations = POSES[pose]

        if index >= len(variations):
            raise ValueError("Invalid variation index")

        return variations[index]