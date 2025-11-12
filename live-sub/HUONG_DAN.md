# 🚀 Hướng dẫn sử dụng Live Sub

## 📋 Yêu cầu hệ thống

1. **Python 3.8+** - Để chạy backend
2. **Node.js 18+** - Để build frontend
3. **Rust** - Để build Tauri app
4. **FFmpeg** - Để xử lý video
5. **yt-dlp** - Để download stream

## 🔧 Cài đặt

### Bước 1: Cài đặt Backend

```bash
cd live-sub/backend
pip install -r requirements.txt
```

### Bước 2: Cấu hình API Key

Tạo file `.env` trong thư mục `backend/`:

```
GEMINI_API_KEY=your_api_key_here
```

Lấy API key tại: https://aistudio.google.com/apikey

### Bước 3: Cài đặt Frontend

```bash
cd live-sub
npm install
```

## ▶️ Chạy ứng dụng

### Cách 1: Chạy thủ công (Development)

**Terminal 1 - Backend:**

```bash
cd live-sub/backend
python main.py
```

**Terminal 2 - Frontend:**

```bash
cd live-sub
npm run tauri dev
```

### Cách 2: Dùng file batch (Windows)

Double-click file `START_BACKEND.bat` để chạy backend, sau đó chạy:

```bash
npm run tauri dev
```

## 📖 Cách sử dụng

### 1. Ghi Stream

1. Mở tab **"📹 Ghi Stream"**
2. Nhập URL YouTube livestream
3. Chọn độ dài mỗi segment (mặc định 60 giây)
4. Click **"Bắt đầu ghi"**
5. Video sẽ được lưu vào thư mục `recordings/`

### 2. Tạo phụ đề

1. Chuyển sang tab **"📁 Video"**
2. Chọn video cần tạo phụ đề
3. Click **"Tạo phụ đề"**
4. Đợi Gemini AI xử lý (có thể mất vài phút)
5. File `.srt` sẽ được tạo cùng thư mục với video

### 3. Xem kết quả

- Video gốc: `recordings/`
- Video đã xử lý: `processed/`
- File phụ đề: `.srt` cùng tên với video

## 🏗️ Kiến trúc

```
React UI (Tauri Desktop)
    ↓ Tauri IPC
Rust Layer (HTTP Client)
    ↓ REST API
Python FastAPI Backend
    ↓
Python Scripts (stream_recorder, generate_srt, etc.)
```

## 🐛 Xử lý lỗi

### Backend không chạy

- Kiểm tra Python đã cài đặt: `python --version`
- Kiểm tra dependencies: `pip install -r requirements.txt`
- Kiểm tra port 8000 có bị chiếm không

### Không tạo được phụ đề

- Kiểm tra GEMINI_API_KEY trong file `.env`
- Kiểm tra kết nối internet
- Xem log trong terminal backend

### Không ghi được stream

- Kiểm tra FFmpeg: `ffmpeg -version`
- Kiểm tra yt-dlp: `yt-dlp --version`
- Kiểm tra URL stream có hợp lệ không

## 📚 Tài liệu thêm

- [README_ARCHITECTURE.md](./README_ARCHITECTURE.md) - Chi tiết kiến trúc
- [FastAPI Docs](http://127.0.0.1:8000/docs) - API documentation (khi backend chạy)

## 💡 Tips

1. **Segment duration**: Đặt 60-300 giây tùy nhu cầu
2. **Gemini API**: Free tier có giới hạn, cân nhắc upgrade nếu dùng nhiều
3. **Disk space**: Video chiếm nhiều dung lượng, dọn dẹp thường xuyên
4. **Performance**: Backend và frontend nên chạy trên SSD để tốc độ tốt hơn

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Tạo issue hoặc pull request trên GitHub.
