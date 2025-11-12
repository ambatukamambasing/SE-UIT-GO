import uuid
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from typing import Optional
from ..models.bill import BillStatus # Import Enum từ model

class BillBase(BaseModel):
    payment_method: str = Field(..., max_length=50)
    amount: Decimal = Field(..., ge=0, decimal_places=2)

class BillCreate(BaseModel):
    # Dùng nội bộ, không cần API
    trip_id: uuid.UUID
    passenger_id: uuid.UUID
    driver_id: uuid.UUID
    amount: Decimal = Field(..., ge=0, decimal_places=2)
    payment_method: str = Field(..., max_length=50)
    status: BillStatus = BillStatus.pending

class BillResponse(BillBase):
    id: uuid.UUID
    trip_id: uuid.UUID
    passenger_id: uuid.UUID
    driver_id: uuid.UUID
    status: BillStatus
    created_at: datetime
    
    class Config:
        orm_mode = True # Đọc từ SQLAlchemy model

class BillStatusUpdate(BaseModel):
    status: BillStatus # Ví dụ: 'completed' hoặc 'failed'