# IUH Schedule Widget

Desktop widget hiển thị lịch học/công việc dạng bảng, tích hợp với trang web IUH (Đại học Công Nghiệp TP.HCM).

## Tính năng

- 📅 **Hiển thị lịch dạng bảng**: Giao diện 7 ngày x 3 ca (Sáng, Chiều, Tối)
- 📌 **Dính desktop**: Widget luôn hiển thị trên desktop, không đè lên ứng dụng khác
- ✏️ **Quản lý công việc**: Thêm, sửa, xóa công việc cho từng ca
- 🔐 **Auto-login**: Đăng nhập tự động bằng cookies từ website IUH
- 💾 **Lưu dữ liệu**: Dữ liệu được lưu local vào file JSON
- 🖥️ **System tray**: Chạy nền với icon trên system tray

## Giao diện

Widget được thiết kế theo màu sắc của trang web IUH:
- Màu xanh header: `#5a9fd4`
- Màu xanh lá lịch học: `#d4edda`
- Màu vàng công việc: `#fff3cd`

## Yêu cầu hệ thống

- Windows (được tối ưu cho Windows)
- Python 3.8+
- PySide6

## Cài đặt

1. **Clone repository**:
   ```bash
   git clone <repository-url>
   cd Schedule
   ```

2. **Cài đặt dependencies**:
   ```bash
   pip install PySide6
   ```

## Sử dụng

### Chạy trực tiếp

```bash
python app.py
```

### Build thành file exe

Sử dụng PyInstaller:

```bash
pip install pyinstaller
pyinstaller build_app.spec
```

File exe sẽ được tạo trong thư mục `dist/`.

## Cấu trúc thư mục

```
Schedule/
│
├── app.py                    # Entry point chính
├── bridge.py                 # Bridge code (nếu cần)
├── build_app.spec            # PyInstaller spec file
├── schedule_data.json        # Dữ liệu lịch (tự động tạo)
├── cookies.json              # Cookies đăng nhập (tự động tạo)
├── settings.json             # Cài đặt (tự động tạo)
│
└── components/
    ├── __init__.py           # Export các components
    ├── constants.py          # Constants và config
    ├── dialogs.py            # Dialog windows
    ├── login.py              # Login window
    ├── managers.py           # Data/Cookie/Settings managers
    └── widgets.py            # Main schedule widget
```

## Components

### Managers
- **DataManager**: Quản lý dữ liệu lịch (đọc/ghi JSON)
- **CookieManager**: Quản lý cookies đăng nhập
- **SettingsManager**: Quản lý cài đặt ứng dụng

### UI Components
- **ScheduleWidget**: Widget hiển thị bảng lịch chính
- **LoginWindow**: Cửa sổ đăng nhập
- **Dialogs**: Các dialog thêm/sửa công việc

## Cách hoạt động

1. **Khởi động**: Ứng dụng đọc dữ liệu từ `schedule_data.json`
2. **Hiển thị**: Widget hiển thị lịch dạng bảng 7x3
3. **Tương tác**: Click vào ô để thêm/sửa/xóa công việc
4. **Đồng bộ**: (Nếu có cookies) tự động đồng bộ với trang IUH
5. **Lưu trữ**: Mọi thay đổi được lưu vào file JSON

## Đăng nhập IUH

Để sử dụng tính năng auto-login:

1. Mở cửa sổ Login từ system tray
2. Nhập thông tin đăng nhập IUH
3. Cookies sẽ được lưu vào `cookies.json`
4. Ứng dụng sẽ tự động đăng nhập ở các lần sau

## System Tray

Right-click vào icon trên system tray để:
- Hiện/ẩn widget
- Mở cửa sổ login
- Làm mới dữ liệu
- Cài đặt
- Thoát ứng dụng

## Phím tắt

*(Có thể thêm sau)*

## Troubleshooting

### Widget không hiển thị
- Kiểm tra có lỗi trong console
- Thử xóa file `schedule_data.json` và khởi động lại

### Không đăng nhập được
- Kiểm tra URL: `https://sv.iuh.edu.vn`
- Xóa file `cookies.json` và đăng nhập lại
- Kiểm tra kết nối internet

### Lỗi encoding (Windows)
- Ứng dụng đã fix encoding UTF-8 cho Windows console
- Nếu vẫn lỗi, chạy trong terminal hỗ trợ UTF-8

## Phát triển

### Thêm tính năng mới

1. Thêm constants vào [constants.py](components/constants.py)
2. Thêm business logic vào [managers.py](components/managers.py)
3. Thêm UI vào [widgets.py](components/widgets.py)
4. Test và build lại

### Dependencies

Thêm dependencies vào `build_app.spec` trong phần `hiddenimports` nếu cần.

## License

*(Thêm license nếu có)*

## Đóng góp

*(Thêm hướng dẫn đóng góp nếu là dự án mở)*

## Liên hệ

0986966745 - Bá Sơn

---

**Lưu ý**: Đây là ứng dụng cá nhân, không liên quan chính thức đến Đại học Công Nghiệp TP.HCM.
