"""
Video Subtitle Merger - Ghép phụ đề SRT vào video bằng FFmpeg
Yêu cầu: FFmpeg đã cài đặt
"""

import subprocess
import sys
from pathlib import Path


class SubtitleMerger:
    def __init__(self):
        """Khởi tạo SubtitleMerger"""
        self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        """Kiểm tra FFmpeg đã cài đặt chưa"""
        try:
            subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  FFmpeg chưa được cài đặt!")
            print("\nCách cài đặt:")
            print("  1. Tải tại: https://ffmpeg.org/download.html")
            print("  2. Thêm FFmpeg vào PATH")
            sys.exit(1)
    
    def merge_subtitle(self, video_path, srt_path=None, output_path=None, 
                       subtitle_style=None, burn_in=True):
        """
        Ghép phụ đề vào video
        
        Args:
            video_path: Đường dẫn video gốc
            srt_path: Đường dẫn file SRT (mặc định: cùng tên với video)
            output_path: Đường dẫn video output (mặc định: video_name_sub.mp4)
            subtitle_style: Style cho phụ đề (dict với các key: font, size, color, etc.)
            burn_in: True = burn subtitle vào video, False = embed subtitle stream
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            raise FileNotFoundError(f"Không tìm thấy video: {video_path}")
        
        # Tự động tìm file SRT nếu không chỉ định
        if srt_path is None:
            srt_path = video_path.with_suffix('.srt')
        else:
            srt_path = Path(srt_path)
        
        if not srt_path.exists():
            raise FileNotFoundError(f"Không tìm thấy file SRT: {srt_path}")
        
        # Tạo tên file output
        if output_path is None:
            output_path = video_path.parent / f"{video_path.stem}_sub{video_path.suffix}"
        else:
            output_path = Path(output_path)
        
        print(f"🎬 Video: {video_path.name}")
        print(f"📝 Phụ đề: {srt_path.name}")
        print(f"💾 Output: {output_path.name}")
        
        if burn_in:
            self._burn_subtitle(video_path, srt_path, output_path, subtitle_style)
        else:
            self._embed_subtitle(video_path, srt_path, output_path)
        
        return output_path
    
    def _burn_subtitle(self, video_path, srt_path, output_path, subtitle_style):
        """Burn phụ đề vào video (không thể tắt được)"""
        print(f"\n🔥 Đang burn phụ đề vào video...")
        
        # Đường dẫn tuyệt đối
        video_abs = str(video_path.absolute())
        srt_abs = str(srt_path.absolute())
        output_abs = str(output_path.absolute())
        
        # Escape đường dẫn SRT cho subtitles filter trên Windows
        # Phải escape backslash và dấu hai chấm
        srt_escaped = srt_abs.replace('\\', '\\\\\\\\').replace(':', '\\\\:')
        
        # Tạo filter subtitles (không dùng force_style vì không được hỗ trợ tốt)
        # Thay vào đó dùng subtitles filter đơn giản
        vf_filter = f"subtitles={srt_escaped}"
        
        # Nếu có custom style, cảnh báo user
        if subtitle_style:
            print("⚠️  Lưu ý: Custom style không được hỗ trợ với SRT.")
            print("    Để tùy chỉnh style, hãy convert SRT sang ASS trước.")
        
        print("💡 Tối ưu CPU: Nhanh + Chất lượng cao...")
        print("    Preset: faster | CRF: 18 (visually lossless)")
        
        # CPU encoding với settings tối ưu cho cả tốc độ và chất lượng
        cmd = [
            'ffmpeg',
            '-i', video_abs,
            '-vf', vf_filter,
            '-c:a', 'copy',  # Copy audio, không re-encode
            '-c:v', 'libx264',  # CPU encoder
            '-preset', 'ultrafast',
            '-crf', '18',  # Chất lượng rất cao (18 = visually lossless, 23 = default)
            '-tune', 'film',  # Tối ưu cho video film/game
            '-movflags', '+faststart',  # Tối ưu cho streaming/web
            '-threads', '0',  # Dùng tất cả CPU cores
            '-y',
            output_abs
        ]
        
        print(f"\n🔧 Debug - FFmpeg command:")
        print(f"   {' '.join(cmd)}\n")
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Merge stderr vào stdout
                text=True
            )
            
            # Hiển thị output
            output_lines = []
            for line in process.stdout:
                output_lines.append(line)
                if 'time=' in line:
                    print(f"\r⏳ {line.strip()}", end='', flush=True)
                elif 'error' in line.lower() or 'invalid' in line.lower():
                    print(f"\n⚠️  {line.strip()}")
            
            process.wait()
            
            if process.returncode == 0:
                print(f"\n✓ Đã tạo video có phụ đề: {output_path}")
            else:
                print(f"\n✗ Lỗi khi xử lý video (exit code: {process.returncode})")
                print(f"\nChi tiết lỗi (20 dòng cuối):")
                for line in output_lines[-20:]:
                    print(f"  {line.strip()}")
                
        except Exception as e:
            print(f"\n✗ Lỗi: {e}")
    
    def _embed_subtitle(self, video_path, srt_path, output_path):
        """Embed phụ đề vào video (có thể bật/tắt)"""
        print(f"\n📦 Đang embed phụ đề vào video...")
        
        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-i', str(srt_path),
            '-c', 'copy',  # Copy tất cả streams
            '-c:s', 'mov_text',  # Subtitle codec cho MP4
            '-metadata:s:s:0', 'language=vie',  # Đánh dấu ngôn ngữ
            '-y',
            str(output_path)
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✓ Đã embed phụ đề vào video: {output_path}")
                print("💡 Phụ đề có thể bật/tắt trong trình phát video")
            else:
                print(f"✗ Lỗi: {result.stderr}")
                
        except Exception as e:
            print(f"✗ Lỗi: {e}")
    
    def batch_merge(self, video_dir, pattern="*.mp4", burn_in=True):
        """
        Ghép phụ đề cho tất cả video trong thư mục
        
        Args:
            video_dir: Thư mục chứa video
            pattern: Pattern để tìm video
            burn_in: True = burn subtitle, False = embed subtitle
        """
        video_dir = Path(video_dir)
        video_files = sorted(video_dir.glob(pattern))
        
        # Lọc bỏ các file đã có _sub
        video_files = [v for v in video_files if '_sub' not in v.stem]
        
        if not video_files:
            print(f"⚠️  Không tìm thấy video nào trong {video_dir}")
            return
        
        print(f"📹 Tìm thấy {len(video_files)} video")
        print(f"🔥 Chế độ: {'Burn-in' if burn_in else 'Embed'}\n")
        
        results = []
        for i, video_path in enumerate(video_files, 1):
            print(f"\n{'='*60}")
            print(f"[{i}/{len(video_files)}]")
            print(f"{'='*60}")
            
            # Kiểm tra có file SRT không
            srt_path = video_path.with_suffix('.srt')
            if not srt_path.exists():
                print(f"⚠️  Không tìm thấy file SRT cho {video_path.name}")
                results.append((video_path, None, 'no_srt'))
                continue
            
            try:
                output_path = self.merge_subtitle(
                    video_path,
                    burn_in=burn_in
                )
                results.append((video_path, output_path, 'success'))
            except Exception as e:
                print(f"✗ Lỗi: {e}")
                results.append((video_path, None, f'error: {e}'))
        
        # Tổng kết
        print(f"\n{'='*60}")
        print(f"📊 TỔNG KẾT")
        print(f"{'='*60}")
        
        success_count = sum(1 for _, _, status in results if status == 'success')
        print(f"✓ Thành công: {success_count}/{len(video_files)}")
        
        if success_count < len(video_files):
            print(f"\n⚠️  Lỗi:")
            for video, output, status in results:
                if status != 'success':
                    print(f"  - {video.name}: {status}")


def main():
    """Ví dụ sử dụng"""
    merger = SubtitleMerger()
    
    print("Chọn chế độ:")
    print("1. Ghép phụ đề cho 1 video")
    print("2. Ghép phụ đề cho tất cả video trong thư mục")
    
    choice = input("\nNhập lựa chọn (1 hoặc 2): ").strip()
    
    if choice == '1':
        # Xử lý 1 video
        video_path = input("Đường dẫn video: ").strip().strip('"').strip("'")
        srt_path = input("Đường dẫn SRT (Enter để tự động tìm): ").strip().strip('"').strip("'")
        
        print("\nChọn kiểu phụ đề:")
        print("1. Burn-in (phụ đề cố định, không tắt được)")
        print("2. Embed (phụ đề có thể bật/tắt)")
        burn_choice = input("Nhập lựa chọn (1 hoặc 2, mặc định 1): ").strip() or '1'
        
        burn_in = burn_choice == '1'
        
        # Style tùy chỉnh (optional)
        custom_style = input("\nTùy chỉnh style? (y/n, mặc định n): ").strip().lower()
        subtitle_style = None
        
        if custom_style == 'y':
            subtitle_style = {}
            font = input("Font (mặc định Arial): ").strip()
            if font:
                subtitle_style['font'] = font
            
            size = input("Kích thước (mặc định 24): ").strip()
            if size:
                subtitle_style['size'] = int(size)
        
        merger.merge_subtitle(
            video_path,
            srt_path if srt_path else None,
            burn_in=burn_in,
            subtitle_style=subtitle_style
        )
        
    elif choice == '2':
        # Xử lý batch
        video_dir = input("Thư mục chứa video (mặc định: recordings): ").strip() or 'recordings'
        pattern = input("Pattern (mặc định: *.mp4): ").strip() or '*.mp4'
        
        print("\nChọn kiểu phụ đề:")
        print("1. Burn-in (phụ đề cố định, không tắt được)")
        print("2. Embed (phụ đề có thể bật/tắt)")
        burn_choice = input("Nhập lựa chọn (1 hoặc 2, mặc định 1): ").strip() or '1'
        
        burn_in = burn_choice == '1'
        
        merger.batch_merge(video_dir, pattern, burn_in)
    
    else:
        print("Lựa chọn không hợp lệ!")


if __name__ == "__main__":
    main()
