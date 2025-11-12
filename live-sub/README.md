# 🎬 Live Sub - Hệ thống tự động ghi stream và tạo phụ đề

Ứng dụng desktop tự động ghi YouTube livestream, tạo phụ đề tiếng Việt bằng AI, và gắn phụ đề vào video.

## ✨ Tính năng

- 🎥 **Ghi stream tự động** - Tách thành segments, auto-reconnect khi mất kết nối
- 🤖 **Tạo phụ đề AI** - Dùng Google Gemini để transcribe và dịch sang tiếng Việt
- 🔗 **Gắn phụ đề** - Tự động merge subtitle vào video
- 💻 **Desktop App** - Giao diện đẹp với Tauri + React
- 🏗️ **Kiến trúc hiện đại** - FastAPI backend + Rust + React frontend

## 🚀 Quick Start

Xem [QUICKSTART.md](./QUICKSTART.md) để chạy nhanh trong 3 bước.

## 📖 Hướng dẫn chi tiết

Xem [HUONG_DAN.md](./HUONG_DAN.md) để biết thêm chi tiết.

## 🏗️ Kiến trúc

```
React UI (Tauri Desktop)
    ↓ Tauri IPC
Rust Layer (HTTP Client)
    ↓ REST API (http://127.0.0.1:8000)
Python FastAPI Backend
    ↓
Python Scripts (stream_recorder, generate_srt, merge_subtitle)
```

Xem [README_ARCHITECTURE.md](./README_ARCHITECTURE.md) để hiểu rõ hơn.

## 🛠️ Tech Stack

- **Frontend**: React 19 + TypeScript + Tailwind CSS + shadcn/ui
- **Desktop**: Tauri 2 (Rust)
- **Backend**: FastAPI (Python 3.8+)
- **Video**: FFmpeg + yt-dlp
- **AI**: Google Gemini API

## 📋 Yêu cầu

- Python 3.8+
- Node.js 18+
- Rust (cho Tauri)
- FFmpeg
- yt-dlp
- Google Gemini API key

## 📁 Cấu trúc dự án

```
live-sub/
├── backend/              # Python FastAPI backend
│   ├── api/             # API routes
│   ├── services/        # Business logic
│   └── main.py          # Entry point
├── src/                 # React frontend
│   ├── components/      # UI components
│   └── App.tsx          # Main app
├── src-tauri/           # Rust Tauri layer
│   └── src/lib.rs       # Tauri commands
└── [Python scripts]     # Original scripts (root)
```

## 🎯 Workflow

1. User nhập URL stream → React UI
2. Tauri gọi Rust command
3. Rust gọi FastAPI endpoint
4. FastAPI chạy Python script (stream_recorder.py)
5. Video được lưu vào `recordings/`
6. User click "Tạo phụ đề"
7. FastAPI chạy generate_srt.py với Gemini
8. File .srt được tạo
9. Tự động merge vào video → `processed/`

## 📝 API Endpoints

- `POST /api/stream/start` - Bắt đầu ghi stream
- `POST /api/stream/stop/{task_id}` - Dừng ghi
- `GET /api/stream/status/{task_id}` - Trạng thái
- `GET /api/stream/list` - Danh sách video
- `POST /api/processing/generate-srt` - Tạo phụ đề
- `POST /api/processing/merge-subtitle` - Gắn phụ đề

Xem API docs tại: http://127.0.0.1:8000/docs (khi backend chạy)

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Tạo issue hoặc pull request.

## 📄 License

MIT License

## 🙏 Credits

- [Tauri](https://tauri.app/) - Desktop framework
- [FastAPI](https://fastapi.tiangolo.com/) - Python web framework
- [Google Gemini](https://ai.google.dev/) - AI API
- [shadcn/ui](https://ui.shadcn.com/) - UI components
- [FFmpeg](https://ffmpeg.org/) - Video processing
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloader
