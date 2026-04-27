import fal_client
from core.config import settings


class FalClient:
    """
    Central wrapper for FAL API calls
    """

    def __init__(self):
        if not settings.FAL_KEY:
            raise EnvironmentError("FAL_KEY is not configured")

        # Set API key
        fal_client.api_key = settings.FAL_KEY

    def run(self, model_id: str, arguments: dict):
        """
        Execute a FAL model
        """

        try:
            result = fal_client.subscribe(
                model_id,
                arguments=arguments
            )

            return result

        except Exception as e:
            raise RuntimeError(f"FAL request failed: {str(e)}")


# Singleton instance
fal = FalClient()