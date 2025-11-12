from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app import schemas, models, services
from app.services import cancel_trip
from app.core.database import get_db

INTERNAL_SERVICE_API_KEY = "your-internal-service-api-key"
# --- Security Dependency ---
api_key_header = APIKeyHeader(name="X-API-Key")


async def verify_api_key(api_key: str = Security(api_key_header)):
    """
      Dependency to verify the internal service API key.
      """
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API Key. Provide 'X-API-Key' header."
        )
    if api_key != INTERNAL_SERVICE_API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid API Key."
        )
    return api_key


router = APIRouter(
    prefix="/trips",
    tags=["Trips"]
)

@router.post("/", response_model=schemas.TripCreateResponse, status_code=status.HTTP_201_CREATED)
async def request_new_trip(
    trip: schemas.TripCreate, 
    db: Session = Depends(get_db)
):
    """
    Hành khách yêu cầu một chuyến đi mới.
    Returns trip details along with nearby available drivers.
    """ 
    # Chỉ cần gọi service, mọi logic đã nằm trong đó
    return await services.create_trip(db=db, trip_data=trip)


@router.get("/{trip_id}", response_model=schemas.TripResponse)
def get_trip_details(
    trip_id: UUID, 
    db: Session = Depends(get_db)
):
    """
    Lấy thông tin chi tiết của một chuyến đi.
    """
    db_trip = services.get_trip_by_id(db, trip_id)
    if db_trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    # TODO: Đây là nơi bạn có thể làm "API Composition"
    # Gọi userService để lấy tên passenger
    # Gọi driverService để lấy tên tài xế
    # Gộp 3 response lại rồi trả về
    
    return db_trip


@router.patch("/{trip_id}/cancel", response_model=schemas.TripResponse)
async def cancel_trip_by_id(
        trip_id: UUID,
        db: Session = Depends(get_db)
):
    """
    Hủy một chuyến đi.
    """
    db_trip = services.cancel_trip(db, trip_id)
    if db_trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return db_trip
