from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID # Đảm bảo bạn đã import UUID

# -----------------------------------------------
# 
# Đây là các "schema" (mô hình dữ liệu) của Pydantic
# Chúng KHÔNG phải là model của SQLAlchemy
#
# -----------------------------------------------

# Đây là class cơ sở, chứa các trường chung
# Nó phải khớp với CSDL trip_db của bạn
class TripBase(BaseModel):
    # Dùng đúng kiểu UUID
    passenger_id: UUID
    driver_id: Optional[UUID] = None
    
    # Dùng đúng tên trường và kiểu dữ liệu từ CSDL
    start_location_address: str

    end_location_address: str

    status: str = "requested" # CSDL của bạn mặc định là 'requested'

# Schema dùng khi TẠO MỚI một chuyến đi
class TripCreate(TripBase):
    pass  # Kế thừa tất cả các trường từ TripBase

# Schema dùng để TRẢ VỀ (RESPONSE) cho client
class TripResponse(TripBase):
    id: UUID # 👈 ID phải là UUID
    
    # Các trường thời gian CSDL tự tạo
    requested_at: datetime
    updated_at: Optional[datetime] = None # 👈 Chỉ định nghĩa 1 lần
    
    # Thêm các trường thời gian khác nếu bạn muốn trả về
    accepted_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    # Cấu hình này bảo Pydantic đọc dữ liệu
    # từ model SQLAlchemy (ví dụ: trip.id thay vì trip['id'])
    class Config:
        from_attributes = True


from typing import List, Optional, Any

class DriverInfo(BaseModel):
    """Schema for driver information from driver service"""
    id: UUID
    name: Optional[str] = None
    distance: Optional[float] = None
    rating: Optional[float] = None
    # Add other fields as needed based on driver service response
    
    class Config:
        from_attributes = True


class TripCreateResponse(BaseModel):
    """Response when creating a new trip with nearby drivers info"""
    trip: TripResponse
    nearby_drivers: List[Any]  # Use Any or create a specific schema based on driver service response
    passenger_location: dict
    
    class Config:
        from_attributes = True