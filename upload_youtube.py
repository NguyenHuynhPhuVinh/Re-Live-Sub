"""
YouTube Video Uploader - Upload video lên YouTube với OAuth2
Yêu cầu: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
"""

import os
import sys
import pickle
from pathlib import Path
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError


# Scopes cần thiết cho YouTube upload
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']


class YouTubeUploader:
    def __init__(self, credentials_file='client_secrets.json'):
        """
        Args:
            credentials_file: File JSON chứa OAuth2 credentials từ Google Cloud Console
        """
        self.credentials_file = credentials_file
        self.token_file = 'youtube_token.pickle'
        self.youtube = None
        
        self._authenticate()
    
    def _authenticate(self):
        """Xác thực với YouTube API"""
        creds = None
        
        # Kiểm tra token đã lưu
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # Nếu không có token hoặc token hết hạn
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("🔄 Đang refresh token...")
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    print(f"❌ Không tìm thấy file credentials: {self.credentials_file}")
                    print("\n📝 Hướng dẫn lấy credentials:")
                    print("1. Vào https://console.cloud.google.com/")
                    print("2. Tạo project mới hoặc chọn project có sẵn")
                    print("3. Enable YouTube Data API v3")
                    print("4. Tạo OAuth 2.0 Client ID (Desktop app)")
                    print("5. Download JSON và đặt tên 'client_secrets.json'")
                    sys.exit(1)
                
                print("🔐 Đang xác thực với Google...")
                print("Trình duyệt sẽ mở, vui lòng đăng nhập và cho phép quyền truy cập")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Lưu token
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
            print("✓ Đã lưu token xác thực")
        
        # Tạo YouTube service
        self.youtube = build('youtube', 'v3', credentials=creds)
        print("✓ Đã kết nối YouTube API")
    
    def upload_video(self, video_path, title=None, description="", 
                     category="22", privacy="private", tags=None):
        """
        Upload video lên YouTube
        
        Args:
            video_path: Đường dẫn video
            title: Tiêu đề video (mặc định: tên file)
            description: Mô tả video
            category: Category ID (22 = People & Blogs, 20 = Gaming)
            privacy: "public", "private", hoặc "unlisted"
            tags: List các tag
        
        Returns:
            Video ID nếu thành công
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            raise FileNotFoundError(f"Không tìm thấy video: {video_path}")
        
        # Tiêu đề mặc định
        if title is None:
            title = video_path.stem
        
        # Tags mặc định
        if tags is None:
            tags = []
        
        print(f"\n📤 Đang upload video...")
        print(f"📹 File: {video_path.name}")
        print(f"📝 Tiêu đề: {title}")
        print(f"🔒 Privacy: {privacy}")
        
        # Metadata
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': category
            },
            'status': {
                'privacyStatus': privacy,
                'selfDeclaredMadeForKids': False
            }
        }
        
        # Upload file
        media = MediaFileUpload(
            str(video_path),
            chunksize=1024*1024,  # 1MB chunks
            resumable=True
        )
        
        try:
            request = self.youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )
            
            response = None
            last_progress = 0
            
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    if progress != last_progress:
                        print(f"\r⏳ Upload: {progress}%", end='', flush=True)
                        last_progress = progress
            
            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            print(f"\n✓ Upload thành công!")
            print(f"🎬 Video ID: {video_id}")
            print(f"🔗 URL: {video_url}")
            
            return video_id
            
        except HttpError as e:
            print(f"\n❌ Lỗi HTTP: {e}")
            return None
        except Exception as e:
            print(f"\n❌ Lỗi: {e}")
            return None
    
    def batch_upload(self, video_dir, pattern="*_sub.mp4", privacy="private",
                     title_prefix="", description_template=""):
        """
        Upload nhiều video cùng lúc
        
        Args:
            video_dir: Thư mục chứa video
            pattern: Pattern để tìm video
            privacy: Privacy setting
            title_prefix: Prefix cho tiêu đề
            description_template: Template mô tả
        """
        video_dir = Path(video_dir)
        video_files = sorted(video_dir.glob(pattern))
        
        if not video_files:
            print(f"⚠️  Không tìm thấy video nào trong {video_dir}")
            return
        
        print(f"📹 Tìm thấy {len(video_files)} video")
        print(f"🔒 Privacy: {privacy}\n")
        
        results = []
        for i, video_path in enumerate(video_files, 1):
            print(f"\n{'='*60}")
            print(f"[{i}/{len(video_files)}]")
            print(f"{'='*60}")
            
            # Tạo tiêu đề
            title = f"{title_prefix}{video_path.stem}".strip()
            
            # Tạo mô tả
            description = description_template.format(
                filename=video_path.name,
                date=datetime.now().strftime("%Y-%m-%d")
            )
            
            try:
                video_id = self.upload_video(
                    video_path,
                    title=title,
                    description=description,
                    privacy=privacy
                )
                
                if video_id:
                    results.append((video_path, video_id, 'success'))
                else:
                    results.append((video_path, None, 'failed'))
                    
            except Exception as e:
                print(f"✗ Lỗi: {e}")
                results.append((video_path, None, f'error: {e}'))
        
        # Tổng kết
        print(f"\n{'='*60}")
        print(f"📊 TỔNG KẾT")
        print(f"{'='*60}")
        
        success_count = sum(1 for _, _, status in results if status == 'success')
        print(f"✓ Thành công: {success_count}/{len(results)}")
        
        if success_count > 0:
            print(f"\n🎬 Video đã upload:")
            for video_path, video_id, status in results:
                if status == 'success':
                    print(f"  • {video_path.name}")
                    print(f"    https://www.youtube.com/watch?v={video_id}")
        
        if success_count < len(results):
            print(f"\n⚠️  Lỗi:")
            for video_path, _, status in results:
                if status != 'success':
                    print(f"  - {video_path.name}: {status}")


def main():
    """Ví dụ sử dụng"""
    
    print("YouTube Video Uploader")
    print("="*60)
    
    # Kiểm tra credentials
    if not os.path.exists('client_secrets.json'):
        print("\n⚠️  Chưa có file 'client_secrets.json'!")
        print("\n📝 Hướng dẫn setup:")
        print("1. Vào https://console.cloud.google.com/")
        print("2. Tạo project mới")
        print("3. Enable 'YouTube Data API v3'")
        print("4. Tạo OAuth 2.0 Client ID (Desktop app)")
        print("5. Download JSON và đổi tên thành 'client_secrets.json'")
        print("6. Đặt file trong thư mục này")
        sys.exit(1)
    
    uploader = YouTubeUploader()
    
    print("\nChọn chế độ:")
    print("1. Upload 1 video")
    print("2. Upload nhiều video")
    
    choice = input("\nNhập lựa chọn (1 hoặc 2): ").strip()
    
    if choice == '1':
        # Upload 1 video
        video_path = input("Đường dẫn video: ").strip().strip('"').strip("'")
        title = input("Tiêu đề (Enter để dùng tên file): ").strip() or None
        description = input("Mô tả (optional): ").strip()
        
        print("\nChọn privacy:")
        print("1. Private (riêng tư)")
        print("2. Unlisted (không công khai)")
        print("3. Public (công khai)")
        privacy_choice = input("Nhập lựa chọn (1, 2 hoặc 3, mặc định 1): ").strip() or '1'
        
        privacy_map = {'1': 'private', '2': 'unlisted', '3': 'public'}
        privacy = privacy_map.get(privacy_choice, 'private')
        
        uploader.upload_video(
            video_path,
            title=title,
            description=description,
            privacy=privacy
        )
        
    elif choice == '2':
        # Upload batch
        video_dir = input("Thư mục chứa video (mặc định: recordings): ").strip() or 'recordings'
        pattern = input("Pattern (mặc định: *_sub.mp4): ").strip() or '*_sub.mp4'
        title_prefix = input("Prefix cho tiêu đề (optional): ").strip()
        
        print("\nChọn privacy:")
        print("1. Private (riêng tư)")
        print("2. Unlisted (không công khai)")
        print("3. Public (công khai)")
        privacy_choice = input("Nhập lựa chọn (1, 2 hoặc 3, mặc định 1): ").strip() or '1'
        
        privacy_map = {'1': 'private', '2': 'unlisted', '3': 'public'}
        privacy = privacy_map.get(privacy_choice, 'private')
        
        description = input("Mô tả (optional): ").strip()
        
        uploader.batch_upload(
            video_dir,
            pattern=pattern,
            privacy=privacy,
            title_prefix=title_prefix,
            description_template=description
        )
    
    else:
        print("Lựa chọn không hợp lệ!")


if __name__ == "__main__":
    main()
