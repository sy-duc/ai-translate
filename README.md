# AI Translate

Công cụ dịch tài liệu với khả năng giữ nguyên định dạng gốc.

## Yêu cầu hệ thống

- Python >= 3.11

## Hướng dẫn cài đặt trên Windows

### 1. Cài đặt Python

Tải và cài đặt Python 3.11+ từ [python.org](https://www.python.org/downloads/).

> **Lưu ý:** Khi cài đặt, nhớ **tích chọn "Add Python to PATH"**.

### 2. Clone dự án

```bash
git clone <url-repo>
cd ai-translate
```

### 3. Tạo môi trường ảo (virtual environment)

Mở **Command Prompt** hoặc **PowerShell** trong thư mục dự án:

```bash
python -m venv venv
```

### 4. Kích hoạt môi trường ảo

**Command Prompt:**
```bash
venv\Scripts\activate
```

**PowerShell:**
```powershell
venv\Scripts\Activate.ps1
```

> Nếu PowerShell báo lỗi về execution policy, chạy lệnh sau rồi thử lại:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

Khi kích hoạt thành công, đầu dòng lệnh sẽ hiển thị `(venv)`.

### 5. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### 6. Chạy ứng dụng

```bash
python -m src.main
```

### 7. Tắt môi trường ảo (khi không dùng nữa)

```bash
deactivate
```
