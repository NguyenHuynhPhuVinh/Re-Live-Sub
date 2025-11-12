"""
Auto System Starter - Khởi động cả Pipeline và Recorder
"""

import subprocess
import sys
import time
from pathlib import Path


def main():
    print("=" * 70)
    print("AUTO VIDEO PROCESSING SYSTEM")
    print("=" * 70)
    print()
    print("Script này sẽ khởi động 2 process:")
    print("1. Auto Processing Pipeline (tự động xử lý video)")
    print("2. Stream Recorder (ghi stream)")
    print()
    
    # Kiểm tra các file cần thiết
    required_files = [
        "auto_process_pipeline.py",
        "stream_recorder.py",
        ".env"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("⚠️  Thiếu các file sau:")
        for file in missing_files:
            print(f"  - {file}")
        print()
        if ".env" in missing_files:
            print("💡 Tạo file .env và thêm GEMINI_API_KEY")
        sys.exit(1)
    
    input("Nhấn Enter để tiếp tục...")
    print()
    
    # Khởi động Auto Processing Pipeline
    print("🚀 Đang khởi động Auto Processing Pipeline...")
    try:
        if sys.platform == "win32":
            pipeline_process = subprocess.Popen(
                ["cmd", "/c", "start", "cmd", "/k", "python", "auto_process_pipeline.py"],
                shell=True
            )
        else:
            # Linux/Mac: mở terminal mới
            pipeline_process = subprocess.Popen(
                ["python", "auto_process_pipeline.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        print("✓ Pipeline đã khởi động")
    except Exception as e:
        print(f"✗ Lỗi khởi động pipeline: {e}")
        sys.exit(1)
    
    time.sleep(2)
    
    # Khởi động Stream Recorder
    print("🚀 Đang khởi động Stream Recorder...")
    try:
        if sys.platform == "win32":
            recorder_process = subprocess.Popen(
                ["cmd", "/c", "start", "cmd", "/k", "python", "stream_recorder.py"],
                shell=True
            )
        else:
            recorder_process = subprocess.Popen(
                ["python", "stream_recorder.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        print("✓ Recorder đã khởi động")
    except Exception as e:
        print(f"✗ Lỗi khởi động recorder: {e}")
        sys.exit(1)
    
    print()
    print("=" * 70)
    print("✅ ĐÃ KHỞI ĐỘNG THÀNH CÔNG!")
    print("=" * 70)
    print()
    print("2 process đã được khởi động:")
    print("  1. Auto Processing Pipeline - Tự động xử lý video")
    print("  2. Stream Recorder - Ghi stream YouTube")
    print()
    print("💡 Đóng cửa sổ này, 2 process kia vẫn chạy.")
    print()
    
    input("Nhấn Enter để thoát...")


if __name__ == "__main__":
    main()
