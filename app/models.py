import uuid
from sqlalchemy import Column, ForeignKey, String, DateTime, Text, Numeric, SmallInteger
from sqlalchemy.dialects.postgresql import UUID as PG_UUID # Import kiểu UUID của PostgreSQL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func # Dùng để lấy CURRENT_TIMESTAMP

# Import Base từ file database của bạn
from .core.database import Base

# ===========================================================
# BẢNG TRIPS (CHUYẾN ĐI)
# ===========================================================
class Trip(Base):
    __tablename__ = "trips"

    # ------------------
    # KHÓA CHÍNH VÀ ID
    # ------------------
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # ID từ các service khác (dùng UUID)
    passenger_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    driver_id = Column(PG_UUID(as_uuid=True), nullable=True, index=True)
    vehicle_id = Column(PG_UUID(as_uuid=True), nullable=True)

    status = Column(String(30), nullable=False, default='requested', index=True)

    # ------------------
    # THÔNG TIN ĐỊA ĐIỂM
    # ------------------
    start_location_address = Column(Text, nullable=False)
    end_location_address = Column(Text, nullable=False)

    # ------------------
    # CHI TIẾT CHUYẾN ĐI
    # ------------------
    distance_km = Column(Numeric(6, 2), nullable=True)
    duration_min = Column(Numeric(6, 2), nullable=True)

    # ------------------
    # DẤU THỜI GIAN (TIMESTAMPS)
    # ------------------
    # Dùng server_default thay vì default để CSDL tự điền
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Dùng cả server_default và onupdate để khớp với trigger
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # ------------------
    # QUAN HỆ (Relationships)
    # ------------------
    # Quan hệ 1-1 với Bill
    bill = relationship("Bill", uselist=False, back_populates="trip", cascade="all, delete-orphan")
    # Quan hệ 1-1 với TripReview
    review = relationship("TripReview", uselist=False, back_populates="trip", cascade="all, delete-orphan")


# ===========================================================
# BẢNG BILLS (HÓA ĐƠN)
# ===========================================================
class Bill(Base):
    __tablename__ = "bills"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Key (FK) nội bộ trỏ tới bảng 'trips'
    trip_id = Column(PG_UUID(as_uuid=True), ForeignKey("trips.id"), nullable=False, unique=True, index=True)
    
    # UUID từ UserService (lưu lại để truy vấn nhanh)
    passenger_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    driver_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)

    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default='pending')

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Quan hệ 1-1 ngược lại với Trip
    trip = relationship("Trip", back_populates="bill")


# ===========================================================
# BẢNG TRIP_REVIEWS (ĐÁNH GIÁ CHUYẾN ĐI)
# ===========================================================
class TripReview(Base):
    __tablename__ = "trip_reviews"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # FK nội bộ trỏ tới bảng 'trips'
    trip_id = Column(PG_UUID(as_uuid=True), ForeignKey("trips.id"), nullable=False, unique=True, index=True)

    # UUID từ UserService
    passenger_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    driver_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    
    rating_for_driver = Column(SmallInteger, nullable=True)
    comment_for_driver = Column(Text, nullable=True)
    
    rating_for_passenger = Column(SmallInteger, nullable=True)
    comment_for_passenger = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Quan hệ 1-1 ngược lại với Trip
    trip = relationship("Trip", back_populates="review")