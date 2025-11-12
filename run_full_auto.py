"""
Full Auto System - Chạy tự động toàn bộ hệ thống
Chỉ cần nhập URL stream, còn lại tự động hết
"""

import os
import sys
import subprocess
import time
import threading
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()


def check_requirements():
    """Kiểm tra các yêu cầu cần thiết"""
    print("🔍 Kiểm tra yêu cầu...")
    
    # Kiểm tra API key
    if not os.environ.get('GEMINI_API_KEY'):
        print("❌ Chưa đặt GEMINI_API_KEY trong file .env")
        print("\n💡 Tạo file .env và thêm:")
        print("   GEMINI_API_KEY=your_api_key_here")
        print("\n📝 Lấy API key tại: https://aistudio.google.com/apikey")
        sys.exit(1)
    
    # Kiểm tra FFmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except:
        print("❌ FFmpeg chưa được cài đặt")
        print("\n💡 Tải tại: https://ffmpeg.org/download.html")
        sys.exit(1)
    
    # Kiểm tra yt-dlp
    try:
        subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
    except:
        print("❌ yt-dlp chưa được cài đặt")
        print("\n💡 Chạy: pip install yt-dlp")
        sys.exit(1)
    
    print("✅ Tất cả yêu cầu đã đủ\n")


def run_pipeline():
    """Chạy auto processing pipeline"""
    from auto_process_pipeline import VideoProcessingPipeline
    
    pipeline = VideoProcessingPipeline(
        watch_dir="recordings",
        temp_dir="recordings/temp",
        processed_dir="processed",
        language='vi',
        burn_subtitle=True,
        stable_time=10
    )
    
    pipeline.start_watching()


def run_recorder(youtube_url, segment_duration=30):
    """Chạy stream recorder"""
    from stream_recorder import YouTubeStreamRecorder
    from datetime import datetime
    
    # Tạo tên stream từ timestamp
    stream_name = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    recorder = YouTubeStreamRecorder(
        output_dir="recordings",
        segment_duration=segment_duration,  # Có thể tùy chỉnh
        enhance_quality=False,  # Copy stream (nhanh)
        use_temp_dir=True  # Dùng temp dir
    )
    
    recorder.record_stream(youtube_url, stream_name=stream_name)


def main():
    print("=" * 70)
    print("🚀 FULL AUTO SYSTEM - HỆ THỐNG TỰ ĐỘNG HOÀN TOÀN")
    print("=" * 70)
    print()
    
    # Kiểm tra yêu cầu
    check_requirements()
    
    # Nhập URL
    print("📺 NHẬP THÔNG TIN STREAM")
    print("-" * 70)
    youtube_url = input("YouTube Stream URL: ").strip()
    
    if not youtube_url:
        print("❌ URL không được để trống!")
        sys.exit(1)
    
    # Tùy chọn segment duration
    segment_input = input("Segment duration (giây, mặc định 30 cho test): ").strip()
    segment_duration = int(segment_input) if segment_input else 30
    
    print()
    print("=" * 70)
    print("⚙️  CẤU HÌNH")
    print("=" * 70)
    print("📁 Thư mục temp:      recordings/temp")
    print("�  Thư mục output:    recordings")
    print("📁 Thư mục processed: processed")
    print(f"⏱️  Segment duration:  {segment_duration} giây ({segment_duration//60} phút {segment_duration%60} giây)")
    print("🌐 Ngôn ngữ phụ đề:   Tiếng Việt")
    print("🔥 Burn subtitle:     Có")
    print("⚡ Chế độ ghi:        Copy Stream (nhanh)")
    print("=" * 70)
    print()
    
    input("Nhấn Enter để bắt đầu...")
    print()
    
    # Khởi động pipeline trong thread riêng (KHÔNG dùng daemon)
    print("🚀 Đang khởi động Auto Processing Pipeline...")
    pipeline_thread = threading.Thread(target=run_pipeline, daemon=False)
    pipeline_thread.start()
    
    # Đợi pipeline khởi động
    time.sleep(3)
    print("✅ Pipeline đã sẵn sàng")
    print()
    
    # Chạy recorder trong thread riêng
    print("🎥 Đang khởi động Stream Recorder...")
    print("=" * 70)
    print()
    
    recorder_thread = threading.Thread(target=lambda: run_recorder(youtube_url, segment_duration), daemon=False)
    recorder_thread.start()
    
    # Đợi cả 2 threads
    try:
        print("💡 Hệ thống đang chạy. Nhấn Ctrl+C để dừng.\n")
        while recorder_thread.is_alive() or pipeline_thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Đang dừng hệ thống...")
        print("⚠️  Đợi các process hoàn thành...")
        print("💡 Nhấn Ctrl+C lần nữa để force quit")
        try:
            recorder_thread.join(timeout=5)
            pipeline_thread.join(timeout=5)
        except KeyboardInterrupt:
            print("\n⚠️  Force quit!")
        print("✅ Đã dừng")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
