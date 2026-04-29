from posthog import Posthog
import os

posthog = Posthog(
    project_api_key=os.getenv("POSTHOG_API_KEY"),
    host=os.getenv("POSTHOG_HOST")
)

def capture_event(user_id, event, properties=None):
    try:
        posthog.capture(
            distinct_id=str(user_id),
            event=event,
            properties=properties or {}
        )
    except Exception as e:
        print("PostHog Error:", e)