# HƯỚNG DẪN SỬ DỤNG HỆ THỐNG TỰ ĐỘNG

## 🚀 Khởi Động Nhanh

### Bước 1: Cài Đặt

```bash
pip install -r requirements.txt
```

### Bước 2: Cấu Hình API Key

1. Lấy Gemini API key tại: https://aistudio.google.com/apikey
2. Tạo file `.env` (copy từ `.env.example`)
3. Thêm API key vào file `.env`:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

### Bước 3: Khởi Động Hệ Thống

**Cách 1: Dùng script tự động (Windows)**

```bash
start_auto_system.bat
```

**Cách 2: Dùng Python (Cross-platform)**

```bash
python start_auto_system.py
```

**Cách 3: Chạy thủ công (2 terminal)**

Terminal 1 - Pipeline:

```bash
python auto_process_pipeline.py
```

Terminal 2 - Recorder:

```bash
python stream_recorder.py
```

---

## 📋 Quy Trình Hoạt Động

```
┌─────────────────────────────────────────────────────────────┐
│  1. STREAM RECORDER                                         │
│     - Ghi stream YouTube                                    │
│     - Lưu vào: recordings/temp/video_001.mp4 (đang ghi)   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  2. HOÀN THÀNH GHI                                          │
│     - Di chuyển: recordings/video_001.mp4                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  3. AUTO PIPELINE PHÁT HIỆN                                 │
│     - Theo dõi thư mục recordings/                          │
│     - Phát hiện video mới                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  4. TẠO PHỤ ĐỀ                                              │
│     - Gọi Gemini API                                        │
│     - Tạo: recordings/video_001.srt                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  5. GẮNPHỤ ĐỀ                                              │
│     - Dùng FFmpeg burn subtitle                             │
│     - Tạo: recordings/video_001_sub.mp4                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  6. DI CHUYỂN VÀO PROCESSED                                 │
│     - processed/video_001_sub.mp4 (video có phụ đề)        │
│     - processed/video_001.srt (file phụ đề)                │
│     - processed/original_video_001.mp4 (video gốc)         │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Cấu Trúc Thư Mục

```
project/
├── recordings/              # Thư mục chứa video hoàn chỉnh
│   ├── temp/               # Video đang được ghi (không xử lý)
│   │   └── stream_001.mp4  # Đang ghi...
│   └── stream_000.mp4      # Hoàn thành, chờ xử lý
│
├── processed/              # Video đã xử lý xong
│   ├── stream_000_sub.mp4  # Video có phụ đề
│   ├── stream_000.srt      # File phụ đề
│   └── original_stream_000.mp4  # Video gốc
│
├── auto_process_pipeline.py  # Pipeline tự động
├── stream_recorder.py        # Ghi stream
├── generate_srt.py          # Tạo phụ đề
├── merge_subtitle.py        # Gắn phụ đề
└── .env                     # API keys
```

---

## ⚙️ Cấu Hình

### Stream Recorder

Khi chạy `stream_recorder.py`, bạn sẽ được hỏi:

1. **Chế độ ghi:**

   - `1` = Copy Stream (nhanh, giữ nguyên chất lượng)
   - `2` = Enhance Quality (chậm hơn, re-encode 10 Mbps)

2. **YouTube URL:**

   - Nhập URL livestream YouTube

3. **Tên stream:**
   - Nhập tên hoặc Enter để dùng timestamp

### Auto Pipeline

Khi chạy `auto_process_pipeline.py`, bạn sẽ được hỏi:

1. **Thư mục video hoàn chỉnh:** (mặc định: `recordings`)
2. **Thư mục temp:** (mặc định: `recordings/temp`)
3. **Thư mục output:** (mặc định: `processed`)
4. **Ngôn ngữ phụ đề:** `vi` hoặc `en` (mặc định: `vi`)
5. **Burn subtitle:** `y` hoặc `n` (mặc định: `y`)
6. **Thời gian chờ file ổn định:** giây (mặc định: `10`)

---

## 💡 Tips & Tricks

### 1. Xử Lý Video Có Sẵn

Pipeline tự động xử lý cả video có sẵn trong thư mục `recordings`:

```bash
# Đặt video vào recordings/
cp my_video.mp4 recordings/

# Chạy pipeline
python auto_process_pipeline.py

# Pipeline sẽ tự động:
# 1. Tạo SRT
# 2. Gắn phụ đề
# 3. Di chuyển vào processed/
```

### 2. Chạy Riêng Từng Bước

Nếu không muốn dùng pipeline tự động:

```bash
# Bước 1: Ghi stream
python stream_recorder.py

# Bước 2: Tạo SRT
python generate_srt.py

# Bước 3: Gắn phụ đề
python merge_subtitle.py
```

### 3. Tùy Chỉnh Style Phụ Đề

Sửa trong `merge_subtitle.py`:

```python
subtitle_style = {
    'font': 'Arial',
    'size': 28,
    'color': '&H00FFFFFF',  # Trắng
    'outline': '&H00000000',  # Viền đen
    'bold': True
}
```

### 4. Xử Lý Batch

```bash
# Tạo SRT cho tất cả video
python generate_srt.py
# Chọn chế độ 2

# Gắn phụ đề cho tất cả video
python merge_subtitle.py
# Chọn chế độ 2
```

---

## 🐛 Xử Lý Lỗi

### Lỗi: "Chưa đặt GEMINI_API_KEY"

**Giải pháp:**

1. Tạo file `.env`
2. Thêm: `GEMINI_API_KEY=your_key_here`

### Lỗi: "FFmpeg chưa được cài đặt"

**Giải pháp:**

1. Tải FFmpeg: https://ffmpeg.org/download.html
2. Thêm FFmpeg vào PATH

### Lỗi: "yt-dlp không tìm thấy stream"

**Giải pháp:**

1. Kiểm tra URL có đúng không
2. Kiểm tra stream có đang live không
3. Update yt-dlp: `pip install -U yt-dlp`

### Pipeline không xử lý video

**Kiểm tra:**

1. Video có trong `recordings/` không? (không phải `recordings/temp/`)
2. Video có đuôi `.mp4`, `.mkv`, `.avi`, `.mov` không?
3. Tên video có chứa `_sub` không? (sẽ bị bỏ qua)

---

## 📊 Giám Sát

### Xem Log Pipeline

Pipeline sẽ hiển thị:

- ✅ Video được phát hiện
- 📝 Đang tạo SRT
- 🔗 Đang gắn phụ đề
- 📦 Đang di chuyển file
- ✅ Hoàn thành

### Xem Log Recorder

Recorder sẽ hiển thị:

- 🎥 Đang ghi stream
- ✓ Đã tạo segment #1, #2, #3...
- 🔄 Reconnecting (nếu mất kết nối)
- 📦 Di chuyển file từ temp

---

## 🎯 Workflow Khuyến Nghị

### Cho Stream Dài (> 1 giờ)

1. Chạy pipeline trước
2. Chạy recorder với segment 5 phút
3. Pipeline sẽ tự động xử lý từng segment khi hoàn thành

### Cho Video Ngắn (< 30 phút)

1. Ghi toàn bộ video trước
2. Chạy pipeline sau để xử lý

### Cho Nhiều Stream

1. Chạy 1 pipeline
2. Chạy nhiều recorder (mỗi stream 1 terminal)
3. Pipeline xử lý tất cả video theo thứ tự

---

## 📞 Hỗ Trợ

Nếu gặp vấn đề:

1. Kiểm tra log trong terminal
2. Kiểm tra file `.env` có đúng không
3. Kiểm tra FFmpeg đã cài đặt chưa
4. Kiểm tra yt-dlp đã update chưa

---

## 🔄 Cập Nhật

```bash
# Cập nhật dependencies
pip install -U -r requirements.txt

# Cập nhật yt-dlp
pip install -U yt-dlp
```

---

**Chúc bạn sử dụng hiệu quả! 🎉**
