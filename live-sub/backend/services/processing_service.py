"""
Video Processing Service
"""
import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from generate_srt import GeminiSRTGenerator
from merge_subtitle import SubtitleMerger

class ProcessingService:
    def __init__(self):
        self.active_tasks: Dict[str, dict] = {}
        self.srt_generator = GeminiSRTGenerator()
        self.subtitle_merger = SubtitleMerger()
        self.processed_dir = Path("processed")
        self.processed_dir.mkdir(exist_ok=True)
    
    async def generate_srt(self, video_path: str, language: str, background_tasks):
        """Tạo file SRT"""
        task_id = str(uuid.uuid4())
        
        self.active_tasks[task_id] = {
            "status": "processing",
            "type": "generate_srt",
            "video_path": video_path,
            "started_at": datetime.now().isoformat()
        }
        
        background_tasks.add_task(
            self._generate_srt_task,
            task_id,
            video_path,
            language
        )
        
        return task_id
    
    async def _generate_srt_task(self, task_id: str, video_path: str, language: str):
        """Background task tạo SRT"""
        try:
            loop = asyncio.get_event_loop()
            srt_path = await loop.run_in_executor(
                None,
                self.srt_generator.generate_srt_from_video,
                video_path,
                None,
                language
            )
            
            self.active_tasks[task_id]["status"] = "completed"
            self.active_tasks[task_id]["srt_path"] = str(srt_path)
        except Exception as e:
            self.active_tasks[task_id]["status"] = "error"
            self.active_tasks[task_id]["error"] = str(e)
    
    async def merge_subtitle(self, video_path: str, burn_in: bool, background_tasks):
        """Gắn phụ đề vào video"""
        task_id = str(uuid.uuid4())
        
        self.active_tasks[task_id] = {
            "status": "processing",
            "type": "merge_subtitle",
            "video_path": video_path,
            "started_at": datetime.now().isoformat()
        }
        
        background_tasks.add_task(
            self._merge_subtitle_task,
            task_id,
            video_path,
            burn_in
        )
        
        return task_id
    
    async def _merge_subtitle_task(self, task_id: str, video_path: str, burn_in: bool):
        """Background task gắn subtitle"""
        try:
            loop = asyncio.get_event_loop()
            output_path = await loop.run_in_executor(
                None,
                self.subtitle_merger.merge_subtitle,
                video_path,
                None,
                burn_in
            )
            
            self.active_tasks[task_id]["status"] = "completed"
            self.active_tasks[task_id]["output_path"] = str(output_path)
        except Exception as e:
            self.active_tasks[task_id]["status"] = "error"
            self.active_tasks[task_id]["error"] = str(e)
    
    async def get_status(self, task_id: str) -> Optional[dict]:
        """Lấy trạng thái task"""
        return self.active_tasks.get(task_id)
    
    async def list_processed_videos(self):
        """Liệt kê video đã xử lý"""
        videos = []
        for video_file in sorted(self.processed_dir.glob("*.mp4")):
            videos.append({
                "name": video_file.name,
                "path": str(video_file),
                "size": video_file.stat().st_size,
                "created_at": datetime.fromtimestamp(video_file.stat().st_ctime).isoformat()
            })
        return videos
