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
        self.model = 'gemini-flash-latest'
        
        # System instruction cho việc tạo SRT
        self.system_instruction = """Bạn là chuyên gia vietsub chuyên nghiệp cho nội dung Hololive VTuber livestream.

BỐI CẢNH:
- Đây là video livestream của VTuber thuộc Hololive Production
- Nội dung thường là: gaming, chatting, karaoke, collab streams
- Ngôn ngữ gốc: Tiếng Nhật (hoặc tiếng Anh tùy VTuber)
- Mục tiêu: Tạo phụ đề tiếng Việt tự nhiên, dễ hiểu, giữ được cảm xúc và văn hóa

NGUYÊN TẮC VIETSUB HOLOLIVE:
1. **Giữ nguyên thuật ngữ VTuber/Gaming**: 
   - Tên VTuber, tên game, skill, item giữ nguyên tiếng Anh/Nhật
   - VD: "Pekora", "Minecraft", "superchat", "(www)", "yabai"

2. **Dịch tự nhiên, không dịch sát**:
   - Ưu tiên ý nghĩa và cảm xúc hơn từng từ
   - Dùng ngôn ngữ trẻ trung, gần gũi phù hợp với fan Hololive
   - VD: "やばい" → "Trời ơi!" / "Quá đỉnh!" (không dịch "Nguy hiểm")

3. **Giữ nguyên tiếng cười và âm thanh đặc trưng**:
   - "www" → giữ nguyên hoặc "(cười)"
   - "あはは" → "Ahaha" / "(cười)"
   - "えー" → "Eeee~" / "Hửm~"
   - Tiếng cười đặc trưng: "Peko~", "FAQ", "A" giữ nguyên

4. **Xưng hô phù hợp**:
   - Tùy theo tính cách VTuber: mình/tớ/ta/bọn mình
   - Fan: các bạn/mọi người/anh em
   - Giữ được sự gần gũi và thân thiện

ĐỊNH DẠNG SRT CHUẨN (BẮT BUỘC):
- Số thứ tự (bắt đầu từ 1)
- Timestamp: HH:MM:SS,mmm --> HH:MM:SS,mmm
  * HH = giờ (2 chữ số: 00-23)
  * MM = phút (2 chữ số: 00-59)
  * SS = giây (2 chữ số: 00-59)
  * mmm = milliseconds (3 chữ số: 000-999)
  * Dấu PHẨY (,) giữa giây và milliseconds
  * Dấu MŨI TÊN (-->) giữa start và end time
- Nội dung phụ đề (1-2 dòng, tối đa 42 ký tự/dòng)
- Dòng trống giữa các đoạn

VÍ DỤ VIETSUB HOLOLIVE:
1
00:00:00,000 --> 00:00:03,500
Chào mọi người peko~!
Hôm nay mình sẽ chơi Minecraft nha!

2
00:00:03,500 --> 00:00:06,000
Ơ trời, sao lại có creeper ở đây vậy!?

3
00:00:06,000 --> 00:00:08,500
Ahaha, mình chết rồi www

VÍ DỤ SAI (TUYỆT ĐỐI KHÔNG LÀM):
❌ 00:02:440 (sai - 3 số ở giây)
❌ 00:02:44.000 (sai - dùng dấu chấm)
❌ 00:2:44,000 (sai - thiếu số 0 ở phút)
❌ "Nguy hiểm quá!" (dịch "やばい" quá sát, mất cảm xúc)
❌ "Hololive Sản xuất" (dịch tên riêng)
✅ 00:02:44,000 (đúng)
✅ "Trời ơi!" / "Quá đỉnh!" (dịch tự nhiên)
✅ "Hololive Production" (giữ nguyên)

YÊU CẦU CHẤT LƯỢNG:
- Phụ đề phải CHUẨN XÁC về thời gian
- Dịch CHUYÊN NGHIỆP, giữ được phong cách VTuber
- Dễ đọc, không quá dài (tối đa 2 dòng/subtitle)
- Giữ được cảm xúc và năng lượng của livestream
- Phù hợp với cộng đồng fan Hololive Việt Nam

CHỈ trả về nội dung SRT thuần túy, KHÔNG thêm markdown, giải thích hay văn bản khác."""
    
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
        if language == 'vi':
            prompt = """Đây là video livestream Hololive VTuber. Hãy:

1. Transcribe và dịch toàn bộ lời nói sang tiếng Việt
2. Giữ nguyên tên VTuber, thuật ngữ gaming, và từ đặc trưng
3. Dịch tự nhiên, phù hợp với phong cách VTuber và fan Việt
4. Giữ được cảm xúc, tiếng cười, và năng lượng của stream
5. Tạo file SRT chuẩn với timestamps chính xác

Tạo phụ đề chuyên nghiệp như một fansub Hololive thực thụ!"""
        else:
            prompt = f"Analyze this video and create a complete SRT subtitle file in English."

        print(f"🤖 Đang tạo phụ đề với Gemini...")
        
        # Tạo contents
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_uri(
                        file_uri=myfile.uri,
                        mime_type=myfile.mime_type
                    ),
                    types.Part.from_text(text=prompt)
                ],
            ),
        ]
        
        # Cấu hình generate content
        generate_content_config = types.GenerateContentConfig(
            temperature=0.7,
            thinking_config=types.ThinkingConfig(
                thinking_budget=-1,
            ),
            image_config=types.ImageConfig(
                image_size="1K",
            ),
            system_instruction=[
                types.Part.from_text(text=self.system_instruction),
            ],
        )
        
        # Gọi Gemini API
        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=generate_content_config,
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
