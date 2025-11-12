# YouTube Stream Recorder & SRT Generator

Công cụ ghi stream YouTube và tự động tạo phụ đề SRT bằng Gemini AI.

## Tính năng

1. **Stream Recorder** (`stream_recorder.py`): Ghi YouTube livestream thành các đoạn video 5 phút
2. **SRT Generator** (`generate_srt.py`): Tạo file phụ đề SRT từ video bằng Gemini API
3. **SRT Validator** (`validate_srt.py`): Kiểm tra và sửa lỗi file SRT
4. **Subtitle Merger** (`merge_subtitle.py`): Ghép phụ đề SRT vào video bằng FFmpeg
5. **YouTube Live Streamer** (`stream_to_youtube.py`): Phát trực tiếp video lên YouTube Live
6. **YouTube Uploader** (`upload_youtube.py`): Upload video lên YouTube (private/unlisted/public)

## Cài đặt

```bash
pip install -r requirements.txt
```

## Sử dụng

### 1. Ghi Stream YouTube

```python
python stream_recorder.py
```

Hoặc tùy chỉnh:

```python
from stream_recorder import YouTubeStreamRecorder

recorder = YouTubeStreamRecorder(
    output_dir="recordings",
    segment_duration=300  # 5 phút
)

recorder.record_stream(
    "https://www.youtube.com/watch?v=VIDEO_ID",
    stream_name="my_stream"
)

# Hoặc với enhance quality (re-encode bitrate cao hơn)
recorder_hq = YouTubeStreamRecorder(
    output_dir="recordings",
    segment_duration=300,
    enhance_quality=True  # Re-encode với 10 Mbps
)
recorder_hq.record_stream(
    "https://www.youtube.com/watch?v=VIDEO_ID",
    stream_name="my_stream_hq"
)
```

### 2. Tạo Phụ Đề SRT

**Bước 1: Đặt API Key**

Lấy API key tại: https://aistudio.google.com/apikey

Tạo file `.env` trong thư mục project:

```bash
# Copy file mẫu
copy .env.example .env

# Sửa file .env và thêm API key của bạn
GEMINI_API_KEY=your_api_key_here
```

**Bước 2: Chạy script**

```bash
python generate_srt.py
```

Chọn chế độ:

- **Chế độ 1**: Tạo SRT cho 1 video
- **Chế độ 2**: Tạo SRT cho tất cả video trong thư mục

**Sử dụng trong code:**

```python
from generate_srt import GeminiSRTGenerator

generator = GeminiSRTGenerator()

# Tạo SRT cho 1 video
generator.generate_srt_from_video(
    "recordings/test_stream_000.mp4",
    language='vi'  # hoặc 'en'
)

# Tạo SRT cho tất cả video
generator.batch_generate_srt(
    video_dir="recordings",
    pattern="*.mp4",
    language='vi'
)
```

### 3. Kiểm Tra File SRT

```bash
python validate_srt.py
```

Chọn chế độ:

- **Chế độ 1**: Kiểm tra 1 file SRT
- **Chế độ 2**: Kiểm tra tất cả file SRT trong thư mục

**Tính năng:**

- Kiểm tra định dạng timestamp (HH:MM:SS,mmm)
- Kiểm tra số thứ tự subtitle
- Kiểm tra logic thời gian (start < end)
- Cảnh báo phụ đề quá dài
- Tự động sửa lỗi (optional)

**Sử dụng trong code:**

```python
from validate_srt import SRTValidator

validator = SRTValidator()

# Kiểm tra 1 file
is_valid, fixed_content = validator.validate_file(
    "recordings/test_stream_000.srt",
    fix=True  # Tự động sửa lỗi
)

# Kiểm tra tất cả file
validator.batch_validate(
    directory="recordings",
    pattern="*.srt",
    fix=True
)
```

### 4. Ghép Phụ Đề Vào Video

```bash
python merge_subtitle.py
```

Chọn chế độ:

- **Chế độ 1**: Ghép phụ đề cho 1 video
- **Chế độ 2**: Ghép phụ đề cho tất cả video trong thư mục

**Kiểu phụ đề:**

- **Burn-in**: Phụ đề cố định, không thể tắt (khuyến nghị cho upload)
- **Embed**: Phụ đề có thể bật/tắt trong trình phát

**Sử dụng trong code:**

```python
from merge_subtitle import SubtitleMerger

merger = SubtitleMerger()

# Ghép phụ đề cho 1 video (burn-in)
merger.merge_subtitle(
    "recordings/test_stream_000.mp4",
    burn_in=True
)

# Ghép phụ đề với style tùy chỉnh
merger.merge_subtitle(
    "recordings/test_stream_000.mp4",
    subtitle_style={
        'font': 'Arial',
        'size': 28,
        'color': '&H00FFFFFF',  # Trắng
        'outline': '&H00000000',  # Viền đen
        'bold': True
    },
    burn_in=True
)

# Ghép phụ đề cho tất cả video
merger.batch_merge(
    video_dir="recordings",
    pattern="*.mp4",
    burn_in=True
)
```

## Định dạng SRT

File SRT được tạo theo chuẩn:

```
1
00:00:00,000 --> 00:00:05,000
Dòng phụ đề đầu tiên

2
00:00:05,000 --> 00:00:10,000
Dòng phụ đề thứ hai
```

### 5. Stream Video Lên YouTube Live

**Setup Stream Key:**

1. Vào [YouTube Studio](https://studio.youtube.com)
2. Chọn **Go Live** → **Stream**
3. Copy **Stream key** (giữ bí mật!)
4. Thêm vào file `.env`:
   ```
   YOUTUBE_STREAM_KEY=your_stream_key_here
   ```

**Chạy script:**

```bash
python stream_to_youtube.py
```

**Tính năng:**

- Stream 1 video hoặc playlist
- Loop video/playlist vô hạn
- Tự động encode phù hợp cho YouTube (1080p, 4.5 Mbps)
- Stream ở chế độ riêng tư (đổi sang Public trong YouTube Studio)

**Sử dụng trong code:**

```python
from stream_to_youtube import YouTubeLiveStreamer

streamer = YouTubeLiveStreamer(stream_key="your_key")

# Stream 1 video
streamer.stream_video(
    "recordings/test_stream_000_sub.mp4",
    loop=True  # Loop vô hạn
)

# Stream playlist
streamer.stream_playlist(
    video_dir="recordings",
    pattern="*_sub.mp4",
    loop=True  # Loop playlist
)
```

## Lưu ý

- Video dài hơn 1 phút nên tải lên qua File API (script đã tự động xử lý)
- Gemini hỗ trợ video tối đa 2 giờ (cửa sổ ngữ cảnh 2M)
- Mỗi giây video tiêu tốn ~300 tokens
- Hỗ trợ định dạng: MP4, MPEG, MOV, AVI, FLV, MPG, WEBM, WMV, 3GPP

## Yêu cầu

- Python 3.7+
- FFmpeg (cho stream recorder)
- yt-dlp
- google-genai
- Gemini API key

## License

MIT
