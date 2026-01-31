"""
Constants và cấu hình cho IUH Schedule Widget
"""
import os
import sys

# File lưu dữ liệu - hỗ trợ cả khi chạy từ .exe và .py
if getattr(sys, 'frozen', False):
    # Chạy từ .exe - dữ liệu nằm cùng folder với .exe
    APP_DIR = os.path.dirname(sys.executable)
else:
    # Chạy từ .py - dữ liệu nằm ở thư mục gốc project
    APP_DIR = os.path.dirname(os.path.dirname(__file__))

DATA_FILE = os.path.join(APP_DIR, "schedule_data.json")
COOKIES_FILE = os.path.join(APP_DIR, "cookies.json")
SETTINGS_FILE = os.path.join(APP_DIR, "settings.json")

# URL trang lịch học
SCHEDULE_URL = "https://sv.iuh.edu.vn/lich-theo-tuan.html?pLoaiLich=1"
LOGIN_URL = "https://sv.iuh.edu.vn"

def get_schedule_url_for_week(week_offset=0):
    """Lấy URL lịch học cho tuần cụ thể
    
    Args:
        week_offset: Số tuần tính từ tuần hiện tại (0=tuần này, 1=tuần sau, -1=tuần trước)
    
    Returns:
        URL string
    """
    if week_offset == 0:
        return SCHEDULE_URL
    else:
        # IUH dùng tham số pTuanHoc để chọn tuần
        # pTuanHoc=1 là tuần hiện tại, 2 là tuần sau, etc.
        week_num = week_offset + 1
        return f"https://sv.iuh.edu.vn/lich-theo-tuan.html?pLoaiLich=1&pTuanHoc={week_num}"

# Màu sắc giống web IUH
COLORS = {
    'header_bg': '#5a9fd4',
    'class_bg': '#d4edda',
    'task_bg': '#fff3cd',
    'empty_bg': '#ffffff',
    'border': '#dee2e6',
    'text': '#212529',
    'text_light': '#ffffff',
    'widget_bg': '#f8f9fa',
    'accent': '#17a2b8',
    'success': '#28a745',
    'warning': '#ffc107',
    'danger': '#dc3545',
}

DAYS = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'CN']
PERIODS = ['Sáng', 'Chiều', 'Tối']

# Định nghĩa thời gian các tiết học
TIET_TIME = {
    # Ca Sáng
    '1-3': (6, 30, 9, 0),    # 6h30 - 9h
    '4-6': (9, 0, 11, 30),   # 9h - 11h30
    # Ca Chiều  
    '7-9': (12, 30, 15, 0),  # 12h30 - 15h
    '10-12': (15, 0, 17, 30), # 15h - 17h30
}

# Khoảng thời gian của mỗi ca
PERIOD_TIME = {
    0: (6, 30, 12, 0),   # Sáng: 6h30 - 12h
    1: (12, 30, 17, 30), # Chiều: 12h30 - 17h30
    2: (18, 0, 22, 0),   # Tối: 18h - 22h
}
