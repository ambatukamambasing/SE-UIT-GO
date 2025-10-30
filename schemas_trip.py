# schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class TripBase(BaseModel):
    passenger_id: UUID
    driver_id: Optional[UUID] = None
    vehicle_id: Optional[UUID] = None
    start_location_address: str
    start_lat: float
    start_lng: float
    end_location_address: str
    end_lat: float
    end_lng: float
    estimated_fare: Optional[float] = None
    final_fare: Optional[float] = None
    distance_km: Optional[float] = None
    duration_min: Optional[float] = None
    status: Optional[str] = "requested"

class TripCreate(TripBase):
    pass

class TripUpdate(BaseModel):
    status: Optional[str]
    final_fare: Optional[float]

class Trip(TripBase):
    id: UUID
    requested_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
