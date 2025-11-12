"""
Stream Recording Service
"""
import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from stream_recorder import YouTubeStreamRecorder

class StreamService:
    def __init__(self):
        self.active_tasks: Dict[str, dict] = {}
        self.recordings_dir = Path("recordings")
        self.recordings_dir.mkdir(exist_ok=True)
    
    async def start_recording(self, url: str, segment_duration: int, enhance_quality: bool, background_tasks):
        """Bắt đầu ghi stream"""
        task_id = str(uuid.uuid4())
        stream_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.active_tasks[task_id] = {
            "status": "recording",
            "url": url,
            "stream_name": stream_name,
            "started_at": datetime.now().isoformat(),
            "segment_duration": segment_duration,
            "segments": []
        }
        
        # Run in background
        background_tasks.add_task(
            self._record_stream,
            task_id,
            url,
            stream_name,
            segment_duration,
            enhance_quality
        )
        
        return task_id
    
    async def _record_stream(self, task_id: str, url: str, stream_name: str, 
                            segment_duration: int, enhance_quality: bool):
        """Background task để ghi stream"""
        try:
            recorder = YouTubeStreamRecorder(
                output_dir="recordings",
                segment_duration=segment_duration,
                enhance_quality=enhance_quality,
                use_temp_dir=True
            )
            
            # Run in thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                recorder.record_stream,
                url,
                stream_name
            )
            
            self.active_tasks[task_id]["status"] = "completed"
        except Exception as e:
            self.active_tasks[task_id]["status"] = "error"
            self.active_tasks[task_id]["error"] = str(e)
    
    async def stop_recording(self, task_id: str):
        """Dừng ghi stream"""
        if task_id in self.active_tasks:
            self.active_tasks[task_id]["status"] = "stopped"
            # TODO: Implement actual stop mechanism
    
    async def get_status(self, task_id: str) -> Optional[dict]:
        """Lấy trạng thái task"""
        return self.active_tasks.get(task_id)
    
    async def list_recordings(self):
        """Liệt kê các video đã ghi"""
        videos = []
        for video_file in sorted(self.recordings_dir.glob("*.mp4")):
            videos.append({
                "name": video_file.name,
                "path": str(video_file),
                "size": video_file.stat().st_size,
                "created_at": datetime.fromtimestamp(video_file.stat().st_ctime).isoformat()
            })
        return videos
