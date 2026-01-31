"""
Widgets: ScheduleCell và ScheduleWidget
"""
import sys
import ctypes
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QGridLayout,
    QMenu, QSystemTrayIcon, QSizePolicy, QDialog
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QApplication

from .constants import COLORS, DAYS, PERIODS
from .dialogs import AddTaskDialog
from .login import LoginWindow

# Logging cho debug
print("[DEBUG] widgets.py loaded", file=sys.stdout, flush=True)

# Windows API
user32 = ctypes.windll.user32
SW_SHOW = 5
SW_RESTORE = 9
HWND_TOPMOST = -1
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_SHOWWINDOW = 0x0040
SWP_NOACTIVATE = 0x0010


class ScheduleCell(QFrame):
    """Một ô trong bảng lịch"""
    
    def __init__(self, day, period, data_manager, parent=None):
        super().__init__(parent)
        self.day = day
        self.period = period
        self.data_manager = data_manager
        self.week_dates = None  # Sẽ được set từ parent widget
        
        self.setMinimumSize(150, 100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(6, 6, 6, 6)
        self.layout.setSpacing(3)
        
        # Không refresh ở đây - sẽ refresh sau khi set_week_dates()
    
    def set_week_dates(self, week_dates):
        """Set ngày tháng của tuần để lọc, sau đó refresh"""
        self.week_dates = week_dates
        self.refresh()  # Refresh sau khi có week_dates
    
    def refresh(self):
        """Cập nhật nội dung ô"""
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Lấy items với lọc theo week_dates
        items = self.data_manager.get_items_for_cell(self.day, self.period, self.week_dates)
        
        if not items:
            self.setStyleSheet(f"""
                ScheduleCell {{
                    background: {COLORS['empty_bg']};
                    border: 1px solid {COLORS['border']};
                }}
                ScheduleCell:hover {{
                    background: #e9ecef;
                    border: 2px dashed {COLORS['accent']};
                }}
            """)
            lbl = QLabel("+")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color: #aaa; font-size: 28px; font-weight: bold;")
            lbl.setAttribute(Qt.WA_TransparentForMouseEvents, True)  # Cho phép event đi qua xuống cell
            self.layout.addWidget(lbl)
        else:
            has_class = any(i['type'] == 'schedule' for i in items)
            bg_color = COLORS['class_bg'] if has_class else COLORS['task_bg']
            
            self.setStyleSheet(f"""
                ScheduleCell {{
                    background: {bg_color};
                    border: 1px solid {COLORS['border']};
                    border-radius: 6px;
                }}
            """)
            
            for item in items:
                if item['type'] == 'schedule':
                    schedule_container = QFrame()
                    
                    # Kiểm tra nếu phòng là 'Tr' (trực tuyến) thì đổi màu
                    room = item['data'].get('room', '')
                    is_online = room.lower().strip() == 'tr'
                    
                    if is_online:
                        # Màu xanh dương nhạt cho lớp trực tuyến
                        schedule_container.setStyleSheet("""
                            QFrame {
                                background: rgba(66, 165, 245, 0.35);
                                border: 1px solid rgba(33, 150, 243, 0.4);
                                border-radius: 4px;
                                padding: 3px;
                                margin: 1px 0;
                            }
                        """)
                    else:
                        schedule_container.setStyleSheet("""
                            QFrame {
                                background: rgba(255,255,255,0.65);
                                border: 1px solid rgba(26, 71, 42, 0.15);
                                border-radius: 4px;
                                padding: 3px;
                                margin: 1px 0;
                            }
                        """)
                    schedule_layout = QVBoxLayout(schedule_container)
                    schedule_layout.setContentsMargins(5, 4, 5, 4)
                    schedule_layout.setSpacing(3)
                    
                    subject = item['data'].get('subject', 'N/A')
                    subject_lbl = QLabel(subject)
                    subject_lbl.setStyleSheet("""
                        font-size: 11px; 
                        color: #1a472a; 
                        font-weight: bold; 
                        background: transparent;
                        line-height: 1.2;
                    """)
                    subject_lbl.setWordWrap(True)
                    subject_lbl.setAlignment(Qt.AlignLeft | Qt.AlignTop)
                    schedule_layout.addWidget(subject_lbl)
                    
                    # Tách tiết và phòng ra 2 phía
                    tiet = item['data'].get('tiet', '')
                    room = item['data'].get('room', '')
                    
                    if tiet or room:
                        detail_layout = QHBoxLayout()
                        detail_layout.setContentsMargins(0, 0, 0, 0)
                        detail_layout.setSpacing(5)
                        
                        if tiet:
                            tiet_lbl = QLabel(f"Tiết {tiet}")
                            tiet_lbl.setStyleSheet("""
                                font-size: 9px; 
                                color: #555; 
                                background: transparent;
                                font-weight: 600;
                            """)
                            detail_layout.addWidget(tiet_lbl)
                        
                        detail_layout.addStretch()
                        
                        if room:
                            room_lbl = QLabel(room)
                            room_lbl.setStyleSheet("""
                                font-size: 9px; 
                                color: #555; 
                                background: transparent;
                                font-weight: 600;
                            """)
                            room_lbl.setAlignment(Qt.AlignRight)
                            detail_layout.addWidget(room_lbl)
                        
                        schedule_layout.addLayout(detail_layout)
                    
                    self.layout.addWidget(schedule_container)
                else:
                    task = item['data']
                    
                    # Tạo container cho task với layout ngang
                    task_container = QFrame()
                    task_container.setCursor(QCursor(Qt.PointingHandCursor))
                    task_container.setMinimumHeight(28)
                    
                    task_layout = QHBoxLayout(task_container)
                    task_layout.setContentsMargins(6, 4, 6, 4)
                    task_layout.setSpacing(6)
                    
                    # Icon và giờ bên trái
                    icon = "✅" if task.get('done') else "📌"
                    time_str = task.get('time', '')
                    left_text = f"{icon} {time_str}" if time_str else icon
                    
                    left_lbl = QLabel(left_text)
                    left_lbl.setStyleSheet("""
                        font-size: 9px;
                        font-weight: 600;
                        color: #555;
                        background: transparent;
                    """)
                    task_layout.addWidget(left_lbl)
                    
                    # Tên công việc bên phải
                    title = task.get('title', '')
                    title_lbl = QLabel(title)
                    title_lbl.setStyleSheet("""
                        font-size: 10px;
                        font-weight: bold;
                        color: #333;
                        background: transparent;
                    """)
                    title_lbl.setWordWrap(False)
                    title_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    task_layout.addWidget(title_lbl, 1)
                    
                    # Styling cho container
                    if task.get('done'):
                        task_container.setStyleSheet("""
                            QFrame {
                                background: rgba(200, 200, 200, 0.6);
                                border: 1px solid #aaa;
                                border-radius: 4px;
                                margin: 1px 0;
                            }
                            QFrame:hover {
                                background: rgba(180, 180, 180, 0.8);
                                border: 1px solid #888;
                            }
                            QLabel {
                                text-decoration: line-through;
                                color: #666;
                            }
                        """)
                    else:
                        task_container.setStyleSheet("""
                            QFrame {
                                background: rgba(255, 193, 7, 0.3);
                                border: 1px solid #ffc107;
                                border-radius: 4px;
                                margin: 1px 0;
                            }
                            QFrame:hover {
                                background: rgba(255, 193, 7, 0.5);
                                border: 2px solid #e0a800;
                            }
                        """)
                    
                    task_container.setToolTip("🖱️ Click để xem chi tiết")
                    
                    # Thêm event handler để mở dialog chi tiết
                    def task_click_handler(e, t=task):
                        if e.button() == Qt.LeftButton:
                            # Delay nhỏ để popup cũ đóng hoàn toàn trước khi mở dialog mới
                            QTimer.singleShot(50, lambda: self.show_task_detail(t))
                    
                    task_container.mousePressEvent = task_click_handler
                    
                    self.layout.addWidget(task_container)
        
        self.layout.addStretch()
    
    def show_task_detail(self, task):
        """Hiện dialog xem chi tiết công việc"""
        dialog = QDialog(self)
        dialog.setWindowTitle("📋 Chi tiết công việc")
        dialog.setFixedSize(380, 280)
        dialog.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        dialog.setStyleSheet("""
            QDialog {
                background: #ffffff;
                border-radius: 12px;
                border: 2px solid #5a9fd4;
            }
            QLabel {
                color: #333333;
                background: transparent;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title_lbl = QLabel(f"📝 {task.get('title', 'Công việc')}")
        title_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #333333;")
        title_lbl.setWordWrap(True)
        layout.addWidget(title_lbl)
        
        status = "✅ Đã hoàn thành" if task.get('done') else "⬜ Chưa hoàn thành"
        status_color = "#28a745" if task.get('done') else "#ffc107"
        status_lbl = QLabel(status)
        status_lbl.setStyleSheet(f"font-size: 13px; color: {status_color}; font-weight: bold;")
        layout.addWidget(status_lbl)
        
        time_str = task.get('time', '')
        if time_str:
            time_lbl = QLabel(f"🕐 Giờ thực hiện: {time_str}")
            time_lbl.setStyleSheet("font-size: 13px; color: #555555;")
            layout.addWidget(time_lbl)
        
        day_idx = task.get('day', 0)
        period_idx = task.get('period', 0)
        day_name = DAYS[day_idx] if day_idx < len(DAYS) else "N/A"
        period_name = PERIODS[period_idx] if period_idx < len(PERIODS) else "N/A"
        schedule_lbl = QLabel(f"📅 {day_name} - Ca {period_name}")
        schedule_lbl.setStyleSheet("font-size: 13px; color: #555555;")
        layout.addWidget(schedule_lbl)
        
        note = task.get('note', '')
        if note:
            note_lbl = QLabel(f"📝 Ghi chú:\n{note}")
            note_lbl.setStyleSheet("font-size: 12px; color: #666666; padding: 10px; background: #f8f9fa; border-radius: 8px;")
            note_lbl.setWordWrap(True)
            layout.addWidget(note_lbl)
        
        created = task.get('created', '')
        if created:
            try:
                created_dt = datetime.fromisoformat(created)
                created_str = created_dt.strftime("%d/%m/%Y %H:%M")
                created_lbl = QLabel(f"📆 Tạo lúc: {created_str}")
                created_lbl.setStyleSheet("font-size: 11px; color: #888888;")
                layout.addWidget(created_lbl)
            except:
                pass
        
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        
        edit_btn = QPushButton("✏️ Sửa")
        edit_btn.setStyleSheet("""
            QPushButton {
                background: #5a9fd4;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background: #4a8fc4; }
        """)
        edit_btn.clicked.connect(lambda: (dialog.accept(), self.edit_task(task)))
        btn_layout.addWidget(edit_btn)
        
        close_btn = QPushButton("Đóng")
        close_btn.setStyleSheet("""
            QPushButton {
                background: #6c757d;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover { background: #5a6268; }
        """)
        close_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        dialog.exec()
    
    def mousePressEvent(self, event):
        day_name = DAYS[self.day] if self.day < len(DAYS) else f"Day{self.day}"
        period_name = PERIODS[self.period] if self.period < len(PERIODS) else f"Period{self.period}"
        button = "LEFT" if event.button() == Qt.LeftButton else "RIGHT" if event.button() == Qt.RightButton else "OTHER"
        
        print(f"\n[CLICK] {button} - {day_name} - Ca {period_name}", file=sys.stdout, flush=True)
        
        # Nếu có popup đang mở, bỏ qua và chỉ đóng popup đó
        if QApplication.activePopupWidget() is not None:
            print(f"  -> Popup đang mở, bỏ qua", file=sys.stdout, flush=True)
            event.accept()
            return
        
        # QUAN TRỌNG: Phải lọc theo week_dates giống như refresh()
        items = self.data_manager.get_items_for_cell(self.day, self.period, self.week_dates)
        has_schedule = any(i['type'] == 'schedule' for i in items)
        
        # Debug: In ra chi tiết các items
        print(f"  -> Items: {len(items)}, Có lịch: {has_schedule}", file=sys.stdout, flush=True)
        for idx, item in enumerate(items):
            print(f"     Item {idx}: type={item.get('type')}, data={list(item.get('data', {}).keys())[:3]}", file=sys.stdout, flush=True)
        
        if event.button() == Qt.LeftButton:
            # Nếu ô trống hoặc không có lịch học, hiện dialog thêm với delay nhỏ
            if not has_schedule:
                print(f"  -> Mở dialog thêm task", file=sys.stdout, flush=True)
                event.accept()
                QTimer.singleShot(50, self.show_add_dialog)
            else:
                print(f"  -> Có lịch, không mở dialog", file=sys.stdout, flush=True)
                event.accept()
        elif event.button() == Qt.RightButton:
            print(f"  -> Mở context menu", file=sys.stdout, flush=True)
            event.accept()
            self.show_context_menu(event.pos())
    
    def show_add_dialog(self):
        """Hiện dialog thêm task"""
        day_name = DAYS[self.day] if self.day < len(DAYS) else f"Day{self.day}"
        period_name = PERIODS[self.period] if self.period < len(PERIODS) else f"Period{self.period}"
        print(f"\n[DIALOG] Mở AddTaskDialog - {day_name} - Ca {period_name}", file=sys.stdout, flush=True)
        
        items = self.data_manager.get_items_for_cell(self.day, self.period, self.week_dates)
        existing_tiets = []
        for item in items:
            if item['type'] == 'class':
                tiet = item['data'].get('tiet', '')
                if tiet:
                    existing_tiets.append(tiet)
        
        dialog = AddTaskDialog(self, self.day, self.period, existing_tiets=existing_tiets)
        if dialog.exec():
            data = dialog.get_data()
            if data['title']:
                # Lấy date của ngày này trong tuần hiện tại từ week_dates
                task_date = self.week_dates.get(self.day, None) if self.week_dates else None
                self.data_manager.add_task(data['title'], data['day'], data['period'], data['note'], time=data.get('time'), date=task_date)
    
    def show_context_menu(self, pos):
        """Hiện menu khi click phải"""
        items = self.data_manager.get_items_for_cell(self.day, self.period, self.week_dates)
        
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 4px;
                color: #333333;
            }
            QMenu::item:selected {
                background: #e3f2fd;
                color: #000000;
            }
        """)
        
        add_action = menu.addAction("➕ Thêm công việc")
        add_action.triggered.connect(self.show_add_dialog)
        
        tasks = [i['data'] for i in items if i['type'] == 'task']
        
        if tasks:
            menu.addSeparator()
            
            for task in tasks:
                submenu = menu.addMenu(f"📝 {task.get('title', 'Task')[:25]}")
                
                toggle_text = "✅ Hoàn thành" if not task.get('done') else "↩️ Chưa xong"
                toggle_action = submenu.addAction(toggle_text)
                toggle_action.triggered.connect(lambda checked, t=task: self.data_manager.toggle_task(t['id']))
                
                edit_action = submenu.addAction("✏️ Sửa")
                edit_action.triggered.connect(lambda checked, t=task: self.edit_task(t))
                
                delete_action = submenu.addAction("🗑️ Xóa")
                delete_action.triggered.connect(lambda checked, t=task: self.data_manager.delete_task(t['id']))
        
        menu.exec(self.mapToGlobal(pos))
    
    def edit_task(self, task):
        """Sửa task"""
        dialog = AddTaskDialog(self, task.get('day', 0), task.get('period', 0), edit_task=task)
        if dialog.exec():
            data = dialog.get_data()
            if data['title']:
                self.data_manager.update_task(task['id'], **data)


class ScheduleWidget(QMainWindow):
    """Widget chính - bảng lịch dính desktop"""
    
    def __init__(self, data_manager, cookie_manager, settings_manager):
        super().__init__()
        self.data_manager = data_manager
        self.cookie_manager = cookie_manager
        self.settings_manager = settings_manager
        self.cells = {}
        self.login_window = None
        self._manually_hidden = False
        self.tray = None
        self.current_week_offset = 0  # 0=tuần này, 1=tuần sau, -1=tuần trước
        
        # Window flags - đơn giản, sẽ gắn vào desktop sau
        self.setWindowFlags(
            Qt.Tool |
            Qt.FramelessWindowHint
        )
        # KHÔNG dùng WA_TranslucentBackground khi gắn vào Progman
        # self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        # Size - chiếm toàn bộ nửa trên màn hình
        screen = QApplication.primaryScreen().geometry()
        widget_width = screen.width()
        widget_height = int(screen.height() * 0.5)
        
        self.setFixedSize(widget_width, widget_height)
        self.move(0, 0)  # Đặt ở góc trên bên trái màn hình
        
        # Main widget
        main = QWidget()
        main.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['widget_bg']};
                border-radius: 10px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        self.setCentralWidget(main)
        
        layout = QVBoxLayout(main)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(5)
        
        # Header
        header = QHBoxLayout()
        header.setSpacing(8)
        
        title = QLabel("📅 IUH Schedule Widget")
        title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['text']};")
        header.addWidget(title)
        
        header.addStretch()
        
        # Week navigation
        week_nav = QHBoxLayout()
        week_nav.setSpacing(5)
        
        prev_week_btn = QPushButton("◀")
        prev_week_btn.setFixedSize(32, 32)
        prev_week_btn.setToolTip("Tuần trước")
        prev_week_btn.clicked.connect(self.go_prev_week)
        prev_week_btn.setStyleSheet("border-radius: 16px; background: #17a2b8; color: white; font-size: 14px; font-weight: bold; border: none;")
        week_nav.addWidget(prev_week_btn)
        
        self.week_label = QLabel("Tuần này")
        self.week_label.setFixedWidth(120)
        self.week_label.setAlignment(Qt.AlignCenter)
        self.week_label.setStyleSheet("color: #333333; font-size: 14px; font-weight: 600; background: #e9ecef; border-radius: 16px; padding: 6px;")
        week_nav.addWidget(self.week_label)
        
        next_week_btn = QPushButton("▶")
        next_week_btn.setFixedSize(32, 32)
        next_week_btn.setToolTip("Tuần sau")
        next_week_btn.clicked.connect(self.go_next_week)
        next_week_btn.setStyleSheet("border-radius: 16px; background: #17a2b8; color: white; font-size: 14px; font-weight: bold; border: none;")
        week_nav.addWidget(next_week_btn)
        
        current_week_btn = QPushButton("📍")
        current_week_btn.setFixedSize(32, 32)
        current_week_btn.setToolTip("Về tuần hiện tại")
        current_week_btn.clicked.connect(self.go_current_week)
        current_week_btn.setStyleSheet("border-radius: 16px; background: #28a745; color: white; font-size: 14px; font-weight: bold; border: none;")
        week_nav.addWidget(current_week_btn)
        
        header.addLayout(week_nav)
        
        header.addSpacing(10)
        
        self.date_label = QLabel()
        self.date_label.setStyleSheet("color: #333333; font-size: 14px; font-weight: 600;")
        header.addWidget(self.date_label)
        
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedSize(32, 32)
        refresh_btn.setToolTip("Cập nhật lịch")
        refresh_btn.clicked.connect(self.refresh_schedule)
        refresh_btn.setStyleSheet("border-radius: 16px; background: #e9ecef; font-size: 14px; border: 1px solid #dee2e6;")
        header.addWidget(refresh_btn)
        
        settings_btn = QPushButton("⚙️")
        settings_btn.setFixedSize(32, 32)
        settings_btn.setToolTip("Đăng nhập lại")
        settings_btn.clicked.connect(self.open_login)
        settings_btn.setStyleSheet("border-radius: 16px; background: #e9ecef; font-size: 14px; border: 1px solid #dee2e6;")
        header.addWidget(settings_btn)
        
        hide_btn = QPushButton("—")
        hide_btn.setFixedSize(32, 32)
        hide_btn.setToolTip("Ẩn widget")
        hide_btn.clicked.connect(self.manual_hide)
        hide_btn.setStyleSheet("border-radius: 16px; background: #ffc107; font-size: 14px; color: #333333; font-weight: bold; border: 1px solid #ffb300;")
        header.addWidget(hide_btn)
        
        layout.addLayout(header)
        
        # Grid
        grid = QGridLayout()
        grid.setSpacing(3)
        grid.setContentsMargins(0, 5, 0, 0)
        
        header_cell = QLabel("Ca \\ Ngày")
        header_cell.setAlignment(Qt.AlignCenter)
        header_cell.setStyleSheet(f"""
            background: {COLORS['header_bg']};
            color: white;
            font-weight: bold;
            padding: 8px;
            border-radius: 5px;
            font-size: 13px;
        """)
        grid.addWidget(header_cell, 0, 0)
        
        # Tính ngày tháng dựa vào week_offset
        self.current_week_dates = self.data_manager.get_week_dates_from_offset(self.current_week_offset)
        
        today = datetime.now()
        today_str = today.strftime("%d/%m/%Y")
        
        for i, day in enumerate(DAYS):
            # Lấy ngày từ current_week_dates
            full_date = self.current_week_dates.get(i, '??/??/????')
            # Lấy dd/mm từ full date dd/mm/yyyy
            if '/' in full_date and len(full_date) >= 10:
                date_str = full_date[:5]  # Lấy 5 ký tự đầu: dd/mm
            else:
                date_str = '??/??'
            
            # Check nếu là hôm nay
            is_today = self.current_week_dates.get(i, '') == today_str
            
            cell = QLabel(f"{day}\n{date_str}")
            cell.setAlignment(Qt.AlignCenter)
            
            bg = COLORS['accent'] if is_today else COLORS['header_bg']
            cell.setStyleSheet(f"""
                background: {bg};
                color: white;
                font-weight: bold;
                padding: 8px 6px;
                border-radius: 5px;
                font-size: 12px;
            """)
            grid.addWidget(cell, 0, i + 1)
        
        for row, period in enumerate(PERIODS):
            period_cell = QLabel(period)
            period_cell.setAlignment(Qt.AlignCenter)
            period_cell.setStyleSheet(f"""
                background: {COLORS['header_bg']};
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 5px;
                font-size: 13px;
            """)
            grid.addWidget(period_cell, row + 1, 0)
            
            for col in range(7):
                cell = ScheduleCell(col, row, self.data_manager, self)
                cell.set_week_dates(self.current_week_dates)  # Set week dates và auto refresh
                self.cells[(col, row)] = cell
                grid.addWidget(cell, row + 1, col + 1)
        
        layout.addLayout(grid)
        
        # Timer update date
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_date)
        self.timer.start(60000)
        self.update_date()
        
        # Auto refresh timer
        self.refresh_timer = QTimer()
        refresh_hours = self.settings_manager.settings.get('auto_refresh_hours', 6)
        self.refresh_timer.timeout.connect(self.auto_refresh_schedule)
        self.refresh_timer.start(refresh_hours * 3600 * 1000)
        
        # Connect signals
        self.data_manager.data_changed.connect(self.refresh_all_cells)
        
        # Drag support
        self.drag_pos = None
    
    def refresh_all_cells(self):
        """Refresh tất cả cells với week_dates hiện tại"""
        # Cập nhật week_dates cho mỗi cell
        self.current_week_dates = self.data_manager.get_week_dates_from_offset(self.current_week_offset)
        for cell in self.cells.values():
            cell.set_week_dates(self.current_week_dates)
            cell.refresh()
    
    def update_date(self):
        now = datetime.now()
        self.date_label.setText(now.strftime("%d/%m/%Y %H:%M"))
    
    def _attach_to_desktop(self):
        """Gắn widget vào desktop layer (WorkerW) để chống Win+D"""
        try:
            hwnd = int(self.winId())
            
            # Tìm Progman window
            progman = user32.FindWindowW("Progman", None)
            if not progman:
                return
            
            # Gửi message để spawn WorkerW
            result = ctypes.c_int(0)
            user32.SendMessageTimeoutW(
                progman, 0x052C, 0, 0,
                0x0000, 500, ctypes.byref(result)
            )
            
            # Tìm WorkerW có SHELLDLL_DefView
            workerw = None
            
            def enum_callback(hwnd, lparam):
                nonlocal workerw
                shelldll = user32.FindWindowExW(hwnd, 0, "SHELLDLL_DefView", None)
                if shelldll:
                    # Tìm WorkerW sau SHELLDLL_DefView
                    workerw = user32.FindWindowExW(0, hwnd, "WorkerW", None)
                    if not workerw:
                        workerw = hwnd
                return True
            
            WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
            enum_func = WNDENUMPROC(enum_callback)
            user32.EnumWindows(enum_func, 0)
            
            if workerw:
                # GẮN widget vào WorkerW
                user32.SetParent(hwnd, workerw)
                
                # Đảm bảo widget vẫn hiển thị
                user32.ShowWindow(hwnd, SW_SHOW)
                
                # Set vị trí lại
                screen = QApplication.primaryScreen().geometry()
                user32.SetWindowPos(
                    hwnd, 0,
                    10, 10,
                    self.width(), self.height(),
                    SWP_SHOWWINDOW
                )
            else:
                pass
                
        except Exception as e:
            pass
            import traceback
            traceback.print_exc()
    
    def showEvent(self, event):
        super().showEvent(event)
    

    
    def manual_hide(self):
        """Ẩn widget khi bấm nút -"""
        self._manually_hidden = True
        self.hide()
    
    def show_widget(self):
        """Hiện widget và xóa flag ẩn"""
        self._manually_hidden = False
        self.show()
        QTimer.singleShot(500, self._attach_to_desktop)
    
    def move_to_top_left(self):
        self.move(10, 10)
    
    def _attach_to_desktop(self):
        """Gắn widget vào Progman (desktop) để chống Win+D"""
        try:
            hwnd = int(self.winId())
            
            # Lưu vị trí và size
            old_pos = self.pos()
            old_size = self.size()
            
            # Tìm Progman window (desktop shell)
            progman = user32.FindWindowW("Progman", None)
            if not progman:
                return
            
            # GẮN TRỰC TIẾP VÀO PROGMAN (không vào WorkerW)
            result = user32.SetParent(hwnd, progman)
            if result == 0:
                return
            
            # Set extended style để không bị Win+D ẩn
            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x00080000
            WS_EX_TRANSPARENT = 0x00000020  # Không dùng - sẽ không click được
            WS_EX_NOACTIVATE = 0x08000000
            
            ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            new_ex_style = ex_style | WS_EX_LAYERED | WS_EX_NOACTIVATE
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_ex_style)
            
            # Set alpha = 255 (opaque) để visible
            LWA_ALPHA = 0x00000002
            user32.SetLayeredWindowAttributes(hwnd, 0, 255, LWA_ALPHA)
            
            # Set WS_CHILD style
            GWL_STYLE = -16
            WS_VISIBLE = 0x10000000
            WS_CHILD = 0x40000000
            
            style = user32.GetWindowLongW(hwnd, GWL_STYLE)
            new_style = (style | WS_VISIBLE | WS_CHILD) & ~0x00C00000  # Remove WS_CAPTION
            user32.SetWindowLongW(hwnd, GWL_STYLE, new_style)
            
            # Force show
            user32.ShowWindow(hwnd, SW_SHOW)
            
            # Set vị trí (client coordinates của Progman)
            user32.SetWindowPos(
                hwnd, 0,
                old_pos.x(), old_pos.y(),
                old_size.width(), old_size.height(),
                SWP_SHOWWINDOW
            )
            
            # Force repaint
            user32.UpdateWindow(hwnd)
                
        except Exception as e:
            pass
            import traceback
            traceback.print_exc()
    
    def open_login(self):
        """Mở cửa sổ login"""
        self.login_window = LoginWindow(
            self.data_manager, 
            self.cookie_manager,
            self.on_login_done
        )
        self.login_window.login_required.connect(self.on_login_required)
        self.login_window.show()
    
    def refresh_schedule(self):
        """Refresh lịch học (dùng cookies đã lưu)"""
        if self.cookie_manager.has_cookies():
            self.login_window = LoginWindow(
                self.data_manager,
                self.cookie_manager,
                self.on_login_done,
                auto_mode=True
            )
            self.login_window.login_required.connect(self.on_login_required)
            self.login_window.show()
        else:
            self.open_login()
    
    def go_prev_week(self):
        """Chuyển sang tuần trước"""
        print(f"🔙 Chuyển sang tuần trước (offset: {self.current_week_offset - 1})")
        self.current_week_offset -= 1
        self.update_week_label()
        self.update_grid_headers()  # Cập nhật header với ngày mới
        self.refresh_all_cells()  # Refresh cells với week_dates mới
    
    def go_next_week(self):
        """Chuyển sang tuần sau"""
        print(f"▶️ Chuyển sang tuần sau (offset: {self.current_week_offset + 1})")
        self.current_week_offset += 1
        self.update_week_label()
        
        # Fetch và merge data nếu có cookies
        if self.cookie_manager.has_cookies():
            self.fetch_and_merge_week(self.current_week_offset)
        
        # Cập nhật hiển thị
        self.update_grid_headers()
        self.refresh_all_cells()
    
    def go_current_week(self):
        """Về tuần hiện tại"""
        self.current_week_offset = 0
        self.update_week_label()
        self.update_grid_headers()
        self.refresh_all_cells()
    
    def update_week_label(self):
        """Cập nhật label hiển thị tuần"""
        if self.current_week_offset == 0:
            self.week_label.setText("Tuần này")
        else:
            # Lấy ngày thứ 2 của tuần đó
            week_dates = self.data_manager.get_week_dates_from_offset(self.current_week_offset)
            monday_date = week_dates.get(0, '')
            self.week_label.setText(f"tuan{monday_date}")
    
    def update_grid_headers(self):
        """Cập nhật header grid với ngày tháng mới"""
        # Tính week_dates mới
        self.current_week_dates = self.data_manager.get_week_dates_from_offset(self.current_week_offset)
        
        # Cập nhật header cells (row 0, col 1-7)
        grid = self.centralWidget().findChild(QGridLayout)
        if not grid:
            return
        
        today = datetime.now()
        today_str = today.strftime("%d/%m/%Y")
        
        for i in range(7):
            # Lấy item tại row 0, col i+1
            item = grid.itemAtPosition(0, i + 1)
            if item and item.widget():
                label = item.widget()
                full_date = self.current_week_dates.get(i, '??/??/????')
                # Lấy dd/mm từ full date dd/mm/yyyy
                if '/' in full_date and len(full_date) >= 10:
                    date_str = full_date[:5]  # Lấy 5 ký tự đầu: dd/mm
                else:
                    date_str = '??/??'
                
                is_today = self.current_week_dates.get(i, '') == today_str
                
                label.setText(f"{DAYS[i]}\n{date_str}")
                
                bg = COLORS['accent'] if is_today else COLORS['header_bg']
                label.setStyleSheet(f"""
                    background: {bg};
                    color: white;
                    font-weight: bold;
                    padding: 8px 6px;
                    border-radius: 5px;
                    font-size: 12px;
                """)
    
    def fetch_and_merge_week(self, week_offset):
        """Fetch lịch tuần mới và merge vào data"""
        # Load cookies mới
        cookies = self.cookie_manager.load_cookies()
        
        if not cookies:
            if self.tray:
                self.tray.showMessage(
                    "IUH Schedule",
                    "Cần đăng nhập để lấy lịch tuần khác",
                    QSystemTrayIcon.Warning,
                    3000
                )
            return
        
        # Import ở đây để tránh circular import
        from .constants import get_schedule_url_for_week
        import requests
        
        url = get_schedule_url_for_week(week_offset)
        
        if self.tray:
            self.tray.showMessage(
                "IUH Schedule",
                f"Đang lấy lịch tuần {'+' if week_offset > 0 else ''}{week_offset}...",
                QSystemTrayIcon.Information,
                2000
            )
        
        try:
            cookies_dict = {c['name']: c['value'] for c in cookies}
            
            response = requests.get(url, cookies=cookies_dict, timeout=30)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                # Parse lịch mới với auto_save=False
                from .managers import DataManager
                temp_dm = DataManager()
                
                # Không load data cũ
                temp_dm.schedule = []
                temp_dm.tasks = []
                
                # Parse KHÔNG tự động save
                count = temp_dm.parse_schedule_html(response.text, auto_save=False)
                
                if count > 0:
                    # Merge vào data hiện tại (không xóa lịch cũ)
                    # Lọc duplicate dựa trên date + subject + tiet
                    existing_keys = set()
                    for item in self.data_manager.schedule:
                        key = (item.get('date', ''), item.get('subject', ''), item.get('tiet', ''), item.get('day', -1))
                        existing_keys.add(key)
                    
                    new_count = 0
                    for item in temp_dm.schedule:
                        key = (item.get('date', ''), item.get('subject', ''), item.get('tiet', ''), item.get('day', -1))
                        if key not in existing_keys:
                            self.data_manager.schedule.append(item)
                            existing_keys.add(key)
                            new_count += 1
                            print(f"  ➕ New: {item.get('subject', 'N/A')[:30]} - {item.get('date', 'no date')} - {item.get('tiet', 'N/A')}")
                        else:
                            print(f"  ⏭️ Skip duplicate: {item.get('subject', 'N/A')[:30]}")
                    
                    self.data_manager.save()
                    self.refresh_cells()
                    
                    if self.tray:
                        self.tray.showMessage(
                            "IUH Schedule",
                            f"✅ Đã thêm {new_count} môn học mới\nTổng: {len(self.data_manager.schedule)} môn",
                            QSystemTrayIcon.Information,
                            3000
                        )
                else:
                    if self.tray:
                        self.tray.showMessage(
                            "IUH Schedule",
                            "Không tìm thấy lịch cho tuần này",
                            QSystemTrayIcon.Warning,
                            3000
                        )
            else:
                if self.tray:
                    self.tray.showMessage(
                        "IUH Schedule",
                        f"Lỗi HTTP {response.status_code}",
                        QSystemTrayIcon.Critical,
                        3000
                    )
        except Exception as e:
            pass
            import traceback
            traceback.print_exc()
            if self.tray:
                self.tray.showMessage(
                    "IUH Schedule",
                    f"Lỗi: {str(e)[:50]}",
                    QSystemTrayIcon.Critical,
                    3000
                )
    
    def auto_refresh_schedule(self):
        """Tự động refresh lịch"""
        print("🔄 Auto-refreshing schedule...")
        self.refresh_schedule()
    
    def on_login_required(self):
        """Xử lý khi cần đăng nhập lại (cookies hết hạn)"""
        print("🔔 Hiện thông báo cần đăng nhập lại")
        if self.tray:
            self.tray.showMessage(
                "🔐 Cần đăng nhập lại",
                "Cookies đã hết hạn. Click để đăng nhập lại và cập nhật lịch học.",
                QSystemTrayIcon.Warning,
                5000
            )
    
    def set_tray(self, tray):
        """Lưu reference đến system tray"""
        self.tray = tray
    
    def on_login_done(self):
        self.refresh_all_cells()
        self.show_widget()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event):
        if self.drag_pos and event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
    
    def mouseReleaseEvent(self, event):
        self.drag_pos = None
