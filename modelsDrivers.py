# models.py
from sqlalchemy import Column, String, Boolean, Date, TIMESTAMP, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from database import Base

class Driver(Base):
    __tablename__ = "drivers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), unique=True)
    license_number = Column(String(100), unique=True, nullable=False)
    license_expiry = Column(Date)
    is_active = Column(Boolean, default=True)
    approval_status = Column(String(20), default="pending")
    rating_avg = Column(Numeric(3, 2), default=0.0)
    total_trips = Column(Integer, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
