# models.py
from sqlalchemy import Column, String, Float, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from database import Base

class Trip(Base):
    __tablename__ = "trips"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    passenger_id = Column(UUID(as_uuid=True), nullable=False)
    driver_id = Column(UUID(as_uuid=True), nullable=True)
    vehicle_id = Column(UUID(as_uuid=True), nullable=True)

    status = Column(String(30), default="requested")
    start_location_address = Column(String, nullable=False)
    start_lat = Column(Float, nullable=False)
    start_lng = Column(Float, nullable=False)
    end_location_address = Column(String, nullable=False)
    end_lat = Column(Float, nullable=False)
    end_lng = Column(Float, nullable=False)
    estimated_fare = Column(DECIMAL(10, 2))
    final_fare = Column(DECIMAL(10, 2))
    distance_km = Column(DECIMAL(6, 2))
    duration_min = Column(DECIMAL(6, 2))

    requested_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    accepted_at = Column(TIMESTAMP(timezone=True))
    started_at = Column(TIMESTAMP(timezone=True))
    completed_at = Column(TIMESTAMP(timezone=True))
    cancelled_at = Column(TIMESTAMP(timezone=True))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
