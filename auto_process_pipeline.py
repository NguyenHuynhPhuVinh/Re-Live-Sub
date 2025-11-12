"""
Auto Video Processing Pipeline - Tự động xử lý video sau khi record xong
Quy trình:
1. Theo dõi thư mục recordings để phát hiện video mới
2. Tự động tạo SRT bằng Gemini
3. Tự động gắn phụ đề vào video
4. Di chuyển video đã xử lý vào thư mục processed
"""

import os
import sys
import time
import shutil
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv

# Import các class từ scripts khác
from generate_srt import GeminiSRTGenerator
from merge_subtitle import SubtitleMerger

# Load environment variables
load_dotenv()


class VideoProcessingPipeline:
    def __init__(self, 
                 watch_dir="recordings",
                 temp_dir="recordings/temp",
                 processed_dir="processed",
                 language='vi',
                 burn_subtitle=True,
                 stable_time=10):
        """
        Args:
            watch_dir: Thư mục chứa video hoàn chỉnh
            temp_dir: Thư mục chứa video đang record
            processed_dir: Thư mục lưu video đã xử lý
            language: Ngôn ngữ phụ đề (vi/en)
            burn_subtitle: True = burn subtitle vào video
            stable_time: Thời gian chờ file ổn định (giây)
        """
        self.watch_dir = Path(watch_dir)
        self.temp_dir = Path(temp_dir)
        self.processed_dir = Path(processed_dir)
        self.language = language
        self.burn_subtitle = burn_subtitle
        self.stable_time = stable_time
        
        # Tạo thư mục nếu chưa có
        self.watch_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        self.processed_dir.mkdir(exist_ok=True)
        
        # Khởi tạo các processor
        try:
            self.srt_generator = GeminiSRTGenerator()
            self.subtitle_merger = SubtitleMerger()
        except Exception as e:
            print(f"✗ Lỗi khởi tạo: {e}")
            sys.exit(1)
        
        # Tracking processed files
        self.processed_files = set()
        self.processing_queue = {}  # {file_path: last_modified_time}
    
    def is_file_stable(self, file_path):
        """Kiểm tra file đã ổn định chưa (không còn ghi thêm)"""
        try:
            current_size = file_path.stat().st_size
            current_mtime = file_path.stat().st_mtime
            
            # Kiểm tra xem file có trong queue chưa
            if file_path in self.processing_queue:
                last_mtime = self.processing_queue[file_path]
                
                # Nếu mtime không đổi trong stable_time giây
                if current_mtime == last_mtime:
                    time_diff = time.time() - current_mtime
                    if time_diff >= self.stable_time:
                        return True
                else:
                    # Update mtime mới
                    self.processing_queue[file_path] = current_mtime
                    return False
            else:
                # Thêm vào queue
                self.processing_queue[file_path] = current_mtime
                return False
                
        except Exception as e:
            print(f"⚠️  Lỗi kiểm tra file: {e}")
            return False
    
    def process_video(self, video_path):
        """Xử lý một video: tạo SRT → merge subtitle → move to processed"""
        video_path = Path(video_path)
        
        # Kiểm tra đã xử lý chưa
        if video_path in self.processed_files:
            return
        
        # Kiểm tra file có phải video không
        if video_path.suffix.lower() not in ['.mp4', '.mkv', '.avi', '.mov']:
            return
        
        # Bỏ qua file _sub (đã có subtitle)
        if '_sub' in video_path.stem:
            return
        
        print(f"\n{'='*70}")
        print(f"🎬 BẮT ĐẦU XỬ LÝ: {video_path.name}")
        print(f"{'='*70}")
        print(f"⏰ Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Bước 1: Tạo SRT
            print(f"\n📝 BƯỚC 1: Tạo phụ đề SRT")
            print(f"-" * 70)
            srt_path = self.srt_generator.generate_srt_from_video(
                video_path,
                language=self.language
            )
            print(f"✓ Hoàn thành tạo SRT")
            
            # Bước 2: Merge subtitle
            print(f"\n🔗 BƯỚC 2: Gắn phụ đề vào video")
            print(f"-" * 70)
            output_video = self.subtitle_merger.merge_subtitle(
                video_path,
                srt_path=srt_path,
                burn_in=self.burn_subtitle
            )
            print(f"✓ Hoàn thành gắn phụ đề")
            
            # Bước 3: Di chuyển file
            print(f"\n📦 BƯỚC 3: Di chuyển file đã xử lý")
            print(f"-" * 70)
            
            # Di chuyển video có subtitle
            final_video = self.processed_dir / output_video.name
            shutil.move(str(output_video), str(final_video))
            print(f"✓ Video có sub: {final_video}")
            
            # Di chuyển file SRT
            final_srt = self.processed_dir / srt_path.name
            shutil.move(str(srt_path), str(final_srt))
            print(f"✓ File SRT: {final_srt}")
            
            # Optional: Di chuyển video gốc
            original_video = self.processed_dir / f"original_{video_path.name}"
            shutil.move(str(video_path), str(original_video))
            print(f"✓ Video gốc: {original_video}")
            
            # Đánh dấu đã xử lý
            self.processed_files.add(video_path)
            if video_path in self.processing_queue:
                del self.processing_queue[video_path]
            
            print(f"\n{'='*70}")
            print(f"✅ HOÀN THÀNH: {video_path.name}")
            print(f"{'='*70}\n")
            
        except Exception as e:
            print(f"\n{'='*70}")
            print(f"❌ LỖI KHI XỬ LÝ: {video_path.name}")
            print(f"{'='*70}")
            print(f"Chi tiết: {e}")
            print()
    
    def scan_existing_videos(self):
        """Quét và xử lý các video đã có sẵn trong thư mục"""
        print(f"🔍 Quét video có sẵn trong {self.watch_dir}...")
        
        video_files = []
        for ext in ['.mp4', '.mkv', '.avi', '.mov']:
            video_files.extend(self.watch_dir.glob(f"*{ext}"))
        
        # Lọc bỏ file _sub và file trong temp
        video_files = [
            v for v in video_files 
            if '_sub' not in v.stem and not str(v).startswith(str(self.temp_dir))
        ]
        
        if video_files:
            print(f"📹 Tìm thấy {len(video_files)} video chưa xử lý")
            for video in sorted(video_files):
                self.process_video(video)
        else:
            print(f"✓ Không có video nào cần xử lý")
    
    def start_watching(self):
        """Bắt đầu theo dõi thư mục"""
        print(f"\n{'='*70}")
        print(f"🚀 AUTO VIDEO PROCESSING PIPELINE")
        print(f"{'='*70}")
        print(f"📁 Theo dõi: {self.watch_dir.absolute()}")
        print(f"📁 Temp: {self.temp_dir.absolute()}")
        print(f"📁 Output: {self.processed_dir.absolute()}")
        print(f"🌐 Ngôn ngữ: {self.language}")
        print(f"🔥 Burn subtitle: {'Có' if self.burn_subtitle else 'Không'}")
        print(f"⏱️  Thời gian chờ ổn định: {self.stable_time}s")
        print(f"{'='*70}\n")
        
        # Xử lý video có sẵn
        self.scan_existing_videos()
        
        # Bắt đầu watch mode
        print(f"\n👀 Đang theo dõi thư mục...")
        print(f"💡 Nhấn Ctrl+C để dừng\n")
        
        event_handler = VideoFileHandler(self)
        observer = Observer()
        observer.schedule(event_handler, str(self.watch_dir), recursive=False)
        observer.start()
        
        try:
            while True:
                # Kiểm tra các file trong queue
                files_to_process = []
                for file_path in list(self.processing_queue.keys()):
                    if self.is_file_stable(file_path):
                        files_to_process.append(file_path)
                
                # Xử lý các file đã ổn định
                for file_path in files_to_process:
                    self.process_video(file_path)
                
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Đang dừng pipeline...")
            observer.stop()
        
        observer.join()
        print("✓ Đã dừng")


class VideoFileHandler(FileSystemEventHandler):
    """Handler để theo dõi file events"""
    
    def __init__(self, pipeline):
        self.pipeline = pipeline
    
    def on_created(self, event):
        """Khi có file mới được tạo"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Bỏ qua file trong temp
        if str(file_path).startswith(str(self.pipeline.temp_dir)):
            return
        
        # Chỉ xử lý video
        if file_path.suffix.lower() in ['.mp4', '.mkv', '.avi', '.mov']:
            if '_sub' not in file_path.stem:
                print(f"📥 Phát hiện video mới: {file_path.name}")
                # Thêm vào queue để kiểm tra stable
                self.pipeline.processing_queue[file_path] = time.time()
    
    def on_modified(self, event):
        """Khi file bị sửa đổi"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Bỏ qua file trong temp
        if str(file_path).startswith(str(self.pipeline.temp_dir)):
            return
        
        # Update mtime trong queue
        if file_path in self.pipeline.processing_queue:
            self.pipeline.processing_queue[file_path] = time.time()


def main():
    """Main function"""
    
    # Kiểm tra API key
    if not os.environ.get('GEMINI_API_KEY'):
        print("⚠️  Chưa đặt GEMINI_API_KEY!")
        print("\nCách đặt:")
        print("  1. Tạo file .env trong thư mục này")
        print("  2. Thêm dòng: GEMINI_API_KEY=your_api_key_here")
        print("\nLấy API key tại: https://aistudio.google.com/apikey")
        sys.exit(1)
    
    # Cấu hình
    print("⚙️  CẤU HÌNH PIPELINE")
    print("=" * 70)
    
    watch_dir = input("Thư mục chứa video hoàn chỉnh (mặc định: recordings): ").strip() or "recordings"
    temp_dir = input("Thư mục video đang record (mặc định: recordings/temp): ").strip() or "recordings/temp"
    processed_dir = input("Thư mục lưu video đã xử lý (mặc định: processed): ").strip() or "processed"
    language = input("Ngôn ngữ phụ đề (vi/en, mặc định: vi): ").strip() or "vi"
    
    burn_choice = input("Burn subtitle vào video? (y/n, mặc định: y): ").strip().lower() or "y"
    burn_subtitle = burn_choice == 'y'
    
    stable_time_input = input("Thời gian chờ file ổn định (giây, mặc định: 10): ").strip()
    stable_time = int(stable_time_input) if stable_time_input else 10
    
    # Khởi tạo pipeline
    pipeline = VideoProcessingPipeline(
        watch_dir=watch_dir,
        temp_dir=temp_dir,
        processed_dir=processed_dir,
        language=language,
        burn_subtitle=burn_subtitle,
        stable_time=stable_time
    )
    
    # Bắt đầu
    pipeline.start_watching()


if __name__ == "__main__":
    main()
