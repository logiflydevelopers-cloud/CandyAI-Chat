import replicate
from core.config import settings

class ReplicateClient:
    """
    Central wrapper for Replicate API calls
    """

    def __init__(self):
        if not settings.REPLICATE_API_TOKEN:
            raise EnvironmentError("REPLICATE_API_TOKEN is not configured")

        self.client = replicate.Client(
            api_token=settings.REPLICATE_API_TOKEN
        )

    def run(self, model_id: str, input_data: dict):
        """
        Execute a Replicate model
        """

        try:
            output = self.client.run(
                model_id,
                input=input_data
            )

            return self._extract_url(output)

        except Exception as e:
            raise RuntimeError(f"Replicate request failed: {str(e)}")

    def _extract_url(self, output):
        """
        Normalize Replicate output → return URL
        """

        if isinstance(output, list) and len(output) > 0:
            item = output[0]
            return item.url if hasattr(item, "url") else item

        if hasattr(output, "url"):
            return output.url

        return output


# Singleton instance
replicate_client = ReplicateClient()