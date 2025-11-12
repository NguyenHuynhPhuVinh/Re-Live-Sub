"""
Video Processing API Routes
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

from services.processing_service import ProcessingService

router = APIRouter()
processing_service = ProcessingService()

class ProcessRequest(BaseModel):
    video_path: str
    language: str = "vi"
    burn_subtitle: bool = True

@router.post("/generate-srt")
async def generate_srt(request: ProcessRequest, background_tasks: BackgroundTasks):
    """Tạo file SRT từ video"""
    try:
        task_id = await processing_service.generate_srt(
            video_path=request.video_path,
            language=request.language,
            background_tasks=background_tasks
        )
        return {"task_id": task_id, "status": "processing"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/merge-subtitle")
async def merge_subtitle(request: ProcessRequest, background_tasks: BackgroundTasks):
    """Gắn phụ đề vào video"""
    try:
        task_id = await processing_service.merge_subtitle(
            video_path=request.video_path,
            burn_in=request.burn_subtitle,
            background_tasks=background_tasks
        )
        return {"task_id": task_id, "status": "processing"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{task_id}")
async def get_processing_status(task_id: str):
    """Lấy trạng thái xử lý"""
    status = await processing_service.get_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    return status

@router.get("/list-processed")
async def list_processed():
    """Liệt kê video đã xử lý"""
    return await processing_service.list_processed_videos()
