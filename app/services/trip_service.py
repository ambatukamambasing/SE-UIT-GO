from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException, status
import httpx # Thư viện để gọi API
from decimal import Decimal

from .. import models, schemas
from ..core.config import settings # Import settings để lấy URL

# --- Client gọi UserService ---
# Kiểm tra xem user có tồn tại và hợp lệ không
async def validate_user_exists(user_id: UUID):
    async with httpx.AsyncClient() as client:
        try:
            # Gọi đến API của UserService (đã dockerize)
            url = f"{settings.USER_SERVICE_URL}/api/v1/users/{user_id}"
            response = await client.get(url)
            
            if response.status_code == 404:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                    detail=f"Passenger with id {user_id} not found")
            
            response.raise_for_status() # Báo lỗi nếu 500, 401, ...
            
            user_data = response.json()
            # Bạn có thể kiểm tra thêm, ví dụ: user có bị ban không
            # if user_data.get("is_active") == False:
            #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, ...)
            
            return user_data

        except httpx.RequestError as e:
            # Lỗi không kết nối được UserService
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail=f"User service is unavailable: {str(e)}")


# --- Logic của TripService ---

async def create_trip(db: Session, trip_data: schemas.TripCreate):
    """
    Tạo chuyến đi mới (Logic chính)
    """
    # 1. Xác thực hành khách
    await validate_user_exists(trip_data.passenger_id)
    
    # 2. (Giả lập) Gọi 1 service khác (PricingService) để tính giá
    # (Ở đây ta gán tạm)
    estimated_fare = Decimal("50000.00") 

    # 3. Tạo chuyến đi trong DB
    db_trip = models.trip.Trip(
        passenger_id=trip_data.passenger_id,
        start_location_address=trip_data.start_location_address,
        start_lat=trip_data.start_lat,
        start_lng=trip_data.start_lng,
        end_location_address=trip_data.end_location_address,
        end_lat=trip_data.end_lat,
        end_lng=trip_data.end_lng,
        estimated_fare=estimated_fare,
        status=models.trip.TripStatus.requested
    )
    
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    
    # 4. (Quan trọng) Gửi sự kiện (Event)
    # Bạn sẽ dùng Kafka/RabbitMQ ở đây để thông báo cho
    # "MatchingService" (Dịch vụ tìm tài xế)
    # print(f"EMIT EVENT: TripRequested, trip_id: {db_trip.id}")
    
    return db_trip


def get_trip_by_id(db: Session, trip_id: UUID):
    """
    Lấy thông tin chuyến đi theo ID
    """
    return db.query(models.trip.Trip).filter(models.trip.Trip.id == trip_id).first()

# (Bạn tự viết thêm các hàm get, update, ... khác)