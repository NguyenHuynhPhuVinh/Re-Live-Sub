# 📦 Cài đặt Backend

## Yêu cầu

- Python 3.8 trở lên
- pip (Python package manager)

## Các bước cài đặt

### 1. Cài đặt dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Cài đặt FFmpeg

**Windows:**

- Tải từ: https://ffmpeg.org/download.html
- Giải nén và thêm vào PATH

**macOS:**

```bash
brew install ffmpeg
```

**Linux:**

```bash
sudo apt install ffmpeg
```

### 3. Cài đặt yt-dlp

```bash
pip install yt-dlp
```

Hoặc:

```bash
# Windows
winget install yt-dlp

# macOS
brew install yt-dlp

# Linux
sudo apt install yt-dlp
```

### 4. Tạo file .env

Tạo file `.env` trong thư mục `backend/`:

```
GEMINI_API_KEY=your_api_key_here
```

Lấy API key tại: https://aistudio.google.com/apikey

### 5. Kiểm tra cài đặt

```bash
# Kiểm tra Python
python --version

# Kiểm tra FFmpeg
ffmpeg -version

# Kiểm tra yt-dlp
yt-dlp --version

# Kiểm tra dependencies
pip list | grep fastapi
pip list | grep uvicorn
```

### 6. Chạy backend

```bash
python main.py
```

Backend sẽ chạy tại: http://127.0.0.1:8000

### 7. Kiểm tra API

Mở trình duyệt và truy cập:

- http://127.0.0.1:8000 - Health check
- http://127.0.0.1:8000/docs - API documentation (Swagger UI)
- http://127.0.0.1:8000/health - Health endpoint

## Cấu trúc thư mục

Sau khi chạy, các thư mục sau sẽ được tạo tự động:

- `recordings/` - Video đang ghi
- `recordings/temp/` - Video segments tạm
- `processed/` - Video đã xử lý

## Troubleshooting

### Lỗi: ModuleNotFoundError

```bash
pip install -r requirements.txt --upgrade
```

### Lỗi: Port 8000 đã được sử dụng

Đổi port trong `main.py`:

```python
uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
```

### Lỗi: GEMINI_API_KEY not found

Đảm bảo file `.env` nằm trong thư mục `backend/` và có nội dung:

```
GEMINI_API_KEY=your_actual_key_here
```

### Lỗi: FFmpeg not found

Thêm FFmpeg vào PATH:

- Windows: System Properties → Environment Variables → Path
- macOS/Linux: Thêm vào `~/.bashrc` hoặc `~/.zshrc`

## Development Mode

Chạy với auto-reload:

```bash
python main.py
# hoặc
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

## Production Mode

Chạy với nhiều workers:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Logs

Logs sẽ hiển thị trong terminal. Để lưu logs:

```bash
python main.py > backend.log 2>&1
```

## Cập nhật

Để cập nhật dependencies:

```bash
pip install -r requirements.txt --upgrade
```
