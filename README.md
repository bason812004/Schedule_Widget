# IUH Schedule Widget

Desktop widget hiển thị lịch học/công việc dạng bảng, tích hợp với trang web IUH (Đại học Công Nghiệp TP.HCM).

## Tính năng

- 📅 **Hiển thị lịch dạng bảng**: Giao diện 7 ngày x 3 ca (Sáng, Chiều, Tối)
- 📌 **Dính desktop**: Widget dính vào desktop (Progman), không đè lên ứng dụng khác
- ✏️ **Quản lý công việc**: Thêm, sửa, xóa công việc tùy chỉnh cho từng ca
- 🔄 **Xem nhiều tuần**: Điều hướng qua lại giữa các tuần (prev/next week)
- 🔐 **Auto-login**: Đăng nhập tự động bằng cookies, tự động fetch lịch từ IUH
- 💾 **Lưu theo tuần**: Dữ liệu được tổ chức theo tuần trong file JSON
- 🖥️ **System tray**: Chạy nền với icon trên system tray, double-click để hiện/ẩn
- ⏰ **Auto refresh**: Tự động cập nhật lịch định kỳ (cấu hình được)
- 🚀 **Chạy cùng Windows**: Tùy chọn chạy tự động khi khởi động Windows

## Giao diện

Widget được thiết kế theo màu sắc của trang web IUH:
- Màu xanh header: `#5a9fd4`
- Màu xanh lá lịch học: `#d4edda`
- Màu vàng công việc: `#fff3cd`

## Yêu cầu hệ thống

- Windows 10/11 (được tối ưu cho Windows, sử dụng Windows API)
- Python 3.8+

## Cài đặt

1. **Clone repository**:
   ```bash
   git clone https://github.com/bason812004/Schedule_Widget.git
   cd Schedule_Widget
   ```

2. **Tạo virtual environment** (khuyến nghị):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Cài đặt dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Sử dụng

### Chạy trực tiếp từ Python

```bash
python app.py
```

### Build thành file .exe

Sử dụng script PowerShell có sẵn:

```powershell
.\build.ps1
```

Hoặc build thủ công:

```bash
pip install pyinstaller
pyinstaller --clean IUH_Schedule_Widget.spec
```

File exe sẽ được tạo trong thư mục `dist/IUH_Schedule_Widget.exe`.

## Cấu trúc thư mục

```
Schedule_Widget/
│
├── app.py                    # Entry point chính
├── build.ps1                 # Script build tự động (PowerShell)
├── IUH_Schedule_Widget.spec  # PyInstaller spec file
├── requirements.txt          # Python dependencies
├── README.md                 # Tài liệu này
│
├── schedule_data.json        # Dữ liệu lịch theo tuần (tự động tạo)
├── cookies.json              # Cookies đăng nhập (tự động tạo)
├── settings.json             # Cài đặt app (tự động tạo)
│
└── components/
    ├── __init__.py           # Export các components
    ├── constants.py          # Constants, config, URLs
    ├── dialogs.py            # Dialog windows (Add/Edit task)
    ├── login.py              # Login window với WebView
    ├── managers.py           # Data/Cookie/Settings managers
    └── widgets.py            # ScheduleCell và ScheduleWidget
```

## Components

### Managers (`managers.py`)
- **DataManager**: Quản lý dữ liệu lịch (đọc/ghi JSON theo tuần), parse HTML từ IUH
- **CookieManager**: Quản lý cookies đăng nhập, load/save/clear cookies
- **SettingsManager**: Quản lý cài đặt ứng dụng, Windows startup registry

### UI Components
- **ScheduleWidget** (`widgets.py`): Widget chính hiển thị bảng lịch 7x3, điều hướng tuần
- **ScheduleCell** (`widgets.py`): Ô đơn trong bảng, hiển thị lịch + tasks cho 1 ngày/ca
- **LoginWindow** (`login.py`): Cửa sổ đăng nhập với QWebEngineView
- **AddTaskDialog** (`dialogs.py`): Dialog thêm/sửa công việc

## Cách hoạt động

1. **Khởi động**: 
   - Đọc dữ liệu từ `schedule_data.json` (tổ chức theo tuần)
   - Nếu có cookies và có dữ liệu → hiển thị widget + auto-fetch lịch
   - Nếu không có cookies → hiển thị LoginWindow

2. **Hiển thị**: 
   - Widget hiển thị lịch dạng bảng 7 ngày x 3 ca
   - Header có nút điều hướng tuần (◀ ▶) và nút refresh
   - Mỗi ô hiển thị lịch học (xanh lá) và tasks (vàng)

3. **Tương tác**: 
   - Click trái vào ô trống → thêm công việc mới
   - Click phải vào task → menu sửa/xóa
   - Điều hướng tuần để xem lịch các tuần khác

4. **Đồng bộ**: 
   - Nếu có cookies → tự động fetch lịch từ IUH khi refresh
   - Parse HTML từ `sv.iuh.edu.vn/lich-theo-tuan.html`
   - Merge dữ liệu theo tuần vào file JSON

5. **Lưu trữ**: 
   - Dữ liệu được tổ chức theo key tuần: `"tuan26/01/2026"`
   - Mỗi tuần có `schedule` (lịch học) và `tasks` (công việc)
   - Tự động lưu khi có thay đổi

6. **Desktop Integration**:
   - Widget attach vào Progman (desktop window của Windows)
   - Sử dụng Windows API (user32.dll) để dính vào desktop
   - System tray icon với menu điều khiển

## Đăng nhập IUH

Để sử dụng tính năng tự động lấy lịch:

1. Mở cửa sổ Login từ system tray menu hoặc khi khởi động lần đầu
2. Nhập thông tin đăng nhập IUH vào trang web
3. Cookies sẽ được tự động lưu vào `cookies.json`
4. Widget sẽ tự động fetch lịch và hiển thị
5. Các lần sau ứng dụng sẽ tự động đăng nhập

**Lưu ý**: Cookies có thời hạn, nếu hết hạn cần đăng nhập lại.

## System Tray Menu

Right-click vào icon trên system tray để:
- **Hiện Widget**: Hiển thị widget nếu đang ẩn
- **Cập nhật lịch**: Fetch lịch mới từ IUH (cần cookies)
- **Đăng nhập lại**: Mở cửa sổ login để lấy cookies mới
- **Chạy cùng Windows**: Toggle auto-start khi khởi động Windows
- **Thoát**: Đóng hoàn toàn ứng dụng

**Double-click** vào icon để nhanh chóng hiện/ẩn widget.

## Các thao tác chính

### Xem lịch tuần khác
- Click nút **◀** để xem tuần trước
- Click nút **▶** để xem tuần sau  
- Click nút **📅** để quay về tuần hiện tại

### Thêm công việc
1. Click trái vào ô trống (hoặc ô đã có lịch)
2. Điền thông tin: tiêu đề, ghi chú, deadline
3. Click "Thêm" để lưu

### Sửa/Xóa công việc
1. Click phải vào công việc (khối màu vàng)
2. Chọn "Sửa" hoặc "Xóa" từ menu

### Refresh lịch
- Click nút 🔄 trên header
- Hoặc chọn "Cập nhật lịch" từ system tray
- Lịch sẽ được fetch từ IUH và merge với dữ liệu hiện tại

## Troubleshooting

### Widget không hiển thị
- Kiểm tra console có báo lỗi không
- Widget có thể bị ẩn sau desktop icons, thử di chuyển icons
- Thử khởi động lại app

### Widget không dính vào desktop
- Windows API có thể bị block bởi security software
- Thử chạy với quyền administrator (click phải → Run as administrator)
- Kiểm tra xem có app khác đang can thiệp vào Progman không

### Không đăng nhập được IUH
- Kiểm tra kết nối internet
- Thử truy cập `https://sv.iuh.edu.vn` trên browser
- Xóa `cookies.json` và thử đăng nhập lại
- Website IUH có thể đang bảo trì

### Không lấy được lịch (fetch failed)
- Kiểm tra cookies còn hạn không (đăng nhập lại nếu cần)
- Format HTML của IUH có thể thay đổi
- Kiểm tra console log để debug

### Lỗi khi build exe
- Đảm bảo đã cài đủ dependencies: `pip install -r requirements.txt`
- Xóa folder `build/` và `dist/` rồi build lại
- Kiểm tra `IUH_Schedule_Widget.spec` đúng cấu hình

### Lỗi encoding (Windows)
- App đã tự động fix encoding UTF-8 cho Windows console
- Nếu vẫn lỗi khi chạy từ terminal, dùng Windows Terminal hoặc VS Code terminal

## Phát triển

### Cấu trúc dữ liệu

File `schedule_data.json`:
```json
{
  "tuan26/01/2026": {
    "schedule": [
      {
        "subject": "Tên môn học",
        "tiet": "7-9",
        "day": "Thứ 2",
        "room": "H3.1.1",
        "date": "27/01/2026"
      }
    ],
    "tasks": [
      {
        "id": 1738315620.123,
        "title": "Làm bài tập",
        "day": "Thứ 3",
        "period": "Chiều",
        "note": "Deadline 10/02",
        "done": false,
        "date": "28/01/2026"
      }
    ]
  }
}
```

### Thêm tính năng mới

1. Constants → [constants.py](components/constants.py)
2. Business logic → [managers.py](components/managers.py)  
3. UI components → [widgets.py](components/widgets.py) hoặc [dialogs.py](components/dialogs.py)
4. Test kỹ trước khi build

### Build configuration

File `IUH_Schedule_Widget.spec`:
- `datas`: Files được copy vào exe (hiện tại: `schedule_data.json`)
- `console=False`: Chạy không có console window
- `upx=True`: Nén exe bằng UPX

### Dependencies

- **PySide6**: Qt framework cho Python (UI)
- **requests**: HTTP client (fetch lịch từ IUH)
- **beautifulsoup4**: Parse HTML (trong managers.py)

Cài thêm dependencies:
```bash
pip install <package>
pip freeze > requirements.txt
```

## Các file quan trọng

- **schedule_data.json**: Lưu dữ liệu lịch theo tuần
- **cookies.json**: Lưu cookies đăng nhập (tự động tạo khi login)
- **settings.json**: Lưu cài đặt app (auto_refresh_hours, run_at_startup)
- **.gitignore**: Đã cấu hình ignore build/, dist/, __pycache__/, .pyc files

## Roadmap / TODO

- [ ] Notification cho lịch sắp tới
- [ ] Export lịch ra PDF/Excel
- [ ] Dark mode
- [ ] Phím tắt toàn cục
- [ ] Sync giữa nhiều thiết bị (cloud)
- [ ] Cải thiện UI/UX

## Known Issues

- Widget có thể bị ẩn sau desktop icons trên một số cấu hình Windows
- Cookies IUH có thời hạn ngắn, cần đăng nhập lại thường xuyên
- Parse HTML phụ thuộc vào format của website IUH (có thể thay đổi)

## License

MIT License - Dự án cá nhân, không liên quan chính thức đến Đại học Công Nghiệp TP.HCM.

## Đóng góp

Mọi đóng góp đều được chào đón! 
- Fork repository
- Tạo branch mới (`git checkout -b feature/AmazingFeature`)
- Commit changes (`git commit -m 'Add some AmazingFeature'`)
- Push to branch (`git push origin feature/AmazingFeature`)
- Mở Pull Request

## Liên hệ

**Bá Sơn** - 0986966745

Repository: [https://github.com/bason812004/Schedule_Widget](https://github.com/bason812004/Schedule_Widget)

---

**Lưu ý**: Đây là ứng dụng cá nhân để hỗ trợ sinh viên IUH quản lý lịch học. Không liên quan chính thức đến Đại học Công Nghiệp TP.HCM.
