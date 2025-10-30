# schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from uuid import UUID

class DriverBase(BaseModel):
    full_name: str
    phone_number: Optional[str] = None
    license_number: str
    license_expiry: Optional[date] = None
    is_active: Optional[bool] = True
    approval_status: Optional[str] = "pending"

class DriverCreate(DriverBase):
    pass

class DriverUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    license_number: Optional[str] = None
    license_expiry: Optional[date] = None
    is_active: Optional[bool] = None
    approval_status: Optional[str] = None

class Driver(DriverBase):
    id: UUID
    rating_avg: float
    total_trips: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
