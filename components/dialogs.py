"""
Dialogs: AddTaskDialog và các dialog khác
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QComboBox
)
from PySide6.QtCore import Qt, QTime
from PySide6.QtGui import QCursor

from .constants import TIET_TIME, PERIOD_TIME


class AddTaskDialog(QDialog):
    """Dialog thêm/sửa task - UI đơn giản 3 field"""
    
    def __init__(self, parent, day=0, period=0, edit_task=None, existing_tiets=None):
        super().__init__(parent)
        self.edit_task = edit_task
        self.day = day
        self.period = period
        self.existing_tiets = existing_tiets or []
        
        title = "✏️ Sửa công việc" if edit_task else "➕ Thêm công việc"
        self.setWindowTitle(title)
        self.setFixedSize(450, 420)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f0f4f8);
                border-radius: 20px;
                border: 3px solid #5a9fd4;
            }
            QLineEdit {
                padding: 15px 18px;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                font-size: 15px;
                background: #ffffff;
                color: #000000;
                selection-background-color: #5a9fd4;
            }
            QLineEdit:focus {
                border-color: #5a9fd4;
                background: #ffffff;
            }
            QLineEdit:hover {
                border-color: #aaa;
            }
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #333333;
                background: transparent;
                padding-left: 2px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(30, 25, 30, 25)
        
        # Header với gradient
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a9fd4, stop:1 #7db8e8);
                border-radius: 12px;
                padding: 15px;
                margin-bottom: 5px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 12, 15, 12)
        
        header = QLabel("📋 " + title)
        header.setStyleSheet("""
            font-size: 22px; 
            font-weight: bold; 
            color: #ffffff; 
            background: transparent;
            letter-spacing: 1px;
        """)
        header_layout.addWidget(header)
        header_layout.addStretch()
        
        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(32, 32)
        close_btn.clicked.connect(self.reject)
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.2);
                border: none;
                border-radius: 16px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.4);
            }
        """)
        header_layout.addWidget(close_btn)
        layout.addWidget(header_frame)
        
        # 1. Tên công việc
        title_label = QLabel("📝 Tên công việc")
        layout.addWidget(title_label)
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Nhập tên công việc...")
        self.title_input.setMinimumHeight(50)
        layout.addWidget(self.title_input)
        
        # 2. Giờ - dropdown chọn thời gian mỗi 15 phút
        min_time, max_time, default_time = self._calculate_time_range()
        
        time_label = QLabel("🕐 Giờ thực hiện")
        layout.addWidget(time_label)
        self.time_input = QComboBox()
        self.time_input.setMinimumHeight(50)
        self.time_input.setStyleSheet("""
            QComboBox {
                padding: 12px 16px;
                padding-right: 45px;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                background: #f8f9fa;
                color: #000000;
                min-height: 26px;
            }
            QComboBox:focus {
                border-color: #5a9fd4;
                background: #ffffff;
            }
            QComboBox:hover {
                border-color: #aaa;
            }
            QComboBox::drop-down {
                border: none;
                width: 40px;
                subcontrol-position: right center;
                background: transparent;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 8px solid #333;
                margin-right: 15px;
            }
            QComboBox QAbstractItemView {
                background: #ffffff;
                border: 2px solid #5a9fd4;
                border-radius: 8px;
                selection-background-color: #5a9fd4;
                selection-color: #ffffff;
                padding: 8px;
                font-size: 15px;
                color: #000000;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 10px 15px;
                min-height: 32px;
                color: #000000;
                border-radius: 4px;
            }
            QComboBox QAbstractItemView::item:hover {
                background: #e3f2fd;
                color: #000000;
            }
            QComboBox QAbstractItemView::item:selected {
                background: #5a9fd4;
                color: #ffffff;
            }
        """)
        
        self._populate_time_options(min_time, max_time, default_time)
        layout.addWidget(self.time_input)
        
        # 3. Ghi chú
        note_label = QLabel("📋 Ghi chú (tùy chọn)")
        layout.addWidget(note_label)
        self.note_input = QLineEdit()
        self.note_input.setPlaceholderText("Thêm ghi chú...")
        self.note_input.setMinimumHeight(50)
        layout.addWidget(self.note_input)
        
        layout.addStretch()
        
        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(15)
        
        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setMinimumHeight(52)
        cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 15px 35px;
                border: 2px solid #dc3545;
                border-radius: 12px;
                font-size: 15px;
                font-weight: bold;
                background: #ffffff;
                color: #dc3545;
            }
            QPushButton:hover {
                background: #dc3545;
                color: #ffffff;
            }
            QPushButton:pressed {
                background: #c82333;
            }
        """)
        btn_row.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Lưu công việc" if not edit_task else "✅ Cập nhật")
        save_btn.clicked.connect(self.save_task)
        save_btn.setMinimumHeight(52)
        save_btn.setCursor(QCursor(Qt.PointingHandCursor))
        save_btn.setStyleSheet("""
            QPushButton {
                padding: 15px 35px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #28a745, stop:1 #34c759);
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 12px;
                font-size: 15px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #218838, stop:1 #2db84d);
            }
            QPushButton:pressed {
                background: #1e7e34;
            }
        """)
        btn_row.addWidget(save_btn)
        
        layout.addLayout(btn_row)
        
        # Fill data if editing
        if edit_task:
            self.title_input.setText(edit_task.get('title', ''))
            time_str = edit_task.get('time', '08:00')
            idx = self.time_input.findText(time_str)
            if idx >= 0:
                self.time_input.setCurrentIndex(idx)
            self.note_input.setText(edit_task.get('note', ''))
        
        self.title_input.setFocus()
    
    def _populate_time_options(self, min_time, max_time, default_time):
        """Tạo danh sách thời gian mỗi 15 phút"""
        self.time_input.clear()
        
        current = QTime(min_time.hour(), (min_time.minute() // 15) * 15)
        if current < min_time:
            current = current.addSecs(15 * 60)
        
        default_idx = 0
        idx = 0
        
        while current <= max_time:
            time_str = current.toString("HH:mm")
            self.time_input.addItem(time_str)
            
            if current <= default_time:
                default_idx = idx
            
            current = current.addSecs(15 * 60)
            idx += 1
        
        if self.time_input.count() == 0:
            self.time_input.addItem(min_time.toString("HH:mm"))
        
        self.time_input.setCurrentIndex(default_idx)
    
    def _calculate_time_range(self):
        """Tính khoảng thời gian cho phép dựa trên các tiết đã có"""
        period_start_h, period_start_m, period_end_h, period_end_m = PERIOD_TIME.get(self.period, (6, 30, 21, 0))
        
        min_time = QTime(period_start_h, period_start_m)
        max_time = QTime(period_end_h, period_end_m)
        
        if self.existing_tiets:
            latest_end = None
            for tiet in self.existing_tiets:
                if tiet in TIET_TIME:
                    _, _, end_h, end_m = TIET_TIME[tiet]
                    tiet_end = QTime(end_h, end_m)
                    if latest_end is None or tiet_end > latest_end:
                        latest_end = tiet_end
            
            if latest_end and latest_end > min_time:
                min_time = latest_end
        
        default_time = min_time
        
        return min_time, max_time, default_time
    
    def save_task(self):
        """Validate và lưu task"""
        title = self.title_input.text().strip()
        if not title:
            self.title_input.setStyleSheet("""
                QLineEdit {
                    padding: 15px 18px;
                    border: 2px solid #dc3545;
                    border-radius: 12px;
                    font-size: 15px;
                    background: #fff0f0;
                    color: #000000;
                }
            """)
            self.title_input.setPlaceholderText("⚠️ Bạn cần nhập tên công việc!")
            self.title_input.setFocus()
            return
        self.accept()
    
    def get_data(self):
        return {
            'title': self.title_input.text().strip(),
            'day': self.day,
            'period': self.period,
            'time': self.time_input.currentText(),
            'note': self.note_input.text().strip()
        }
    
    def mousePressEvent(self, event):
        """Đóng dialog khi click ra ngoài"""
        # Với frameless dialog, chỉ cần reject vì không có vùng ngoài
        # Nếu muốn giữ dialog, user phải click vào các widget bên trong
        super().mousePressEvent(event)
