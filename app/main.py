from fastapi import FastAPI
from .core.database import engine, Base
from .api.v1 import trips # Import router của bạn

# Dòng này tạo các bảng trong DB dựa trên Models (nếu chưa có)
# Trong production, bạn nên dùng Alembic
#Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TripService API",
    description="Dịch vụ quản lý chuyến đi, hóa đơn và đánh giá",
    version="1.0.0"
)

# Gắn router vào app
app.include_router(trips.router, prefix="/api/v1")
# app.include_router(bills.router, prefix="/api/v1")
# app.include_router(reviews.router, prefix="/api/v1")

@app.get("/health", tags=["Health Check"])
def health_check():
    """Kiểm tra service có đang chạy không"""
    return {"service": "TripService", "status": "ok"}