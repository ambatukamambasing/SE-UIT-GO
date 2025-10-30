# 🚗 UIT-Go Trip Microservice

> Microservice chịu trách nhiệm **quản lý chuyến đi, hóa đơn và đánh giá** trong hệ thống đặt xe UIT-Go.

---

## 📘 1. Giới thiệu

`TripService` là một thành phần của hệ thống **UIT-Go Microservices**, được phát triển theo kiến trúc **tách biệt hoàn toàn**.  
Service này đảm nhiệm việc:
- Quản lý chuyến đi (`trips`)
- Ghi nhận hóa đơn (`bills`)
- Quản lý đánh giá giữa hành khách và tài xế (`trip_reviews`)

---

## 🧱 2. Cấu trúc thư mục

```bash
trip-service/
│
├── main_trip.py          # File chính chạy FastAPI (API endpoints)
├── database.py           # Kết nối PostgreSQL
├── models.py             # ORM định nghĩa bảng trips
├── schemas.py            # Kiểu dữ liệu Pydantic (input/output)
├── crud.py               # Xử lý logic CRUD
├── .env.example          # Cấu hình môi trường mẫu
├── requirements.txt      # Thư viện cần cài
└── README.md             # Tài liệu mô tả project
