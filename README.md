# Privacy Screen for Gaming (Privacy Vignette)

Ứng dụng này giúp tạo ra một lớp phủ màn hình màu đen (hoặc làm mờ) trên màn hình chính, hoạt động như một lớp màn che khuất tầm nhìn từ xa.

## 🎯 Mục đích
- **Bảo vệ quyền riêng tư:** Hạn chế tầm nhìn của camera an ninh hoặc những người đứng ở khoảng cách xa không thể nhìn rõ màn hình của bạn.
- **Giải trí riêng tư:** Đặc biệt hữu ích khi bạn muốn chơi game hoặc xem phim tại nơi làm việc mà không muốn bị người khác dễ dàng phát hiện hoặc chú ý đến nội dung trên màn hình.

## ✨ Tính năng chính
- Tạo lớp phủ (dark overlay / vignette) tùy chỉnh trên màn hình máy tính.
- Tích hợp biểu tượng dưới khay hệ thống (System Tray) để quản lý dễ dàng.
- Tùy chỉnh các thông số hiển thị thông qua file cấu hình `config.json`.
- Hỗ trợ phím tắt để bật/tắt nhanh lớp phủ.

## 🚀 Cài đặt và Sử dụng

### 1. Yêu cầu hệ thống
Đảm bảo bạn đã cài đặt Python trên máy tính. Cài đặt các thư viện cần thiết bằng lệnh:
```bash
pip install -r requirements.txt
```

### 2. Chạy ứng dụng
Bạn có thể chạy ứng dụng trực tiếp bằng mã nguồn:
```bash
python main_windows.py
```
*(Hoặc `main.py` tùy thuộc vào hệ điều hành/cấu hình bạn đang dùng).*

### 3. Đóng gói thành file thực thi (.exe)
Nếu bạn đang sử dụng Windows, bạn có thể dễ dàng build ứng dụng thành một file `.exe` độc lập bằng cách chạy file batch:
```bash
build_windows.bat
```
File thực thi sẽ được tạo ra bên trong thư mục `dist`.

---

*Lưu ý: Công cụ này được sinh ra nhằm mục đích bảo vệ quyền riêng tư cá nhân, người dùng tự chịu trách nhiệm về cách sử dụng công cụ trong môi trường làm việc.*
