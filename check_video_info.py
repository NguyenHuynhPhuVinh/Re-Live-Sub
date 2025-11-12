"""
Video Info Checker - Kiểm tra thông tin video (resolution, bitrate, codec, etc.)
"""

import subprocess
import json
import sys
from pathlib import Path


def get_video_info(video_path):
    """Lấy thông tin chi tiết về video"""
    video_path = Path(video_path)
    
    if not video_path.exists():
        print(f"❌ Không tìm thấy video: {video_path}")
        return None
    
    # Dùng ffprobe để lấy thông tin
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        str(video_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        # Tìm video stream
        video_stream = None
        audio_stream = None
        
        for stream in data.get('streams', []):
            if stream['codec_type'] == 'video' and not video_stream:
                video_stream = stream
            elif stream['codec_type'] == 'audio' and not audio_stream:
                audio_stream = stream
        
        if not video_stream:
            print(f"❌ Không tìm thấy video stream")
            return None
        
        # Lấy thông tin format
        format_info = data.get('format', {})
        
        # Parse thông tin
        width = int(video_stream.get('width', 0))
        height = int(video_stream.get('height', 0))
        
        # Xác định resolution name
        if height >= 2160:
            res_name = "4K (2160p)"
        elif height >= 1440:
            res_name = "2K (1440p)"
        elif height >= 1080:
            res_name = "Full HD (1080p)"
        elif height >= 720:
            res_name = "HD (720p)"
        elif height >= 480:
            res_name = "SD (480p)"
        elif height >= 360:
            res_name = "360p"
        else:
            res_name = f"{height}p"
        
        # Bitrate
        bitrate = int(format_info.get('bit_rate', 0)) / 1000  # Chuyển sang kbps
        
        # Duration
        duration = float(format_info.get('duration', 0))
        duration_min = int(duration // 60)
        duration_sec = int(duration % 60)
        
        # File size
        file_size = video_path.stat().st_size / (1024 * 1024)  # MB
        
        # FPS
        fps_str = video_stream.get('r_frame_rate', '0/1')
        fps_parts = fps_str.split('/')
        fps = int(fps_parts[0]) / int(fps_parts[1]) if len(fps_parts) == 2 else 0
        
        # Codec
        video_codec = video_stream.get('codec_name', 'unknown')
        audio_codec = audio_stream.get('codec_name', 'unknown') if audio_stream else 'none'
        
        # In thông tin
        print(f"\n{'='*60}")
        print(f"📹 THÔNG TIN VIDEO: {video_path.name}")
        print(f"{'='*60}")
        print(f"📐 Độ phân giải:  {width}x{height} ({res_name})")
        print(f"🎞️  FPS:           {fps:.2f}")
        print(f"⏱️  Thời lượng:    {duration_min}:{duration_sec:02d}")
        print(f"💾 Kích thước:    {file_size:.2f} MB")
        print(f"📊 Bitrate:       {bitrate:.0f} kbps")
        print(f"🎬 Video codec:   {video_codec}")
        print(f"🔊 Audio codec:   {audio_codec}")
        
        if audio_stream:
            sample_rate = audio_stream.get('sample_rate', 'unknown')
            channels = audio_stream.get('channels', 'unknown')
            print(f"🎵 Audio:         {sample_rate} Hz, {channels} channels")
        
        print(f"{'='*60}\n")
        
        return {
            'width': width,
            'height': height,
            'resolution': res_name,
            'fps': fps,
            'duration': duration,
            'file_size_mb': file_size,
            'bitrate_kbps': bitrate,
            'video_codec': video_codec,
            'audio_codec': audio_codec
        }
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khi chạy ffprobe: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Lỗi parse JSON: {e}")
        return None
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return None


def compare_videos(video1_path, video2_path):
    """So sánh 2 video"""
    print("🔍 So sánh 2 video...\n")
    
    info1 = get_video_info(video1_path)
    info2 = get_video_info(video2_path)
    
    if not info1 or not info2:
        return
    
    print(f"{'='*60}")
    print(f"📊 SO SÁNH")
    print(f"{'='*60}")
    
    # So sánh resolution
    if info1['height'] == info2['height']:
        print(f"✅ Độ phân giải: Giống nhau ({info1['resolution']})")
    else:
        print(f"⚠️  Độ phân giải: Khác nhau")
        print(f"   Video 1: {info1['resolution']}")
        print(f"   Video 2: {info2['resolution']}")
    
    # So sánh file size
    size_diff = info2['file_size_mb'] - info1['file_size_mb']
    size_percent = (size_diff / info1['file_size_mb']) * 100
    print(f"\n💾 Kích thước:")
    print(f"   Video 1: {info1['file_size_mb']:.2f} MB")
    print(f"   Video 2: {info2['file_size_mb']:.2f} MB")
    print(f"   Chênh lệch: {size_diff:+.2f} MB ({size_percent:+.1f}%)")
    
    # So sánh bitrate
    bitrate_diff = info2['bitrate_kbps'] - info1['bitrate_kbps']
    bitrate_percent = (bitrate_diff / info1['bitrate_kbps']) * 100
    print(f"\n📊 Bitrate:")
    print(f"   Video 1: {info1['bitrate_kbps']:.0f} kbps")
    print(f"   Video 2: {info2['bitrate_kbps']:.0f} kbps")
    print(f"   Chênh lệch: {bitrate_diff:+.0f} kbps ({bitrate_percent:+.1f}%)")
    
    print(f"{'='*60}\n")


def batch_check(directory, pattern="*.mp4"):
    """Kiểm tra tất cả video trong thư mục"""
    directory = Path(directory)
    video_files = sorted(directory.glob(pattern))
    
    if not video_files:
        print(f"⚠️  Không tìm thấy video nào trong {directory}")
        return
    
    print(f"📹 Tìm thấy {len(video_files)} video\n")
    
    results = []
    for video_path in video_files:
        info = get_video_info(video_path)
        if info:
            results.append((video_path.name, info))
    
    # Tổng kết
    if results:
        print(f"\n{'='*60}")
        print(f"📊 TỔNG KẾT")
        print(f"{'='*60}")
        
        total_size = sum(info['file_size_mb'] for _, info in results)
        total_duration = sum(info['duration'] for _, info in results)
        
        print(f"📹 Tổng số video:  {len(results)}")
        print(f"💾 Tổng dung lượng: {total_size:.2f} MB ({total_size/1024:.2f} GB)")
        print(f"⏱️  Tổng thời lượng: {int(total_duration//60)}:{int(total_duration%60):02d}")
        print(f"{'='*60}\n")


def main():
    """Ví dụ sử dụng"""
    print("Chọn chế độ:")
    print("1. Kiểm tra 1 video")
    print("2. So sánh 2 video")
    print("3. Kiểm tra tất cả video trong thư mục")
    
    choice = input("\nNhập lựa chọn (1, 2 hoặc 3): ").strip()
    
    if choice == '1':
        video_path = input("Đường dẫn video: ").strip().strip('"').strip("'")
        get_video_info(video_path)
        
    elif choice == '2':
        video1 = input("Đường dẫn video 1 (gốc): ").strip().strip('"').strip("'")
        video2 = input("Đường dẫn video 2 (so sánh): ").strip().strip('"').strip("'")
        compare_videos(video1, video2)
        
    elif choice == '3':
        directory = input("Thư mục chứa video (mặc định: recordings): ").strip() or 'recordings'
        pattern = input("Pattern (mặc định: *.mp4): ").strip() or '*.mp4'
        batch_check(directory, pattern)
    
    else:
        print("Lựa chọn không hợp lệ!")


if __name__ == "__main__":
    main()
