# Live Sub - Kiến trúc hệ thống

## 🏗️ Tổng quan kiến trúc

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│              (Tauri Desktop App UI)                      │
└────────────────────┬────────────────────────────────────┘
                     │ Tauri IPC
┌────────────────────▼────────────────────────────────────┐
│                  Rust Tauri Layer                        │
│           (Gọi HTTP API đến Backend)                     │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP REST API
┌────────────────────▼────────────────────────────────────┐
│              Python FastAPI Backend                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │  API Routes                                      │   │
│  │  - /api/stream/*    (Ghi stream)                │   │
│  │  - /api/processing/* (Xử lý video)              │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Services                                        │   │
│  │  - StreamService (stream_recorder.py)           │   │
│  │  - ProcessingService (generate_srt.py)          │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 📁 Cấu trúc thư mục

```
live-sub/
├── backend/                    # Python FastAPI Backend
│   ├── api/
│   │   ├── stream.py          # API routes cho stream recording
│   │   └── processing.py      # API routes cho video processing
│   ├── services/
│   │   ├── stream_service.py  # Business logic ghi stream
│   │   └── processing_service.py # Business logic xử lý video
│   ├── main.py                # FastAPI app entry point
│   └── requirements.txt       # Python dependencies
│
├── src/                       # React Frontend
│   ├── components/
│   │   ├── StreamRecorder.tsx # UI ghi stream
│   │   ├── VideoList.tsx      # Danh sách video
│   │   └── ui/                # shadcn/ui components
│   ├── lib/
│   │   └── utils.ts           # Utilities
│   └── App.tsx                # Main app component
│
├── src-tauri/                 # Rust Tauri
│   ├── src/
│   │   └── lib.rs             # Tauri commands (gọi API)
│   └── Cargo.toml             # Rust dependencies
│
└── [Python scripts gốc ở root] # Được import vào backend
```

## 🔄 Luồng hoạt động

### 1. Ghi Stream

```
User nhập URL → React UI → Tauri Command → FastAPI /api/stream/start
→ StreamService → YouTubeStreamRecorder (Python) → Ghi video vào recordings/
```

### 2. Tạo phụ đề

```
User chọn video → React UI → Tauri Command → FastAPI /api/processing/generate-srt
→ ProcessingService → GeminiSRTGenerator (Python) → Tạo file .srt
```

### 3. Gắn phụ đề

```
User chọn merge → React UI → Tauri Command → FastAPI /api/processing/merge-subtitle
→ ProcessingService → SubtitleMerger (Python) → Video có phụ đề
```

## 🚀 Cách chạy

### 1. Cài đặt Backend

```bash
cd live-sub/backend
pip install -r requirements.txt
```

### 2. Tạo file .env

```bash
# Trong thư mục live-sub/backend/
GEMINI_API_KEY=your_api_key_here
```

### 3. Chạy Backend

```bash
cd live-sub/backend
python main.py
# Backend chạy tại http://127.0.0.1:8000
```

### 4. Chạy Frontend (Terminal khác)

```bash
cd live-sub
npm install
npm run tauri dev
```

## 🔧 API Endpoints

### Stream Recording

- `POST /api/stream/start` - Bắt đầu ghi stream
- `POST /api/stream/stop/{task_id}` - Dừng ghi stream
- `GET /api/stream/status/{task_id}` - Lấy trạng thái
- `GET /api/stream/list` - Danh sách video đã ghi

### Video Processing

- `POST /api/processing/generate-srt` - Tạo file SRT
- `POST /api/processing/merge-subtitle` - Gắn phụ đề
- `GET /api/processing/status/{task_id}` - Trạng thái xử lý
- `GET /api/processing/list-processed` - Video đã xử lý

## 🛠️ Tech Stack

- **Frontend**: React 19 + TypeScript + Tailwind CSS + shadcn/ui
- **Desktop**: Tauri 2 (Rust)
- **Backend**: FastAPI (Python)
- **Video**: FFmpeg + yt-dlp
- **AI**: Google Gemini API

## 📝 Lưu ý

1. Backend phải chạy trước khi mở app Tauri
2. Cần có FFmpeg và yt-dlp trong PATH
3. Cần GEMINI_API_KEY trong file .env
4. Video được lưu trong thư mục `recordings/`
5. Video đã xử lý trong thư mục `processed/`
