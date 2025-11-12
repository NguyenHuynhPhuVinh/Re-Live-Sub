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
    def __init__(self, output_dir="recordings", segment_duration=300, enhance_quality=False, 
                 max_retries=10, retry_delay=5):
        """
        Args:
            output_dir: Thư mục lưu video
            segment_duration: Độ dài mỗi segment (giây), mặc định 300s = 5 phút
            enhance_quality: True = re-encode với bitrate cao hơn (chậm hơn, file lớn hơn)
            max_retries: Số lần thử lại tối đa khi mất kết nối (mặc định 10)
            retry_delay: Thời gian chờ ban đầu giữa các lần retry (giây, mặc định 5)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.segment_duration = segment_duration
        self.enhance_quality = enhance_quality
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
    def get_stream_url(self, youtube_url):
        """Lấy direct stream URL từ YouTube"""
        try:
            # Chọn format tốt nhất: video + audio chất lượng cao nhất
            # bestvideo+bestaudio = chọn video và audio tốt nhất rồi merge
            # best = chọn stream đã merge sẵn tốt nhất
            cmd = [
                'yt-dlp',
                '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                '-g',  # Chỉ lấy URL, không download
                youtube_url
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            stream_url = result.stdout.strip()
            print(f"✓ Đã lấy stream URL (chất lượng cao nhất)")
            return stream_url
        except subprocess.CalledProcessError as e:
            print(f"✗ Lỗi khi lấy stream URL: {e.stderr}")
            return None
    
    def record_stream(self, youtube_url, stream_name=None):
        """
        Ghi stream thành các đoạn 5 phút với auto-reconnect
        
        Args:
            youtube_url: URL YouTube livestream
            stream_name: Tên để đặt cho các file (mặc định dùng timestamp)
        """
        if stream_name is None:
            stream_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print(f"🎥 Bắt đầu ghi stream: {youtube_url}")
        print(f"📁 Lưu vào: {self.output_dir}")
        print(f"⏱️  Mỗi segment: {self.segment_duration}s ({self.segment_duration//60} phút)")
        print(f"🔄 Auto-reconnect: Tối đa {self.max_retries} lần thử lại")
        
        retry_count = 0
        while retry_count <= self.max_retries:
            try:
                if retry_count > 0:
                    wait_time = self.retry_delay * (2 ** (retry_count - 1))  # Exponential backoff
                    print(f"\n⏳ Đợi {wait_time}s trước khi thử lại (lần {retry_count}/{self.max_retries})...")
                    time.sleep(wait_time)
                
                # Lấy stream URL
                print(f"\n🔍 Đang lấy stream URL...")
                stream_url = self.get_stream_url(youtube_url)
                if not stream_url:
                    print(f"✗ Không lấy được stream URL")
                    retry_count += 1
                    continue
                
                # Thử ghi stream
                success = self._record_stream_internal(youtube_url, stream_name, stream_url, retry_count)
                
                if success:
                    print(f"\n✓ Hoàn thành ghi stream")
                    break
                else:
                    retry_count += 1
                    if retry_count <= self.max_retries:
                        print(f"\n⚠️  Stream bị ngắt, sẽ thử reconnect...")
                    
            except KeyboardInterrupt:
                print("\n\n⏹️  Người dùng dừng ghi hình")
                break
            except Exception as e:
                print(f"\n✗ Lỗi không mong đợi: {e}")
                retry_count += 1
        
        if retry_count > self.max_retries:
            print(f"\n✗ Đã thử {self.max_retries} lần nhưng không thành công")
        
        # Liệt kê các file đã tạo
        self.list_recordings(stream_name)
    
    def _record_stream_internal(self, youtube_url, stream_name, stream_url, attempt_number):
        """
        Hàm nội bộ để ghi stream (một lần thử)
        
        Returns:
            True nếu hoàn thành bình thường (user dừng)
            False nếu stream bị ngắt và cần retry
        """
        # Tìm segment number tiếp theo (để tiếp tục đánh số khi reconnect)
        existing_files = sorted(self.output_dir.glob(f"{stream_name}_*.mp4"))
        if existing_files:
            # Lấy số cuối cùng từ file cuối
            last_file = existing_files[-1].stem
            try:
                last_num = int(last_file.split('_')[-1])
                start_number = last_num + 1
            except:
                start_number = len(existing_files)
        else:
            start_number = 0
        
        # Pattern cho tên file: streamname_001.mp4, streamname_002.mp4, ...
        output_pattern = str(self.output_dir / f"{stream_name}_%03d.mp4")
        
        # FFmpeg command để ghi và chia segments
        if self.enhance_quality:
            # Re-encode với bitrate cao và chất lượng tốt
            if attempt_number == 0:
                print(f"⚡ Chế độ: Enhance Quality (re-encode với bitrate cao)")
                print(f"   ⚠️  Lưu ý: Chậm hơn, file lớn hơn, không tạo thêm chi tiết")
            
            ffmpeg_cmd = [
                'ffmpeg',
                '-reconnect', '1',  # Tự động reconnect
                '-reconnect_streamed', '1',  # Reconnect cho streamed content
                '-reconnect_delay_max', '5',  # Max delay giữa các reconnect (giây)
                '-i', stream_url,
                # Video encoding
                '-c:v', 'libx264',  # H.264 encoder
                '-preset', 'slow',  # Preset chậm = chất lượng tốt hơn
                '-crf', '18',  # Chất lượng cao (18 = visually lossless)
                '-b:v', '10M',  # Target bitrate 10 Mbps (cao hơn nhiều so với 3.3 Mbps)
                '-maxrate', '12M',  # Max bitrate
                '-bufsize', '20M',  # Buffer size
                '-pix_fmt', 'yuv420p',  # Pixel format tương thích
                '-profile:v', 'high',  # H.264 profile cao
                '-level', '4.2',  # H.264 level
                # Audio encoding
                '-c:a', 'aac',  # AAC encoder
                '-b:a', '192k',  # Audio bitrate 192 kbps (cao hơn)
                '-ar', '48000',  # Sample rate 48kHz
                # Segment settings
                '-f', 'segment',
                '-segment_time', str(self.segment_duration),
                '-segment_format', 'mp4',
                '-segment_wrap', '0',
                '-segment_start_number', str(start_number),  # Bắt đầu từ số này
                '-reset_timestamps', '1',
                # Output
                output_pattern
            ]
        else:
            # Copy stream trực tiếp (nhanh, giữ nguyên chất lượng gốc)
            if attempt_number == 0:
                print(f"⚡ Chế độ: Copy Stream (nhanh, giữ nguyên chất lượng gốc)")
            
            ffmpeg_cmd = [
                'ffmpeg',
                '-reconnect', '1',  # Tự động reconnect
                '-reconnect_streamed', '1',  # Reconnect cho streamed content
                '-reconnect_delay_max', '5',  # Max delay giữa các reconnect (giây)
                '-i', stream_url,
                '-c', 'copy',  # Copy codec, không re-encode
                '-f', 'segment',
                '-segment_time', str(self.segment_duration),
                '-segment_format', 'mp4',
                '-segment_wrap', '0',
                '-segment_start_number', str(start_number),  # Bắt đầu từ số này
                '-reset_timestamps', '1',
                output_pattern
            ]
        
        if attempt_number == 0:
            print(f"\n🔴 Đang ghi stream...")
            print(f"Nhấn Ctrl+C để dừng\n")
        else:
            print(f"\n🔄 Reconnecting... (lần thử #{attempt_number + 1})")
        
        if attempt_number == 0:
            print(f"🔧 Debug: FFmpeg command:")
            print(f"   {' '.join(ffmpeg_cmd)}\n")
        
        # Chạy ffmpeg
        process = subprocess.Popen(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Monitor output
        segment_count = start_number
        last_output_time = time.time()
        stream_error = False
        user_interrupted = False
        
        try:
            for line in process.stderr:
                # FFmpeg output đi vào stderr
                if attempt_number == 0 or 'error' in line.lower():
                    print(f"[FFmpeg] {line.strip()}")
                
                if 'segment:' in line.lower() or 'Opening' in line:
                    segment_count += 1
                    print(f"✓ Đã tạo segment #{segment_count}")
                    last_output_time = time.time()
                
                # Check for connection errors
                if any(err in line.lower() for err in ['connection', 'timeout', 'i/o error', 'server returned']):
                    print(f"⚠️  Lỗi kết nối: {line.strip()}")
                    stream_error = True
                
                # Check for other errors
                if 'error' in line.lower() or 'failed' in line.lower():
                    if 'error' in line.lower():
                        stream_error = True
                
                # Timeout detection: không có output trong 30s
                if time.time() - last_output_time > 30:
                    print(f"⚠️  Không nhận được dữ liệu trong 30s, có thể stream bị ngắt")
                    stream_error = True
                    break
                    
            process.wait()
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Đang dừng ghi hình...")
            user_interrupted = True
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            print("✓ Đã dừng")
        
        # Return True nếu user dừng (không cần retry)
        # Return False nếu stream error (cần retry)
        if user_interrupted:
            return True
        elif stream_error or process.returncode != 0:
            return False
        else:
            return True
    
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
    # Hỏi user có muốn enhance quality không
    print("Chọn chế độ ghi:")
    print("1. Copy Stream (nhanh, giữ nguyên chất lượng gốc)")
    print("2. Enhance Quality (chậm hơn, re-encode với bitrate 10 Mbps)")
    print("\n💡 Lưu ý: Enhance không tạo thêm chi tiết, chỉ làm mượt hơn")
    
    choice = input("\nNhập lựa chọn (1 hoặc 2, mặc định 1): ").strip() or '1'
    enhance = (choice == '2')
    
    # Ví dụ sử dụng
    recorder = YouTubeStreamRecorder(
        output_dir="recordings",
        segment_duration=300,  # 5 phút
        enhance_quality=enhance
    )
    
    # Nhập URL
    youtube_url = input("\nNhập YouTube livestream URL: ").strip()
    if not youtube_url:
        youtube_url = "https://www.youtube.com/watch?v=VXciXPHJvYk"  # Default
    
    stream_name = input("Tên stream (Enter để dùng timestamp): ").strip() or None
    
    # Bắt đầu ghi
    recorder.record_stream(youtube_url, stream_name=stream_name)


if __name__ == "__main__":
    main()
