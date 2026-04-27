# FAL Providers
from providers.fal.fal_video import (
    generate_character_video
)

from providers.fal.fal_image import character_generation
from providers.fal.fal_edit import edit_character
# Replicate Providers
from providers.replicate.replicate_video import (
    anime_video
)

from providers.replicate.replicate_image import anime_generation
from providers.replicate.replicate_edit import edit_anime


MODEL_REGISTRY = {

    # =========================================
    # IMAGE → VIDEO
    # =========================================
    "image_to_video": {
        "anime_video": {
            "handler": anime_video,
            "provider": "replicate",
            "credit_cost": 4
        },
        "character_video": {
            "handler": generate_character_video,
            "provider": "fal",
            "credit_cost": 7
        }
    },

    # =========================================
    # IMAGE GENERATION
    # =========================================
    "image_generation": {
        "realistic_character": {
            "handler": character_generation,
            "provider": "fal",
            "credit_cost": 3
        },
        "anime_character": {
            "handler": anime_generation,
            "provider": "replicate",
            "credit_cost": 3
        }
    },

    # =========================================
    # IMAGE EDIT
    # =========================================
    "image_edit": {
        "character_edit": {
            "handler": edit_character,
            "provider": "fal",
            "credit_cost": 2
        },
        "anime_edit": {
            "handler": edit_anime,
            "provider": "replicate",
            "credit_cost": 2
        }
    }
}


def get_model(feature: str, model: str):

    if feature not in MODEL_REGISTRY:
        raise ValueError(f"Invalid feature: {feature}")

    feature_models = MODEL_REGISTRY[feature]

    if model not in feature_models:
        raise ValueError(
            f"Invalid model '{model}' for feature '{feature}'"
        )

    return feature_models[model]["handler"]


def get_model_registry():

    clean_registry = {}

    for feature, models in MODEL_REGISTRY.items():
        clean_registry[feature] = {}

        for model_name, data in models.items():
            clean_registry[feature][model_name] = {
                "provider": data.get("provider"),
                "credit_cost": data.get("credit_cost")
            }

    return clean_registry