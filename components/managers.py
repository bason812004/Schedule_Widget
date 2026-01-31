"""
Managers: Quản lý cookies, settings, data
"""
import os
import sys
import json
import winreg
import re
from datetime import datetime, timedelta
from PySide6.QtCore import Signal, QObject

from .constants import DATA_FILE, COOKIES_FILE, SETTINGS_FILE, DAYS, PERIODS


class CookieManager:
    """Quản lý cookies để auto-login"""
    
    def __init__(self):
        self.cookies = []
    
    def save_cookies(self, cookies_list):
        """Lưu cookies ra file"""
        try:
            with open(COOKIES_FILE, 'w', encoding='utf-8') as f:
                json.dump(cookies_list, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            return False
    
    def load_cookies(self):
        """Load cookies từ file"""
        try:
            if os.path.exists(COOKIES_FILE):
                with open(COOKIES_FILE, 'r', encoding='utf-8') as f:
                    self.cookies = json.load(f)
                return self.cookies
        except Exception as e:
            pass
        return []
    
    def has_cookies(self):
        """Kiểm tra có cookies không"""
        return os.path.exists(COOKIES_FILE) and len(self.load_cookies()) > 0
    
    def clear_cookies(self):
        """Xóa cookies"""
        if os.path.exists(COOKIES_FILE):
            os.remove(COOKIES_FILE)



class SettingsManager:
    """Quản lý cài đặt app"""
    
    def __init__(self):
        self.settings = {
            'auto_refresh_hours': 6,
            'run_at_startup': False,
            'last_successful_fetch': None
        }
        self.load()
    
    def load(self):
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    self.settings.update(json.load(f))
        except Exception as e:
            pass
    
    def save(self):
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            pass
    
    def set_startup(self, enabled):
        """Thêm/xóa app khỏi Windows startup"""
        self.settings['run_at_startup'] = enabled
        self.save()
        
        # Lấy đường dẫn app - ưu tiên .exe nếu đã build
        app_path = os.path.abspath(sys.argv[0])
        
        # Nếu là .exe thì dùng trực tiếp, không cần pythonw
        if app_path.endswith('.exe'):
            cmd = f'"{app_path}"'
        else:
            # Nếu là .py thì dùng pythonw
            cmd = f'pythonw "{app_path}"'
        
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "IUHScheduleWidget"
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            if enabled:
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, cmd)
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            pass


class DataManager(QObject):
    """Quản lý dữ liệu lịch học và task"""
    data_changed = Signal()
    
    def __init__(self):
        super().__init__()
        self.schedule = []
        self.tasks = []
        self.load()
    
    def load(self):
        """Load dữ liệu từ file"""
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Hỗ trợ cả format cũ (flat) và mới (week-based)
                    if 'schedule' in data:
                        # Format cũ - chuyển sang format mới
                        self.schedule = data.get('schedule', [])
                        self.tasks = data.get('tasks', [])
                    else:
                        # Format mới - gộp tất cả tuần lại
                        self.schedule = []
                        self.tasks = []
                        for week_key, week_data in data.items():
                            if week_key.startswith('tuan'):
                                self.schedule.extend(week_data.get('schedule', []))
                                self.tasks.extend(week_data.get('tasks', []))
            else:
                pass
        except Exception as e:
            pass
    
    def save(self):
        """Lưu dữ liệu ra file, tổ chức theo tuần"""
        try:
            # Phân loại schedule theo tuần
            weeks = {}
            for item in self.schedule:
                date = item.get('date', '')
                if len(date) >= 10:  # dd/mm/yyyy
                    # Tính ngày thứ 2 của tuần này
                    try:
                        from datetime import datetime, timedelta
                        day, month, year = date.split('/')
                        item_date = datetime(int(year), int(month), int(day))
                        days_since_monday = item_date.weekday()
                        monday = item_date - timedelta(days=days_since_monday)
                        week_key = f"tuan{monday.strftime('%d/%m/%Y')}"
                        
                        if week_key not in weeks:
                            weeks[week_key] = {'schedule': [], 'tasks': []}
                        weeks[week_key]['schedule'].append(item)
                    except:
                        # Nếu parse lỗi, bỏ vào tuần "unknown"
                        if 'unknown' not in weeks:
                            weeks['unknown'] = {'schedule': [], 'tasks': []}
                        weeks['unknown']['schedule'].append(item)
            
            # Thêm tasks vào tuần tương ứng hoặc tuần hiện tại
            for task in self.tasks:
                # Tasks không có date cụ thể, bỏ vào tất cả các tuần
                # Hoặc có thể tạo key riêng cho tasks
                if weeks:
                    # Bỏ vào tuần đầu tiên
                    first_week = list(weeks.keys())[0]
                    weeks[first_week]['tasks'].append(task)
            
            # Thêm timestamp
            weeks['updated'] = datetime.now().isoformat()
            
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(weeks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            pass
            import traceback
            traceback.print_exc()
    
    def parse_schedule_html(self, html, week_dates=None, auto_save=True, merge_mode=False):
        """Parse HTML lịch học từ IUH
        
        Args:
            html: HTML content
            week_dates: Dict map day_idx -> date string (e.g. {0: '03/02/2026', 1: '04/02/2026'})
            auto_save: Tự động lưu file sau khi parse (mặc định True)
            merge_mode: Nếu True, merge vào schedule hiện tại thay vì xóa (mặc định False)
        """
        # Backup schedule cũ nếu merge_mode
        old_schedule = self.schedule.copy() if merge_mode else []
        
        self.schedule = []
        
        # Parse ngày tháng từ header nếu chưa có
        if not week_dates:
            week_dates = self._parse_week_dates_from_html(html)
        
        if len(html) < 5000:
            return 0
        
        error_patterns = ['<title>404', '<title>500', 'page not found', 'server error', '503 service']
        is_error_page = any(pattern in html.lower() for pattern in error_patterns)
        if is_error_page:
            return 0
        
        table_match = re.search(r'<table[^>]*>(.*?)</table>', html, re.DOTALL | re.IGNORECASE)
        
        if not table_match or len(table_match.group(1)) < 1000:
            tables = re.findall(r'<table[^>]*>(.*?)</table>', html, re.DOTALL | re.IGNORECASE)
            for tbl in tables:
                if ('đứ' in tbl.lower() or 'sáng' in tbl.lower() or 'chiều' in tbl.lower()) and len(tbl) > 1000:
                    table_match = type('obj', (object,), {'group': lambda self, n: tbl})()
                    break
        
        if not table_match:
            return 0
        
        table_html = table_match.group(1)
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL)
        
        for row_idx, row_html in enumerate(rows):
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.DOTALL)
            
            if len(cells) < 2:
                continue
            
            first_cell_text = re.sub(r'<[^>]+>', '', cells[0]).strip()
            
            period = -1
            if 'Sáng' in first_cell_text:
                period = 0
            elif 'Chiều' in first_cell_text:
                period = 1  
            elif 'Tối' in first_cell_text:
                period = 2
            
            if period == -1:
                continue
            
            for day_idx in range(7):
                cell_idx = day_idx + 1
                
                if cell_idx >= len(cells):
                    break
                
                cell_html = cells[cell_idx]
                cell_text = re.sub(r'<[^>]+>', ' ', cell_html).strip()
                cell_text = re.sub(r'\s+', ' ', cell_text)
                
                if not cell_text or len(cell_text) < 15:
                    continue
                
                cell_clean = re.sub(r'<[^>]+>', '\n', cell_html)
                lines = [l.strip() for l in cell_clean.split('\n') if l.strip()]
                
                subject_names = []
                for line in lines:
                    if re.match(r'^DH[A-Z0-9]+', line):
                        continue
                    if re.match(r'^[\d\s\-–]+$', line):
                        continue
                    if len(line) < 10:
                        continue
                    if re.match(r'^(Tiết|Phòng|GV|Giảng viên)\s*:', line, re.IGNORECASE):
                        continue
                    if re.match(r'^[A-Z]\d+\.', line) or re.match(r'^[A-Z]\d+\.\d+', line):
                        continue
                    words = line.split()
                    if len(words) <= 4 and all(w[0].isupper() for w in words if w):
                        if not any(kw in line.lower() for kw in ['học', 'trình', 'liệu', 'nghệ', 'trúc', 'nhập', 'môn', 'quản', 'phát', 'triển', 'cntt', 'dự án']):
                            continue
                    subject_names.append(line)
                
                tiet_matches = list(re.finditer(r'Tiết\s*:\s*(\d+)\s*[-–]\s*(\d+)', cell_clean))
                
                if not tiet_matches:
                    continue
                
                phong_matches = list(re.finditer(r'Phòng\s*:\s*([A-Z0-9][A-Za-z0-9\.]*)', cell_clean))
                
                for idx, tiet_match in enumerate(tiet_matches):
                    tiet_str = f"{tiet_match.group(1)}-{tiet_match.group(2)}"
                    
                    if idx < len(subject_names):
                        subject_name = subject_names[idx]
                    else:
                        subject_name = subject_names[-1] if subject_names else "Môn học"
                    
                    room = None
                    if idx < len(phong_matches):
                        room = phong_matches[idx].group(1)
                    
                    item = {
                        'raw': f"{subject_name} Tiết:{tiet_str}"[:200],
                        'day': day_idx,
                        'period': period,
                        'subject': subject_name[:60],
                        'tiet': tiet_str
                    }
                    
                    # Thêm ngày tháng nếu có
                    if week_dates and day_idx in week_dates:
                        item['date'] = week_dates[day_idx]
                    
                    if room:
                        item['room'] = room
                    
                    self.schedule.append(item)
        
        # Merge với schedule cũ nếu merge_mode
        if merge_mode and old_schedule:
            # Tạo set các key từ schedule cũ
            existing_keys = set()
            for item in old_schedule:
                key = (item.get('date', ''), item.get('subject', ''), item.get('tiet', ''), item.get('day', -1))
                existing_keys.add(key)
            
            # Lọc duplicate từ schedule mới
            new_items = []
            duplicate_count = 0
            for item in self.schedule:
                key = (item.get('date', ''), item.get('subject', ''), item.get('tiet', ''), item.get('day', -1))
                if key not in existing_keys:
                    new_items.append(item)
                    existing_keys.add(key)
                else:
                    duplicate_count += 1
            
            # Merge: schedule cũ + items mới (không trùng)
            self.schedule = old_schedule + new_items
        
        if auto_save:
            self.save()
            self.data_changed.emit()
        return len(self.schedule)
    
    def _parse_week_dates_from_html(self, html):
        """Parse ngày tháng của các ngày trong tuần từ header bảng
        
        Returns:
            Dict {day_idx: 'dd/mm/yyyy'} hoặc None nếu không tìm thấy
        """
        try:
            # Tìm header row có các ngày
            header_pattern = r'<tr[^>]*>(.*?)</tr>'
            rows = re.findall(header_pattern, html, re.DOTALL)
            
            for row_idx, row in enumerate(rows[:5]):  # Chỉ check 5 row đầu
                # Tìm các cell có dạng "Thứ X (dd/mm)" hoặc "CN (dd/mm)"
                cells = re.findall(r'<th[^>]*>(.*?)</th>', row, re.DOTALL)
                if len(cells) < 7:
                    continue
                    
                week_dates = {}
                date_found = False
                
                for idx, cell in enumerate(cells):
                    cell_text = re.sub(r'<[^>]+>', ' ', cell).strip()  # Thay thẻ HTML bằng khoảng trắng
                    cell_text = re.sub(r'\s+', ' ', cell_text)  # Gộp nhiều space thành 1
                    
                    # Pattern: "Thứ 2 26/01" hoặc "CN 09/02" (sau khi replace <br> bằng space)
                    date_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', cell_text)
                    if not date_match:
                        # Thử pattern ngắn hơn: (dd/mm) 
                        date_match = re.search(r'(\d{1,2})/(\d{1,2})', cell_text)
                    
                    if date_match:
                        day = date_match.group(1).zfill(2)
                        month = date_match.group(2).zfill(2)
                        
                        # Lấy năm
                        if len(date_match.groups()) >= 3:
                            year = date_match.group(3)
                        else:
                            # Lấy năm hiện tại
                            from datetime import datetime
                            year = datetime.now().year
                            
                            # Nếu tháng nhỏ hơn tháng hiện tại và đang ở cuối năm -> năm sau
                            current_month = datetime.now().month
                            if int(month) < current_month and current_month >= 10:
                                year += 1
                        
                        date_str = f"{day}/{month}/{year}"
                        
                        # Map vị trí cell với day_idx (bỏ qua cell đầu tiên là "Ca")
                        if idx > 0:
                            week_dates[idx - 1] = date_str
                            date_found = True
                
                if date_found and len(week_dates) >= 7:
                    return week_dates
            
            return None
        except Exception as e:
            return None
            import traceback
            traceback.print_exc()
            return None
    
    def add_task(self, title, day, period, note='', deadline=None, time=None, date=None):
        """Thêm task mới
        
        Args:
            title: Tên công việc
            day: Thứ trong tuần (0-6)
            period: Ca (0-2)
            note: Ghi chú
            deadline: Hạn chót (không dùng)
            time: Giờ thực hiện
            date: Ngày cụ thể 'dd/mm/yyyy' - Nếu không có sẽ dùng ngày hiện tại của thứ đó trong tuần này
        """
        # Nếu không có date, tính date của thứ này trong tuần hiện tại
        if not date:
            today = datetime.now()
            days_since_monday = today.weekday()
            monday = today - timedelta(days=days_since_monday)
            target_date = monday + timedelta(days=day)
            date = target_date.strftime('%d/%m/%Y')
        
        task = {
            'id': datetime.now().timestamp(),
            'title': title,
            'day': day,
            'period': period,
            'note': note,
            'time': time or '08:00',
            'deadline': deadline,
            'done': False,
            'created': datetime.now().isoformat(),
            'date': date  # THÊM date để task chỉ xuất hiện trong tuần này
        }
        self.tasks.append(task)
        self.save()
        self.data_changed.emit()
        return task
    
    def update_task(self, task_id, **kwargs):
        """Cập nhật task"""
        for task in self.tasks:
            if task.get('id') == task_id:
                task.update(kwargs)
                break
        self.save()
        self.data_changed.emit()
    
    def delete_task(self, task_id):
        """Xóa task"""
        self.tasks = [t for t in self.tasks if t.get('id') != task_id]
        self.save()
        self.data_changed.emit()
    
    def toggle_task(self, task_id):
        """Đánh dấu hoàn thành/chưa hoàn thành"""
        for task in self.tasks:
            if task.get('id') == task_id:
                task['done'] = not task.get('done', False)
                break
        self.save()
        self.data_changed.emit()
    
    def get_items_for_cell(self, day, period, week_dates=None):
        """Lấy tất cả items cho ô [day][period], sắp xếp theo thời gian
        
        Args:
            day: Thứ trong tuần (0-6)
            period: Ca (0=sáng, 1=chiều, 2=tối)
            week_dates: Dict {day_idx: 'dd/mm/yyyy'} - Nếu có, chỉ lấy items có date khớp
        """
        items = []
        
        for s in self.schedule:
            if s.get('day') == day and s.get('period') == period:
                # Nếu có week_dates, kiểm tra date có khớp không (CHỈ SO SÁNH dd/mm, BỎ QUA năm)
                if week_dates:
                    item_date = s.get('date', '')
                    target_date = week_dates.get(day, '')
                    
                    # Lấy phần dd/mm từ cả 2 strings
                    item_ddmm = item_date[:5] if len(item_date) >= 5 else ''  # "26/01"
                    target_ddmm = target_date[:5] if len(target_date) >= 5 else ''  # "26/01"
                    
                    if item_ddmm != target_ddmm:
                        continue
                
                items.append({'type': 'schedule', 'data': s})
        
        for t in self.tasks:
            if t.get('day') == day and t.get('period') == period:
                # Kiểm tra date của task nếu có week_dates
                if week_dates:
                    task_date = t.get('date', '')
                    target_date = week_dates.get(day, '')
                    
                    # So sánh dd/mm
                    task_ddmm = task_date[:5] if len(task_date) >= 5 else ''
                    target_ddmm = target_date[:5] if len(target_date) >= 5 else ''
                    
                    if task_ddmm and target_ddmm and task_ddmm != target_ddmm:
                        continue
                
                items.append({'type': 'task', 'data': t})
        
        def get_start_time(item):
            if item['type'] == 'task':
                time_str = item['data'].get('time', '12:00')
                try:
                    parts = time_str.split(':')
                    return int(parts[0]) * 60 + int(parts[1])
                except:
                    return 720
            else:
                tiet = item['data'].get('tiet', '')
                tiet_times = {
                    '1-3': 6 * 60 + 30,
                    '4-6': 9 * 60,
                    '7-9': 12 * 60 + 30,
                    '10-12': 15 * 60,
                }
                return tiet_times.get(tiet, 720)
        
        items.sort(key=get_start_time)
        return items
    
    def get_week_dates_from_offset(self, week_offset=0):
        """Tính toán ngày tháng của tuần dựa vào offset
        
        Args:
            week_offset: 0=tuần này, 1=tuần sau, -1=tuần trước
        
        Returns:
            Dict {day_idx: 'dd/mm/yyyy'} hoặc None
        """
        from datetime import datetime, timedelta
        
        # Tìm thứ 2 của tuần hiện tại
        today = datetime.now()
        days_since_monday = today.weekday()  # 0=Monday, 6=Sunday
        monday = today - timedelta(days=days_since_monday)
        
        # Cộng offset tuần
        target_monday = monday + timedelta(weeks=week_offset)
        
        # Tạo dict 7 ngày
        week_dates = {}
        for i in range(7):
            date_obj = target_monday + timedelta(days=i)
            date_str = date_obj.strftime('%d/%m/%Y')
            week_dates[i] = date_str
        
        return week_dates
