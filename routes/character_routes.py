from fastapi import APIRouter, HTTPException
from schemas.character_schema import CharacterRequest
from schemas.pose_schema import PoseRequest
from schemas.video_schema import VideoRequest
from schemas.generate_image_schema import GenerateImageRequest
from tasks.video_tasks import generate_video_task
from tasks.character_tasks import generate_character_task
from tasks.character_tasks import generate_pose_task
from tasks.image_tasks import generate_image_task
from core.celery_app import celery_app

router = APIRouter(
    prefix="/pipeline",
    tags=["Character Pipeline"]
)

@router.post("/character")
async def generate_character(request: CharacterRequest):
    user_data = request.model_dump()
    role = request.role or "user"

    task = generate_character_task.delay(
        user_data,
        request.style,
        role
    )

    return {
        "status": "processing",
        "task_id": task.id,
        "message": "Character generation started"
    }

@router.post("/generate-pose")
async def generate_pose(request: PoseRequest):
    task = generate_pose_task.delay(
        request.character_id,
        request.pose,
        request.variation_index
    )

    return {
        "status": "processing",
        "task_id": task.id
    }

@router.post("/generate-video")
async def generate_video(request: VideoRequest):
    try:
        task = generate_video_task.delay(
            request.character_id,
            request.motion,
            request.motion_index
        )

        return {
            "status": "processing",
            "task_id": task.id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))   

@router.post("/generate-image")
async def generate_image(request: GenerateImageRequest):
    try:
        task = generate_image_task.delay(
            request.character_id,
            request.user_id,
            request.prompt
        )

        return {
            "status": "processing",
            "task_id": task.id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    task = celery_app.AsyncResult(task_id)

    response = {
        "task_id": task_id,
        "status": task.state.lower()
    }

    if task.state == "PENDING":
        response.update({
            "status": "pending",
            "message": "Task is waiting to be processed"
        })

    elif task.state == "STARTED":
        response.update({
            "status": "processing",
            "message": "Task is currently running"
        })

    elif task.state == "SUCCESS":
        result = task.result or {}

        if "error" in result:
            response.update({
                "status": "failed",
                "error": result["error"]
            })
            return response

    elif task.state == "FAILURE":
        response.update({
            "status": "failed",
            "error": str(task.result)
        })

    else:
        response.update({
            "status": task.state.lower(),
            "message": "Unknown task state"
        })

    return response