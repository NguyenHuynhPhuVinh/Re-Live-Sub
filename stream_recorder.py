"""
YouTube Livestream Recorder - Ghi stream thành các đoạn 5 phút
Yêu cầu: pip install yt-dlp
"""

import subprocess
import os
import time
import json
from datetime import datetime
from pathlib import Path


class YouTubeStreamRecorder:
    def __init__(self, output_dir="recordings", segment_duration=300):
        """
        Args:
            output_dir: Thư mục lưu video
            segment_duration: Độ dài mỗi segment (giây), mặc định 300s = 5 phút
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.segment_duration = segment_duration
        
    def get_stream_url(self, youtube_url):
        """Lấy direct stream URL từ YouTube"""
        try:
            cmd = [
                'yt-dlp',
                '-f', 'best',  # Chọn chất lượng tốt nhất
                '-g',  # Chỉ lấy URL, không download
                youtube_url
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            stream_url = result.stdout.strip()
            print(f"✓ Đã lấy stream URL")
            return stream_url
        except subprocess.CalledProcessError as e:
            print(f"✗ Lỗi khi lấy stream URL: {e.stderr}")
            return None
    
    def record_stream(self, youtube_url, stream_name=None):
        """
        Ghi stream thành các đoạn 5 phút
        
        Args:
            youtube_url: URL YouTube livestream
            stream_name: Tên để đặt cho các file (mặc định dùng timestamp)
        """
        if stream_name is None:
            stream_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print(f"🎥 Bắt đầu ghi stream: {youtube_url}")
        print(f"📁 Lưu vào: {self.output_dir}")
        print(f"⏱️  Mỗi segment: {self.segment_duration}s ({self.segment_duration//60} phút)")
        
        # Lấy stream URL
        stream_url = self.get_stream_url(youtube_url)
        if not stream_url:
            return
        
        # Pattern cho tên file: streamname_001.mp4, streamname_002.mp4, ...
        output_pattern = str(self.output_dir / f"{stream_name}_%03d.mp4")
        
        # FFmpeg command để ghi và chia segments
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', stream_url,
            '-c', 'copy',  # Copy codec, không re-encode (nhanh hơn)
            '-f', 'segment',  # Output format là segment
            '-segment_time', str(self.segment_duration),  # Độ dài mỗi segment
            '-segment_format', 'mp4',
            '-reset_timestamps', '1',  # Reset timestamp cho mỗi segment
            '-strftime', '1',  # Enable strftime trong tên file
            output_pattern
        ]
        
        print(f"\n🔴 Đang ghi stream...")
        print(f"Nhấn Ctrl+C để dừng\n")
        
        try:
            # Chạy ffmpeg
            process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Monitor output
            segment_count = 0
            for line in process.stderr:
                # FFmpeg output đi vào stderr
                if 'segment:' in line.lower() or 'Opening' in line:
                    segment_count += 1
                    print(f"✓ Đã tạo segment #{segment_count}")
                    
            process.wait()
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Đang dừng ghi hình...")
            process.terminate()
            process.wait()
            print("✓ Đã dừng")
        except Exception as e:
            print(f"\n✗ Lỗi: {e}")
        
        # Liệt kê các file đã tạo
        self.list_recordings(stream_name)
    
    def list_recordings(self, stream_name=None):
        """Liệt kê các file đã ghi"""
        pattern = f"{stream_name}_*.mp4" if stream_name else "*.mp4"
        files = sorted(self.output_dir.glob(pattern))
        
        if files:
            print(f"\n📹 Đã ghi {len(files)} segments:")
            for f in files:
                size_mb = f.stat().st_size / (1024 * 1024)
                print(f"  - {f.name} ({size_mb:.1f} MB)")
        else:
            print("\n📹 Chưa có file nào được ghi")
        
        return files


def main():
    # Ví dụ sử dụng
    recorder = YouTubeStreamRecorder(
        output_dir="recordings",
        segment_duration=300  # 5 phút
    )
    
    # Thay URL này bằng YouTube livestream của bạn
    youtube_url = "https://www.youtube.com/watch?v=VXciXPHJvYk"
    
    # Bắt đầu ghi
    recorder.record_stream(youtube_url, stream_name="test_stream")


if __name__ == "__main__":
    main()
