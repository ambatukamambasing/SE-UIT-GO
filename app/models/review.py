import uuid
from sqlalchemy import Column, UUID, SMALLINT, ForeignKey, TIMESTAMPTZ, Text
from sqlalchemy.orm import relationship
from ..core.database import Base

class TripReview(Base):
    __tablename__ = "trip_reviews"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id"), nullable=False, unique=True)
    passenger_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    driver_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    rating_for_driver = Column(SMALLINT)
    comment_for_driver = Column(Text)
    rating_for_passenger = Column(SMALLINT)
    comment_for_passenger = Column(Text)
    created_at = Column(TIMESTAMPTZ, server_default='CURRENT_TIMESTAMP')

    trip = relationship("Trip", back_populates="review")