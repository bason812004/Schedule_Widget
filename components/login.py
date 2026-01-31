"""
LoginWindow: Cửa sổ đăng nhập IUH
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QCheckBox
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineProfile
from PySide6.QtCore import Qt, QUrl, QTimer, Signal
from PySide6.QtNetwork import QNetworkCookie

from .constants import SCHEDULE_URL, LOGIN_URL


class LoginWindow(QMainWindow):
    """Cửa sổ đăng nhập IUH với auto-save cookies"""
    
    login_success = Signal()
    schedule_fetched = Signal(int)
    login_required = Signal()
    
    def __init__(self, data_manager, cookie_manager, on_success=None, auto_mode=False):
        super().__init__()
        self.data_manager = data_manager
        self.cookie_manager = cookie_manager
        self.on_success = on_success
        self.auto_mode = auto_mode
        self.cookies_to_save = []
        self.login_detected = False
        
        self.setWindowTitle("🔐 Đăng nhập IUH")
        self.resize(1100, 750)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(10, 8, 10, 8)
        toolbar.setSpacing(10)
        
        self.status = QLabel("🔴 Đăng nhập và TÌM menu 'LỊCH HỌC' hoặc 'THỚI KHÓA BIỂU' (sidebar), rồi bấm 'Lấy Lịch'")
        self.status.setStyleSheet("font-size: 13px; padding: 5px;")
        toolbar.addWidget(self.status)
        toolbar.addStretch()
        
        self.auto_fetch_cb = QCheckBox("Tự động lấy lịch")
        self.auto_fetch_cb.setChecked(True)
        self.auto_fetch_cb.setStyleSheet("font-size: 12px;")
        toolbar.addWidget(self.auto_fetch_cb)
        
        fetch_btn = QPushButton("📥 Lấy Lịch")
        fetch_btn.clicked.connect(self.fetch_schedule)
        fetch_btn.setStyleSheet("""
            QPushButton {
                background: #5a9fd4;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover { background: #4a8fc4; }
        """)
        toolbar.addWidget(fetch_btn)
        
        done_btn = QPushButton("✅ Xong")
        done_btn.clicked.connect(self.finish_login)
        done_btn.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover { background: #218838; }
        """)
        toolbar.addWidget(done_btn)
        
        layout.addLayout(toolbar)
        
        # WebView with profile for cookies
        self.profile = QWebEngineProfile("IUHProfile", self)
        self.webview = QWebEngineView()
        
        # Setup cookie tracking
        cookie_store = self.profile.cookieStore()
        cookie_store.cookieAdded.connect(self.on_cookie_added)
        
        # Load saved cookies
        if not auto_mode:
            self.load_saved_cookies()
        
        layout.addWidget(self.webview)
        
        self.webview.page().loadFinished.connect(self.on_load)
        
        # Start URL
        start_url = SCHEDULE_URL if cookie_manager.has_cookies() else LOGIN_URL
        self.webview.load(QUrl(start_url))
    
    def load_saved_cookies(self):
        """Load cookies đã lưu vào browser"""
        cookies = self.cookie_manager.load_cookies()
        cookie_store = self.profile.cookieStore()
        
        for c in cookies:
            cookie = QNetworkCookie()
            cookie.setName(c.get('name', '').encode())
            cookie.setValue(c.get('value', '').encode())
            cookie.setDomain(c.get('domain', ''))
            cookie.setPath(c.get('path', '/'))
            if c.get('secure'):
                cookie.setSecure(True)
            cookie_store.setCookie(cookie, QUrl(LOGIN_URL))
    
    def on_cookie_added(self, cookie):
        """Track cookies khi được thêm"""
        cookie_data = {
            'name': cookie.name().data().decode(),
            'value': cookie.value().data().decode(),
            'domain': cookie.domain(),
            'path': cookie.path(),
            'secure': cookie.isSecure()
        }
        
        for i, c in enumerate(self.cookies_to_save):
            if c['name'] == cookie_data['name'] and c['domain'] == cookie_data['domain']:
                self.cookies_to_save[i] = cookie_data
                return
        self.cookies_to_save.append(cookie_data)
    
    def on_load(self, success):
        url = self.webview.page().url().toString().lower()
        print(f"🔍 Page loaded: {url}")
        
        if not success:
            self.status.setText("❌ Lỗi tải trang")
            return
        
        if "dang-nhap" in url or "login" in url:
            self.status.setText("🔴 Vui lòng đăng nhập...")
            self.login_detected = False
            
            if self.auto_mode:
                print("⚠️ Cookies hết hạn! Cần đăng nhập lại...")
                self.login_required.emit()
                self.status.setText("⚠️ Cookies hết hạn! Vui lòng đăng nhập lại")
        else:
            if not self.login_detected:
                self.login_detected = True
                self.status.setText("🟢 Đã đăng nhập! Đang lưu cookies...")
                self.save_cookies()
            
            schedule_patterns = [
                "lich-hoc", "lichhoc", "lich-theo-tuan",
                "thoi-khoa-bieu", "thoikhoabieu",
                "schedule", "timetable", "tkb", "hoc-tap"
            ]
            
            is_schedule_page = any(pattern in url for pattern in schedule_patterns)
            
            if is_schedule_page:
                self.status.setText("🟢 Phát hiện trang lịch học! Đang tự động lấy dữ liệu...")
                if self.auto_fetch_cb.isChecked():
                    QTimer.singleShot(2000, self.fetch_schedule)
            else:
                self.status.setText("🟢 Đã đăng nhập! Tìm menu 'LỊCH HỌC' hoặc 'THỜI KHÓA BIỂU' và vào trang đó")
    
    def save_cookies(self):
        """Lưu cookies hiện tại"""
        if self.cookies_to_save:
            self.cookie_manager.save_cookies(self.cookies_to_save)
    
    def fetch_schedule(self):
        """Lấy HTML lịch học"""
        current_url = self.webview.page().url().toString()
        print(f"📍 Current URL: {current_url}")
        self.status.setText("📥 Đang lấy dữ liệu từ trang hiện tại...")
        self._do_fetch()
    
    def _do_fetch(self):
        get_html_js = "(function() { return document.body.innerHTML; })();"
        
        def on_html_received(html):
            if html and len(html) > 100:
                print(f"✅ Nhận HTML: {len(html)} chars")
                
                # Parse với merge_mode=True để KHÔNG xóa lịch cũ
                count = self.data_manager.parse_schedule_html(html, week_dates=None, auto_save=True, merge_mode=True)
                
                if count > 0:
                    self.status.setText(f"🟢 Thành công! Đã lấy {count} môn học")
                    self.schedule_fetched.emit(count)
                    
                    if self.auto_mode and count > 0:
                        QTimer.singleShot(1000, self.finish_login)
                else:
                    self.status.setText("❌ KHÔNG tìm thấy lịch. Vui lòng vào trang 'Lịch học' trước!")
            else:
                self.status.setText("❌ Trang trống - vui lòng reload trang lịch")
        
        self.webview.page().runJavaScript(get_html_js, on_html_received)
    
    def finish_login(self):
        self.save_cookies()
        self.hide()
        self.login_success.emit()
        if self.on_success:
            self.on_success()
