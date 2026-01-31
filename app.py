"""
IUH Schedule Widget - Desktop Widget dạng bảng
- Dính desktop, KHÔNG đè lên ứng dụng khác
- Giao diện bảng giống web IUH (7 ngày x 3 ca)
- Thêm/sửa/xóa công việc
- Auto-login với cookies
"""
import sys

# Fix encoding cho Windows console (chỉ khi có console)
if sys.platform == 'win32' and sys.stdout is not None:
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor

from components import (
    CookieManager, SettingsManager, DataManager,
    ScheduleWidget, LoginWindow
)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("IUH Schedule Widget")
    app.setQuitOnLastWindowClosed(False)
    
    # Managers
    data_manager = DataManager()
    cookie_manager = CookieManager()
    settings_manager = SettingsManager()
    
    # Widget
    widget = ScheduleWidget(data_manager, cookie_manager, settings_manager)
    
    # System tray với icon
    tray = QSystemTrayIcon()
    
    # Tạo icon đơn giản từ text
    pixmap = QPixmap(64, 64)
    pixmap.fill(QColor(90, 159, 212))  # Màu xanh IUH
    painter = QPainter(pixmap)
    painter.setPen(QColor(255, 255, 255))
    from PySide6.QtGui import QFont
    font = QFont("Arial", 32, QFont.Bold)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), 0x84, "📅")  # AlignCenter
    painter.end()
    
    tray.setIcon(QIcon(pixmap))
    tray.setToolTip("IUH Schedule Widget - Double-click để hiện/ẩn")
    
    # Kết nối widget với tray để hiện notification
    widget.set_tray(tray)
    
    # Click notification để mở login
    tray.messageClicked.connect(widget.open_login)
    
    # Tray menu
    tray_menu = QMenu()
    
    show_action = tray_menu.addAction("📅 Hiện Widget")
    show_action.triggered.connect(widget.show_widget)
    
    refresh_action = tray_menu.addAction("🔄 Cập nhật lịch")
    refresh_action.triggered.connect(widget.refresh_schedule)
    
    login_action = tray_menu.addAction("🔐 Đăng nhập lại")
    login_action.triggered.connect(widget.open_login)
    
    tray_menu.addSeparator()
    
    # Startup checkbox
    startup_action = tray_menu.addAction("🚀 Chạy cùng Windows")
    startup_action.setCheckable(True)
    startup_action.setChecked(settings_manager.settings.get('run_at_startup', False))
    startup_action.triggered.connect(lambda checked: settings_manager.set_startup(checked))
    
    tray_menu.addSeparator()
    
    quit_action = tray_menu.addAction("🚪 Thoát")
    quit_action.triggered.connect(app.quit)
    
    tray.setContextMenu(tray_menu)
    tray.activated.connect(lambda reason: widget.show_widget() if reason == QSystemTrayIcon.DoubleClick else None)
    tray.show()
    
    # Kiểm tra dữ liệu từ JSON
    has_data = bool(data_manager.schedule or data_manager.tasks)
    
    if has_data:
        widget.show()
        
        # Gắn vào Progman sau 500ms
        QTimer.singleShot(500, widget._attach_to_desktop)
        
        # Auto refresh if has cookies
        if cookie_manager.has_cookies():
            QTimer.singleShot(2000, widget.refresh_schedule)
    else:
        if cookie_manager.has_cookies():
            login = LoginWindow(data_manager, cookie_manager, widget.show_widget, auto_mode=True)
            login.login_required.connect(widget.on_login_required)
            login.show()
        else:
            login = LoginWindow(data_manager, cookie_manager, widget.show_widget)
            login.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
