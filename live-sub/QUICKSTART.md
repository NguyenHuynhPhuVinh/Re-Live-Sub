# ⚡ Quick Start - Live Sub

## 🚀 Chạy nhanh trong 3 bước

### 1️⃣ Cài đặt Backend

```bash
cd live-sub/backend
pip install -r requirements.txt
```

### 2️⃣ Tạo file .env

Tạo file `backend/.env`:

```
GEMINI_API_KEY=your_api_key_here
```

Lấy key tại: https://aistudio.google.com/apikey

### 3️⃣ Chạy ứng dụng

**Terminal 1 - Backend:**

```bash
cd live-sub/backend
python main.py
```

**Terminal 2 - Frontend:**

```bash
cd live-sub
npm install  # Chỉ lần đầu
npm run tauri dev
```

## ✅ Kiểm tra

- Backend chạy tại: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs
- App Tauri sẽ tự động mở

## 🎯 Sử dụng

1. Nhập URL YouTube livestream
2. Click "Bắt đầu ghi"
3. Video lưu trong `recordings/`
4. Chuyển tab "Video" để tạo phụ đề

## 📝 Lưu ý

- Cần FFmpeg và yt-dlp trong PATH
- Backend phải chạy trước khi mở app
- Video segment mặc định 60 giây (có thể thay đổi)

## 🐛 Lỗi thường gặp

**Backend không chạy:**

```bash
pip install fastapi uvicorn python-dotenv
```

**Không tìm thấy module:**

```bash
# Đảm bảo chạy từ đúng thư mục
cd live-sub/backend
python main.py
```

**Port 8000 bị chiếm:**

- Tắt ứng dụng đang dùng port 8000
- Hoặc đổi port trong `backend/main.py`

Xem thêm: [HUONG_DAN.md](./HUONG_DAN.md)
