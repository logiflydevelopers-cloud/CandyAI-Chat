import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


class Settings:
    """
    Global configuration for AI Gateway
    """

    # =====================================================
    # APP SETTINGS
    # =====================================================

    APP_NAME: str = "AI Gateway"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))

    # =====================================================
    # SECURITY
    # =====================================================

    API_KEY: str = os.getenv("API_KEY", "")

    # =====================================================
    # FAL CONFIG
    # =====================================================

    FAL_KEY: str = os.getenv("FAL_KEY", "")

    # =====================================================
    # OPENAI CONFIG
    # =====================================================

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # =====================================================
    # REPLICATE CONFIG
    # =====================================================

    REPLICATE_API_TOKEN: str = os.getenv("REPLICATE_API_TOKEN", "")

#     # =====================================================
#     # REQUEST LIMITS
#     # =====================================================

#     MAX_VIDEO_DURATION: int = int(os.getenv("MAX_VIDEO_DURATION", 10))
#     MAX_IMAGE_SIZE: int = int(os.getenv("MAX_IMAGE_SIZE", 2048))

#     # =====================================================
#     # TIMEOUTS
#     # =====================================================

#     REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", 120))

#     # =====================================================
#     # LOGGING
#     # =====================================================

#     LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


# Singleton settings object
settings = Settings()