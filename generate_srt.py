"""
Gemini Video to SRT Generator - Tạo phụ đề SRT từ video bằng Gemini API
Yêu cầu: pip install google-genai python-dotenv
"""

import os
import sys
import time
from pathlib import Path
from google import genai
from google.genai import types
import re
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()


class GeminiSRTGenerator:
    def __init__(self, api_key=None):
        """
        Args:
            api_key: Gemini API key (hoặc đặt biến môi trường GEMINI_API_KEY)
        """
        if api_key is None:
            api_key = os.environ.get('GEMINI_API_KEY')
        
        if not api_key:
            raise ValueError(
                "Cần có Gemini API key!\n"
                "Đặt biến môi trường: set GEMINI_API_KEY=your_key_here\n"
                "Hoặc truyền vào: GeminiSRTGenerator(api_key='your_key')"
            )
        
        self.client = genai.Client(api_key=api_key)
        self.model = 'models/gemini-2.5-flash'
    
    def generate_srt_from_video(self, video_path, output_srt_path=None, language='vi'):
        """
        Tạo file SRT từ video
        
        Args:
            video_path: Đường dẫn đến file video
            output_srt_path: Đường dẫn file SRT output (mặc định: video_name.srt)
            language: Ngôn ngữ phụ đề ('vi' cho tiếng Việt, 'en' cho tiếng Anh)
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            raise FileNotFoundError(f"Không tìm thấy video: {video_path}")
        
        if output_srt_path is None:
            output_srt_path = video_path.with_suffix('.srt')
        
        print(f"🎬 Đang xử lý video: {video_path.name}")
        print(f"📤 Đang tải lên Gemini...")
        
        # Tải video lên
        myfile = self.client.files.upload(file=str(video_path))
        print(f"✓ Đã tải lên: {myfile.name}")
        
        # Đợi file được xử lý
        print(f"⏳ Đang chờ Gemini xử lý video...")
        myfile = self._wait_for_file_active(myfile)
        print(f"✓ Video đã sẵn sàng")
        
        # Tạo prompt
        lang_instruction = {
            'vi': 'tiếng Việt',
            'en': 'English'
        }.get(language, 'tiếng Việt')
        
        prompt = f"""Hãy phân tích video này và tạo file phụ đề SRT hoàn chỉnh bằng {lang_instruction}.

Yêu cầu:
1. Transcribe toàn bộ nội dung âm thanh/lời nói trong video
2. Chia thành các đoạn phụ đề ngắn (mỗi đoạn 1-2 câu, tối đa 5 giây)
3. Đánh số thứ tự từ 1
4. Định dạng timestamp chính xác: HH:MM:SS,mmm --> HH:MM:SS,mmm
5. Nếu không có lời nói, hãy mô tả hành động/sự kiện quan trọng trong video

Định dạng SRT chuẩn:
1
00:00:00,000 --> 00:00:05,000
Dòng phụ đề đầu tiên

2
00:00:05,000 --> 00:00:10,000
Dòng phụ đề thứ hai

CHỈ trả về nội dung SRT, không thêm giải thích hay markdown."""

        print(f"🤖 Đang tạo phụ đề với Gemini...")
        
        # Gọi Gemini API
        response = self.client.models.generate_content(
            model=self.model,
            contents=[myfile, prompt]
        )
        
        srt_content = response.text.strip()
        
        # Làm sạch output (loại bỏ markdown nếu có)
        srt_content = self._clean_srt_output(srt_content)
        
        # Lưu file SRT
        with open(output_srt_path, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        
        print(f"✓ Đã tạo file SRT: {output_srt_path}")
        
        # Xóa file tạm trên Gemini (optional)
        try:
            self.client.files.delete(name=myfile.name)
            print(f"✓ Đã xóa file tạm trên Gemini")
        except:
            pass
        
        return output_srt_path
    
    def _wait_for_file_active(self, file, timeout=300):
        """
        Đợi file được xử lý xong (chuyển sang trạng thái ACTIVE)
        
        Args:
            file: File object từ upload
            timeout: Thời gian chờ tối đa (giây)
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Lấy thông tin file mới nhất
            file = self.client.files.get(name=file.name)
            
            if file.state == 'ACTIVE':
                return file
            elif file.state == 'FAILED':
                raise Exception(f"Xử lý video thất bại: {file.error}")
            
            # Đợi 2 giây trước khi check lại
            time.sleep(2)
            print(".", end="", flush=True)
        
        raise TimeoutError(f"Timeout: Video chưa được xử lý sau {timeout}s")
    
    def _clean_srt_output(self, text):
        """Làm sạch output từ Gemini, loại bỏ markdown code blocks"""
        # Loại bỏ markdown code blocks
        text = re.sub(r'^```(?:srt)?\n', '', text, flags=re.MULTILINE)
        text = re.sub(r'\n```$', '', text, flags=re.MULTILINE)
        text = text.strip()
        return text
    
    def batch_generate_srt(self, video_dir, pattern="*.mp4", language='vi'):
        """
        Tạo SRT cho tất cả video trong thư mục
        
        Args:
            video_dir: Thư mục chứa video
            pattern: Pattern để tìm video (mặc định: *.mp4)
            language: Ngôn ngữ phụ đề
        """
        video_dir = Path(video_dir)
        video_files = sorted(video_dir.glob(pattern))
        
        if not video_files:
            print(f"⚠️  Không tìm thấy video nào trong {video_dir}")
            return
        
        print(f"📹 Tìm thấy {len(video_files)} video")
        print(f"🌐 Ngôn ngữ: {language}\n")
        
        results = []
        for i, video_path in enumerate(video_files, 1):
            print(f"\n{'='*60}")
            print(f"[{i}/{len(video_files)}] {video_path.name}")
            print(f"{'='*60}")
            
            try:
                srt_path = self.generate_srt_from_video(
                    video_path,
                    language=language
                )
                results.append((video_path, srt_path, 'success'))
            except Exception as e:
                print(f"✗ Lỗi: {e}")
                results.append((video_path, None, f'error: {e}'))
        
        # Tổng kết
        print(f"\n{'='*60}")
        print(f"📊 TỔNG KẾT")
        print(f"{'='*60}")
        
        success_count = sum(1 for _, _, status in results if status == 'success')
        print(f"✓ Thành công: {success_count}/{len(results)}")
        
        if success_count < len(results):
            print(f"\n⚠️  Lỗi:")
            for video, srt, status in results:
                if status != 'success':
                    print(f"  - {video.name}: {status}")


def main():
    """Ví dụ sử dụng"""
    
    # Kiểm tra API key
    if not os.environ.get('GEMINI_API_KEY'):
        print("⚠️  Chưa đặt GEMINI_API_KEY!")
        print("\nCách đặt:")
        print("  1. Tạo file .env trong thư mục này")
        print("  2. Thêm dòng: GEMINI_API_KEY=your_api_key_here")
        print("\nLấy API key tại: https://aistudio.google.com/apikey")
        sys.exit(1)
    
    generator = GeminiSRTGenerator()
    
    # Chọn chế độ
    print("Chọn chế độ:")
    print("1. Tạo SRT cho 1 video")
    print("2. Tạo SRT cho tất cả video trong thư mục")
    
    choice = input("\nNhập lựa chọn (1 hoặc 2): ").strip()
    
    if choice == '1':
        # Xử lý 1 video
        video_path = input("Đường dẫn video: ").strip()
        # Loại bỏ dấu ngoặc kép nếu có
        video_path = video_path.strip('"').strip("'")
        language = input("Ngôn ngữ (vi/en, mặc định vi): ").strip() or 'vi'
        
        generator.generate_srt_from_video(video_path, language=language)
        
    elif choice == '2':
        # Xử lý batch
        video_dir = input("Thư mục chứa video (mặc định: recordings): ").strip() or 'recordings'
        pattern = input("Pattern (mặc định: *.mp4): ").strip() or '*.mp4'
        language = input("Ngôn ngữ (vi/en, mặc định vi): ").strip() or 'vi'
        
        generator.batch_generate_srt(video_dir, pattern, language)
    
    else:
        print("Lựa chọn không hợp lệ!")


if __name__ == "__main__":
    main()
