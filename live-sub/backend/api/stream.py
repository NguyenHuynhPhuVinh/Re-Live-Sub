"""
Stream Recording API Routes
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import asyncio

from services.stream_service import StreamService

router = APIRouter()
stream_service = StreamService()

class StreamRequest(BaseModel):
    url: str
    segment_duration: int = 60
    enhance_quality: bool = False

class StreamResponse(BaseModel):
    task_id: str
    status: str
    message: str

@router.post("/start", response_model=StreamResponse)
async def start_recording(request: StreamRequest, background_tasks: BackgroundTasks):
    """Bắt đầu ghi stream"""
    try:
        task_id = await stream_service.start_recording(
            url=request.url,
            segment_duration=request.segment_duration,
            enhance_quality=request.enhance_quality,
            background_tasks=background_tasks
        )
        return StreamResponse(
            task_id=task_id,
            status="started",
            message="Stream recording started"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop/{task_id}")
async def stop_recording(task_id: str):
    """Dừng ghi stream"""
    try:
        await stream_service.stop_recording(task_id)
        return {"status": "stopped", "task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{task_id}")
async def get_status(task_id: str):
    """Lấy trạng thái ghi stream"""
    status = await stream_service.get_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    return status

@router.get("/list")
async def list_recordings():
    """Liệt kê các video đã ghi"""
    return await stream_service.list_recordings()
