from posthog import Posthog
import os

posthog = Posthog(
    project_api_key=os.getenv("POSTHOG_API_KEY"),
    host=os.getenv("POSTHOG_HOST")
)

def capture_event(user_id, event, properties=None):
    try:
        user_id = str(user_id)

        posthog.capture(
            distinct_id=user_id,
            event=event,
            properties={
                **(properties or {}),
                
                "$set": {
                    "user_id": user_id
                }
            }
        )

    except Exception as e:
        print("PostHog Error:", e)