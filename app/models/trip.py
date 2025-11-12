import uuid
import enum
from sqlalchemy import Column, String, UUID, Numeric, TIMESTAMPTZ, Enum, Text
from sqlalchemy.orm import relationship
from ..core.database import Base

class TripStatus(str, enum.Enum):
    requested = 'requested'
    accepted = 'accepted'
    in_progress = 'in_progress'
    completed = 'completed'
    cancelled = 'cancelled'

class Trip(Base):
    __tablename__ = "trips"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    passenger_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    driver_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    vehicle_id = Column(UUID(as_uuid=True), nullable=True)

    status = Column(Enum(TripStatus), nullable=False, default=TripStatus.requested, index=True)

    start_location_address = Column(Text, nullable=False)
    end_location_address = Column(Text, nullable=False)

    distance_km = Column(Numeric(6, 2))
    duration_min = Column(Numeric(6, 2))

    requested_at = Column(TIMESTAMPTZ, server_default='CURRENT_TIMESTAMP')
    accepted_at = Column(TIMESTAMPTZ)
    started_at = Column(TIMESTAMPTZ)
    completed_at = Column(TIMESTAMPTZ)
    cancelled_at = Column(TIMESTAMPTZ)
    updated_at = Column(TIMESTAMPTZ, server_default='CURRENT_TIMESTAMP')

    # Quan hệ nội bộ
    bill = relationship("Bill", back_populates="trip", uselist=False, cascade="all, delete-orphan")
    review = relationship("TripReview", back_populates="trip", uselist=False, cascade="all, delete-orphan")