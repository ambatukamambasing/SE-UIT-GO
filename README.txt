===========================================
UIT-Go User Microservice
===========================================

1. GIỚI THIỆU
-------------------------------------------
UserService là một microservice thuộc hệ thống UIT-Go.
Chức năng chính:
- Quản lý người dùng (User)
- Quản lý hồ sơ tài xế (Driver Profile)
- Quản lý phương tiện (Vehicle)

Ngôn ngữ: Python 3.12
Framework: FastAPI
CSDL: PostgreSQL
ORM: SQLAlchemy
Container: Docker + Docker Compose


2. CẤU TRÚC THƯ MỤC
-------------------------------------------
Main_user.py         → File chính chạy FastAPI
database.py          → Cấu hình kết nối cơ sở dữ liệu
Bảng user.sql        → Tạo cấu trúc bảng PostgreSQL
example.env          → Mẫu file môi trường (.env)
requirements.txt     → Liệt kê thư viện cần cài đặt
Dockerfile           → File cấu hình Docker
docker-compose.yml   → Tạo môi trường server + database
README.txt           → Tài liệu hướng dẫn


3. CÀI ĐẶT (LOCAL)
-------------------------------------------
Tạo môi trường ảo:
> python -m venv venv
> .\venv\Scripts\activate

Cài thư viện:
> pip install -r requirements.txt

Chạy server:
> uvicorn Main_user:app --reload

Truy cập:
> http://localhost:8000/docs


4. CẤU HÌNH MÔI TRƯỜNG (.env)
-------------------------------------------
DB_USER=postgres
DB_PASSWORD=user_db_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=user_db


5. CHẠY BẰNG DOCKER
-------------------------------------------
Build và chạy container:
> docker compose up --build

Sau khi chạy, truy cập API:
> http://localhost:8000/docs


6. CẤU TRÚC CSDL CHÍNH
-------------------------------------------
Bảng: users
  - id (UUID, PK)
  - full_name, email, role, is_active, ...

Bảng: driver_profiles
  - driver_id (UUID, PK)
  - user_id (FK → users.id)
  - license_number, rating_avg, ...

Bảng: vehicles
  - id (UUID, PK)
  - driver_id (FK → driver_profiles.driver_id)
  - license_plate, model, color, ...


7. KẾT NỐI GIỮA CÁC SERVICE
-------------------------------------------
TripService sẽ gọi UserService thông qua REST API:

Ví dụ:
- GET /users/
- GET /users/{id}
- POST /users/
- GET /driver-profiles/{driver_id}
- POST /driver-profiles/{driver_id}/vehicles


8. KẾ HOẠCH PHÁT TRIỂN
-------------------------------------------
Giai đoạn 1: Thiết kế bộ xương microservice  ✔️
Giai đoạn 2: Kết nối User ↔ Trip bằng API   🔄
Giai đoạn 3: Bổ sung xác thực (JWT)         🔜


9. NHÓM PHÁT TRIỂN
-------------------------------------------
Dự án: UIT-Go Microservices (SE360 - UIT)
Thành viên:
- Trần Minh Khải (Leader)
- [Thêm tên thành viên tại đây]


10. GHI CHÚ
-------------------------------------------
Được phát triển trong khuôn khổ môn học:
SE360 - Software Engineering
Trường Đại học Công nghệ Thông tin (UIT) - ĐHQG TP.HCM

© 2025 UIT-Go Project | User Service