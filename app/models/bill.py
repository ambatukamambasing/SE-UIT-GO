import uuid
import enum
from sqlalchemy import Column, String, UUID, Numeric, ForeignKey, TIMESTAMPTZ, Enum
from sqlalchemy.orm import relationship
from ..core.database import Base

class BillStatus(str, enum.Enum):
    pending = 'pending'
    completed = 'completed'
    failed = 'failed'

class Bill(Base):
    __tablename__ = "bills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id"), nullable=False, unique=True)
    passenger_id = Column(UUID(as_uuid=True), nullable=False)
    driver_id = Column(UUID(as_uuid=True), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String(50), nullable=False)
    status = Column(Enum(BillStatus), default=BillStatus.pending)
    created_at = Column(TIMESTAMPTZ, server_default='CURRENT_TIMESTAMP')

    trip = relationship("Trip", back_populates="bill")