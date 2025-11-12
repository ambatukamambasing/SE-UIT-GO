from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from typing import Optional
from ..models.trip import TripStatus # Import Enum từ model

# Dữ liệu cơ bản
class TripBase(BaseModel):
    start_location_address: str
    end_location_address: str

# Dữ liệu nhận vào khi tạo chuyến
class TripCreate(TripBase):
    passenger_id: UUID
    # estimated_fare sẽ được tính bởi service

# Dữ liệu trả về cho client
class TripResponse(TripBase):
    id: UUID
    passenger_id: UUID
    driver_id: Optional[UUID] = None
    vehicle_id: Optional[UUID] = None
    status: TripStatus
    requested_at: datetime
    
    class Config:
        orm_mode = True # Cho phép Pydantic đọc từ model SQLAlchemy

# Dùng để cập nhật trạng thái
class TripStatusUpdate(BaseModel):
    status: TripStatus