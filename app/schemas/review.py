import uuid
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ReviewBase(BaseModel):
    rating_for_driver: Optional[int] = Field(None, ge=1, le=5)
    comment_for_driver: Optional[str] = None
    rating_for_passenger: Optional[int] = Field(None, ge=1, le=5)
    comment_for_passenger: Optional[str] = None

class ReviewCreate(ReviewBase):
    # Dữ liệu cần để tạo 1 review
    trip_id: uuid.UUID
    passenger_id: uuid.UUID
    driver_id: uuid.UUID

class ReviewResponse(ReviewBase):
    id: uuid.UUID
    trip_id: uuid.UUID
    passenger_id: uuid.UUID
    driver_id: uuid.UUID
    created_at: datetime
    
    class Config:
        orm_mode = True # Đọc từ SQLAlchemy model