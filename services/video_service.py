from core.constants.video_constants import VIDEOS

class VideoService:

    @staticmethod
    def get_video_prompt(video: str, index: int) -> str:
        if video not in VIDEOS:
            raise ValueError("Invalid pose")

        variations = VIDEOS[video]

        if index >= len(variations):
            raise ValueError("Invalid variation index")

        return variations[index]