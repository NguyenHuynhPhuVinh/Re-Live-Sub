"""
YouTube Live Streamer - Phát trực tiếp video file lên YouTube Live
Yêu cầu: FFmpeg, YouTube Live stream key, watchdog
"""

import subprocess
import sys
import threading
import time
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class YouTubeLiveStreamer:
    def __init__(self, stream_key=None):
        """
        Args:
            stream_key: YouTube Live stream key (lấy từ YouTube Studio)
        """
        self.stream_key = stream_key
        self.rtmp_url = "rtmp://a.rtmp.youtube.com/live2"
        
        if not self.stream_key:
            print("⚠️  Chưa có Stream Key!")
            print("\n📝 Cách lấy Stream Key:")
            print("1. Vào YouTube Studio: https://studio.youtube.com")
            print("2. Chọn 'Go Live' → 'Stream'")
            print("3. Copy 'Stream key' (giữ bí mật!)")
            print("4. Đặt vào biến môi trường YOUTUBE_STREAM_KEY")
            print("   hoặc truyền vào khi khởi tạo")
    
    def stream_video(self, video_path, loop=False, start_time=None):
        """
        Stream video file lên YouTube Live
        
        Args:
            video_path: Đường dẫn video
            loop: True = lặp lại video vô hạn
            start_time: Thời gian bắt đầu (HH:MM:SS), None = từ đầu
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            raise FileNotFoundError(f"Không tìm thấy video: {video_path}")
        
        if not self.stream_key:
            raise ValueError("Cần có Stream Key để stream!")
        
        print(f"\n🎬 Video: {video_path.name}")
        print(f"📡 Đang stream lên YouTube Live...")
        print(f"🔒 Privacy: Riêng tư (thay đổi trong YouTube Studio)")
        if loop:
            print(f"🔁 Chế độ: Loop vô hạn")
        print(f"\n💡 Mở YouTube Studio để xem stream và đổi sang Public")
        print(f"   https://studio.youtube.com/")
        print(f"\n⏹️  Nhấn Ctrl+C để dừng stream\n")
        
        # FFmpeg command để stream
        cmd = [
            'ffmpeg',
            '-re',  # Read input at native frame rate (quan trọng cho streaming)
        ]
        
        # Loop nếu cần
        if loop:
            cmd.extend(['-stream_loop', '-1'])  # Loop vô hạn
        
        # Start time nếu có
        if start_time:
            cmd.extend(['-ss', start_time])
        
        # Input
        cmd.extend(['-i', str(video_path)])
        
        # Video encoding cho YouTube
        cmd.extend([
            # Video
            '-c:v', 'libx264',  # H.264 codec
            '-preset', 'veryfast',  # Preset nhanh cho streaming
            '-b:v', '4500k',  # Bitrate 4.5 Mbps (tốt cho 1080p)
            '-maxrate', '4500k',
            '-bufsize', '9000k',
            '-pix_fmt', 'yuv420p',
            '-g', '60',  # Keyframe interval (2 giây với 30fps)
            '-r', '30',  # Frame rate 30fps
            
            # Audio
            '-c:a', 'aac',  # AAC codec
            '-b:a', '128k',  # Audio bitrate
            '-ar', '44100',  # Sample rate
            '-ac', '2',  # Stereo
            
            # Streaming
            '-f', 'flv',  # FLV format cho RTMP
            f"{self.rtmp_url}/{self.stream_key}"
        ])
        
        print(f"🔧 FFmpeg command:")
        print(f"   {' '.join(cmd[:10])}... (stream key ẩn)\n")
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Monitor output
            for line in process.stdout:
                # Hiển thị thông tin quan trọng
                if 'time=' in line or 'speed=' in line:
                    print(f"\r⏳ {line.strip()}", end='', flush=True)
                elif 'error' in line.lower():
                    print(f"\n⚠️  {line.strip()}")
            
            process.wait()
            
            if process.returncode == 0:
                print(f"\n✓ Stream kết thúc")
            else:
                print(f"\n✗ Stream bị lỗi (exit code: {process.returncode})")
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Đang dừng stream...")
            process.terminate()
            process.wait()
            print("✓ Đã dừng stream")
        except Exception as e:
            print(f"\n✗ Lỗi: {e}")
    
    def stream_playlist(self, video_dir, pattern="*_sub.mp4", loop=False, dynamic=True):
        """
        Stream playlist các video với khả năng tự động thêm video mới
        
        Args:
            video_dir: Thư mục chứa video
            pattern: Pattern để tìm video
            loop: True = lặp lại playlist
            dynamic: True = tự động thêm video mới vào playlist khi đang stream
        """
        video_dir = Path(video_dir)
        video_files = sorted(video_dir.glob(pattern))
        
        if not video_files:
            print(f"⚠️  Không tìm thấy video nào trong {video_dir}")
            return
        
        print(f"📹 Tìm thấy {len(video_files)} video")
        print(f"🔁 Loop: {'Có' if loop else 'Không'}")
        print(f"🔄 Dynamic: {'Có - Tự động thêm video mới' if dynamic else 'Không'}\n")
        
        if not self.stream_key:
            raise ValueError("Cần có Stream Key để stream!")
        
        # Tạo file concat list cho FFmpeg
        concat_file = video_dir / 'playlist.txt'
        playlist_lock = threading.Lock()
        
        def write_playlist(videos):
            """Ghi playlist file"""
            with playlist_lock:
                with open(concat_file, 'w', encoding='utf-8') as f:
                    for video in videos:
                        video_path = str(video.absolute()).replace("'", "'\\''")
                        f.write(f"file '{video_path}'\n")
        
        # Ghi playlist ban đầu
        write_playlist(video_files)
        print(f"📝 Đã tạo playlist: {concat_file.name}")
        
        # Setup watchdog nếu dynamic mode
        observer = None
        if dynamic:
            class PlaylistWatcher(FileSystemEventHandler):
                def __init__(self, video_dir, pattern, playlist_file, write_func):
                    self.video_dir = Path(video_dir)
                    self.pattern = pattern
                    self.playlist_file = playlist_file
                    self.write_func = write_func
                    self.known_videos = set(video_files)
                    self.pending_videos = {}  # {path: last_check_time}
                
                def on_created(self, event):
                    if event.is_directory:
                        return
                    
                    file_path = Path(event.src_path)
                    
                    # Kiểm tra pattern
                    if not self._match_pattern(file_path):
                        return
                    
                    # Thêm vào pending để kiểm tra stable
                    self.pending_videos[file_path] = time.time()
                    print(f"\n📥 Phát hiện video mới: {file_path.name}")
                
                def on_modified(self, event):
                    if event.is_directory:
                        return
                    
                    file_path = Path(event.src_path)
                    
                    # Update pending time
                    if file_path in self.pending_videos:
                        self.pending_videos[file_path] = time.time()
                
                def _match_pattern(self, file_path):
                    """Kiểm tra file có match pattern không"""
                    import fnmatch
                    return fnmatch.fnmatch(file_path.name, self.pattern)
                
                def check_and_add_stable_videos(self):
                    """Kiểm tra và thêm video đã stable vào playlist"""
                    current_time = time.time()
                    stable_videos = []
                    
                    for video_path, last_time in list(self.pending_videos.items()):
                        # Nếu file không thay đổi trong 5 giây
                        if current_time - last_time >= 5:
                            if video_path.exists() and video_path not in self.known_videos:
                                stable_videos.append(video_path)
                                self.known_videos.add(video_path)
                                del self.pending_videos[video_path]
                    
                    if stable_videos:
                        # Thêm vào playlist
                        all_videos = sorted(self.known_videos)
                        self.write_func(all_videos)
                        
                        for video in stable_videos:
                            print(f"\n✅ Đã thêm vào playlist: {video.name}")
                        print(f"📊 Tổng số video: {len(all_videos)}")
            
            watcher = PlaylistWatcher(video_dir, pattern, concat_file, write_playlist)
            observer = Observer()
            observer.schedule(watcher, str(video_dir), recursive=False)
            observer.start()
            print(f"👀 Đang theo dõi thư mục để thêm video mới...")
        
        print(f"📡 Đang stream playlist lên YouTube Live...\n")
        
        # FFmpeg command để stream playlist
        # Sử dụng concat protocol với safe=0 và f_strict=experimental
        cmd = [
            'ffmpeg',
            '-re',  # Read at native frame rate
            '-f', 'concat',
            '-safe', '0',
            '-protocol_whitelist', 'file,pipe,crypto,data',
        ]
        
        # Loop playlist nếu cần
        if loop:
            cmd.extend(['-stream_loop', '-1'])
        
        cmd.extend([
            '-i', str(concat_file),
            
            # Video encoding
            '-c:v', 'libx264',
            '-preset', 'veryfast',
            '-b:v', '4500k',
            '-maxrate', '4500k',
            '-bufsize', '9000k',
            '-pix_fmt', 'yuv420p',
            '-g', '60',
            '-r', '30',
            
            # Audio encoding
            '-c:a', 'aac',
            '-b:a', '128k',
            '-ar', '44100',
            '-ac', '2',
            
            # Streaming
            '-f', 'flv',
            f"{self.rtmp_url}/{self.stream_key}"
        ])
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            print(f"💡 Mở YouTube Studio để xem stream:")
            print(f"   https://studio.youtube.com/\n")
            print(f"⏹️  Nhấn Ctrl+C để dừng stream\n")
            
            # Monitor thread để kiểm tra video mới
            def monitor_new_videos():
                while process.poll() is None:
                    if dynamic and observer:
                        watcher.check_and_add_stable_videos()
                    time.sleep(2)
            
            if dynamic:
                monitor_thread = threading.Thread(target=monitor_new_videos, daemon=True)
                monitor_thread.start()
            
            # Monitor output
            for line in process.stdout:
                if 'time=' in line or 'speed=' in line:
                    print(f"\r⏳ {line.strip()}", end='', flush=True)
                elif 'error' in line.lower():
                    print(f"\n⚠️  {line.strip()}")
            
            process.wait()
            
            if process.returncode == 0:
                print(f"\n✓ Stream kết thúc")
            else:
                print(f"\n✗ Stream bị lỗi")
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Đang dừng stream...")
            process.terminate()
            process.wait()
            print("✓ Đã dừng stream")
        except Exception as e:
            print(f"\n✗ Lỗi: {e}")
        finally:
            # Dừng observer
            if observer:
                observer.stop()
                observer.join()
            
            # Xóa file concat
            if concat_file.exists():
                concat_file.unlink()


def main():
    """Ví dụ sử dụng"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    print("YouTube Live Streamer")
    print("="*60)
    
    # Lấy stream key
    stream_key = os.environ.get('YOUTUBE_STREAM_KEY')
    
    if not stream_key:
        print("\n⚠️  Chưa có Stream Key!")
        print("\n📝 Cách setup:")
        print("1. Vào YouTube Studio: https://studio.youtube.com")
        print("2. Chọn 'Go Live' → 'Stream'")
        print("3. Copy 'Stream key'")
        print("4. Thêm vào file .env:")
        print("   YOUTUBE_STREAM_KEY=your_stream_key_here")
        
        stream_key = input("\nHoặc nhập Stream Key ngay: ").strip()
        
        if not stream_key:
            sys.exit(1)
    
    streamer = YouTubeLiveStreamer(stream_key=stream_key)
    
    print("\nChọn chế độ:")
    print("1. Stream 1 video")
    print("2. Stream playlist (nhiều video)")
    
    choice = input("\nNhập lựa chọn (1 hoặc 2): ").strip()
    
    if choice == '1':
        # Stream 1 video
        video_path = input("Đường dẫn video: ").strip().strip('"').strip("'")
        loop = input("Loop video? (y/n, mặc định n): ").strip().lower() == 'y'
        
        streamer.stream_video(video_path, loop=loop)
        
    elif choice == '2':
        # Stream playlist
        video_dir = input("Thư mục chứa video (mặc định: recordings): ").strip() or 'recordings'
        pattern = input("Pattern (mặc định: *_sub.mp4): ").strip() or '*_sub.mp4'
        loop = input("Loop playlist? (y/n, mặc định n): ").strip().lower() == 'y'
        dynamic = input("Tự động thêm video mới? (y/n, mặc định y): ").strip().lower() != 'n'
        
        streamer.stream_playlist(video_dir, pattern, loop=loop, dynamic=dynamic)
    
    else:
        print("Lựa chọn không hợp lệ!")


if __name__ == "__main__":
    main()
