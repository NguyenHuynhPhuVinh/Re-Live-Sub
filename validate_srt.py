"""
SRT Validator - Kiểm tra và sửa lỗi file SRT
"""

import re
import sys
from pathlib import Path
from datetime import timedelta


class SRTValidator:
    def __init__(self):
        """Khởi tạo SRT Validator"""
        self.errors = []
        self.warnings = []
    
    def validate_file(self, srt_path, fix=False):
        """
        Kiểm tra file SRT
        
        Args:
            srt_path: Đường dẫn file SRT
            fix: True = tự động sửa lỗi, False = chỉ báo lỗi
        
        Returns:
            (is_valid, fixed_content)
        """
        srt_path = Path(srt_path)
        
        if not srt_path.exists():
            raise FileNotFoundError(f"Không tìm thấy file: {srt_path}")
        
        print(f"📝 Đang kiểm tra: {srt_path.name}")
        
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.errors = []
        self.warnings = []
        
        # Parse SRT
        subtitles = self._parse_srt(content)
        
        if not subtitles:
            self.errors.append("File SRT rỗng hoặc không đúng định dạng")
            return False, None
        
        # Validate từng subtitle
        for i, sub in enumerate(subtitles, 1):
            self._validate_subtitle(i, sub)
        
        # Hiển thị kết quả
        self._print_results()
        
        # Sửa lỗi nếu cần
        fixed_content = None
        if fix and (self.errors or self.warnings):
            print(f"\n🔧 Đang sửa lỗi...")
            fixed_content = self._fix_subtitles(subtitles)
            
            # Lưu file đã sửa
            backup_path = srt_path.with_suffix('.srt.bak')
            srt_path.rename(backup_path)
            print(f"💾 Đã backup file gốc: {backup_path.name}")
            
            with open(srt_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"✓ Đã sửa và lưu file: {srt_path.name}")
        
        is_valid = len(self.errors) == 0
        return is_valid, fixed_content
    
    def _parse_srt(self, content):
        """Parse nội dung SRT thành list các subtitle"""
        # Tách các subtitle bằng dòng trống
        blocks = re.split(r'\n\s*\n', content.strip())
        
        subtitles = []
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) < 3:
                continue
            
            try:
                index = int(lines[0].strip())
                timestamp = lines[1].strip()
                text = '\n'.join(lines[2:])
                
                subtitles.append({
                    'index': index,
                    'timestamp': timestamp,
                    'text': text,
                    'raw': block
                })
            except:
                continue
        
        return subtitles
    
    def _validate_subtitle(self, expected_index, sub):
        """Validate một subtitle"""
        index = sub['index']
        timestamp = sub['timestamp']
        text = sub['text']
        
        # 1. Kiểm tra số thứ tự
        if index != expected_index:
            self.errors.append(
                f"Subtitle #{expected_index}: Số thứ tự sai (có {index}, cần {expected_index})"
            )
        
        # 2. Kiểm tra định dạng timestamp
        timestamp_pattern = r'^\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}$'
        if not re.match(timestamp_pattern, timestamp):
            self.errors.append(
                f"Subtitle #{index}: Timestamp sai định dạng: '{timestamp}'"
            )
            
            # Kiểm tra các lỗi thường gặp
            if '.' in timestamp:
                self.warnings.append(
                    f"Subtitle #{index}: Dùng dấu chấm (.) thay vì dấu phẩy (,)"
                )
            if re.search(r'\d{2}:\d{1,2}:\d{2,3}', timestamp):
                self.warnings.append(
                    f"Subtitle #{index}: Thiếu số 0 hoặc sai số chữ số"
                )
        else:
            # Validate logic timestamp
            try:
                start, end = timestamp.split('-->')
                start_ms = self._timestamp_to_ms(start.strip())
                end_ms = self._timestamp_to_ms(end.strip())
                
                if start_ms >= end_ms:
                    self.errors.append(
                        f"Subtitle #{index}: Thời gian bắt đầu >= kết thúc"
                    )
                
                duration = (end_ms - start_ms) / 1000
                if duration > 10:
                    self.warnings.append(
                        f"Subtitle #{index}: Phụ đề quá dài ({duration:.1f}s)"
                    )
            except:
                pass
        
        # 3. Kiểm tra nội dung
        if not text.strip():
            self.warnings.append(f"Subtitle #{index}: Nội dung trống")
        
        if len(text) > 200:
            self.warnings.append(
                f"Subtitle #{index}: Nội dung quá dài ({len(text)} ký tự)"
            )
    
    def _timestamp_to_ms(self, timestamp):
        """Chuyển timestamp sang milliseconds"""
        # Format: HH:MM:SS,mmm
        time_part, ms_part = timestamp.split(',')
        h, m, s = map(int, time_part.split(':'))
        ms = int(ms_part)
        
        total_ms = (h * 3600 + m * 60 + s) * 1000 + ms
        return total_ms
    
    def _ms_to_timestamp(self, ms):
        """Chuyển milliseconds sang timestamp"""
        hours = ms // 3600000
        ms %= 3600000
        minutes = ms // 60000
        ms %= 60000
        seconds = ms // 1000
        milliseconds = ms % 1000
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
    
    def _fix_subtitles(self, subtitles):
        """Sửa lỗi trong subtitles"""
        fixed = []
        
        for i, sub in enumerate(subtitles, 1):
            # Sửa số thứ tự
            index = i
            
            # Sửa timestamp
            timestamp = sub['timestamp']
            
            # Thay dấu chấm bằng dấu phẩy
            timestamp = timestamp.replace('.', ',')
            
            # Sửa format timestamp nếu sai
            timestamp = self._fix_timestamp_format(timestamp)
            
            # Lấy text
            text = sub['text'].strip()
            
            # Tạo subtitle mới
            fixed.append(f"{index}\n{timestamp}\n{text}\n")
        
        return '\n'.join(fixed)
    
    def _fix_timestamp_format(self, timestamp):
        """Sửa định dạng timestamp"""
        try:
            # Tách start và end
            parts = re.split(r'\s*-->\s*', timestamp)
            if len(parts) != 2:
                return timestamp
            
            start, end = parts
            
            # Sửa từng phần
            start_fixed = self._fix_single_timestamp(start)
            end_fixed = self._fix_single_timestamp(end)
            
            return f"{start_fixed} --> {end_fixed}"
        except:
            return timestamp
    
    def _fix_single_timestamp(self, ts):
        """Sửa một timestamp đơn"""
        try:
            # Loại bỏ khoảng trắng
            ts = ts.strip()
            
            # Tách phần time và milliseconds
            if ',' in ts:
                time_part, ms_part = ts.split(',')
            elif '.' in ts:
                time_part, ms_part = ts.split('.')
            else:
                return ts
            
            # Tách giờ:phút:giây
            parts = time_part.split(':')
            if len(parts) != 3:
                return ts
            
            # Đảm bảo đủ 2 chữ số
            h = parts[0].zfill(2)[:2]
            m = parts[1].zfill(2)[:2]
            s = parts[2].zfill(2)[:2]
            
            # Đảm bảo milliseconds có 3 chữ số
            ms = ms_part.ljust(3, '0')[:3]
            
            return f"{h}:{m}:{s},{ms}"
        except:
            return ts
    
    def _print_results(self):
        """In kết quả kiểm tra"""
        print(f"\n{'='*60}")
        print(f"📊 KẾT QUẢ KIỂM TRA")
        print(f"{'='*60}")
        
        if not self.errors and not self.warnings:
            print("✅ File SRT hoàn hảo! Không có lỗi.")
            return
        
        if self.errors:
            print(f"\n❌ LỖI ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print(f"\n⚠️  CẢNH BÁO ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
    
    def batch_validate(self, directory, pattern="*.srt", fix=False):
        """
        Kiểm tra tất cả file SRT trong thư mục
        
        Args:
            directory: Thư mục chứa file SRT
            pattern: Pattern để tìm file
            fix: True = tự động sửa lỗi
        """
        directory = Path(directory)
        srt_files = sorted(directory.glob(pattern))
        
        # Loại bỏ file backup
        srt_files = [f for f in srt_files if not f.name.endswith('.bak')]
        
        if not srt_files:
            print(f"⚠️  Không tìm thấy file SRT nào trong {directory}")
            return
        
        print(f"📝 Tìm thấy {len(srt_files)} file SRT")
        print(f"🔧 Chế độ: {'Sửa lỗi tự động' if fix else 'Chỉ kiểm tra'}\n")
        
        results = []
        for i, srt_path in enumerate(srt_files, 1):
            print(f"\n{'='*60}")
            print(f"[{i}/{len(srt_files)}]")
            print(f"{'='*60}")
            
            try:
                is_valid, _ = self.validate_file(srt_path, fix=fix)
                results.append((srt_path, is_valid))
            except Exception as e:
                print(f"✗ Lỗi: {e}")
                results.append((srt_path, False))
        
        # Tổng kết
        print(f"\n{'='*60}")
        print(f"📊 TỔNG KẾT")
        print(f"{'='*60}")
        
        valid_count = sum(1 for _, is_valid in results if is_valid)
        print(f"✓ Hợp lệ: {valid_count}/{len(results)}")
        
        if valid_count < len(results):
            print(f"\n⚠️  File có lỗi:")
            for srt_path, is_valid in results:
                if not is_valid:
                    print(f"  - {srt_path.name}")


def main():
    """Ví dụ sử dụng"""
    validator = SRTValidator()
    
    print("Chọn chế độ:")
    print("1. Kiểm tra 1 file SRT")
    print("2. Kiểm tra tất cả file SRT trong thư mục")
    
    choice = input("\nNhập lựa chọn (1 hoặc 2): ").strip()
    
    if choice == '1':
        # Kiểm tra 1 file
        srt_path = input("Đường dẫn file SRT: ").strip().strip('"').strip("'")
        fix = input("Tự động sửa lỗi? (y/n, mặc định n): ").strip().lower() == 'y'
        
        validator.validate_file(srt_path, fix=fix)
        
    elif choice == '2':
        # Kiểm tra batch
        directory = input("Thư mục chứa file SRT (mặc định: recordings): ").strip() or 'recordings'
        pattern = input("Pattern (mặc định: *.srt): ").strip() or '*.srt'
        fix = input("Tự động sửa lỗi? (y/n, mặc định n): ").strip().lower() == 'y'
        
        validator.batch_validate(directory, pattern, fix=fix)
    
    else:
        print("Lựa chọn không hợp lệ!")


if __name__ == "__main__":
    main()
