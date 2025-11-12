import httpx
from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException
import os

from app import models, schemas

# Configuration for driver service
DRIVER_SERVICE_URL =  os.getenv("DRIVER_API_BASE_URL", "http://localhost:8002")# Update with your driver service URL
DRIVER_SERVICE_API_KEY = "my-secret-microservice-key"  # Update with your actual key


async def create_trip(db: Session, trip_data: schemas.TripCreate):
    """
    Create a new trip by:
    1. Getting passenger location from driver service
    2. Finding nearby drivers
    3. Creating the trip record
    """
    try:
        # Step 1: Get passenger location from driver service
        async with httpx.AsyncClient() as client:
            headers = {"X-API-Key": DRIVER_SERVICE_API_KEY}

            # Get passenger location - use passenger_id instead of user_id
            location_response = await client.get(
                f"{DRIVER_SERVICE_URL}/passenger/location",
                params={"user_id": str(trip_data.passenger_id)},  # Changed from user_id to passenger_id
                headers=headers
            )

            if location_response.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail=f"Failed to get passenger location: {location_response.text}"
                )

            location_data = location_response.json()
            lat = location_data.get("lat")
            lng = location_data.get("lng")

            if not lat or not lng:
                raise HTTPException(
                    status_code=502,
                    detail="Invalid location data from driver service"
                )

            # Step 2: Find nearby drivers
            nearby_response = await client.get(
                f"{DRIVER_SERVICE_URL}/drivers/nearby",
                params={"lat": lat, "lng": lng},
                headers=headers
            )

            if nearby_response.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail=f"Failed to get nearby drivers: {nearby_response.text}"
                )

            nearby_drivers = nearby_response.json()

            if not nearby_drivers:
                raise HTTPException(
                    status_code=404,
                    detail="No nearby drivers available"
                )

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Driver service unavailable: {str(e)}"
        )

    # Step 3: Create the trip (you can optionally assign the first nearby driver)
    db_trip = models.Trip(
        passenger_id=trip_data.passenger_id,  # Changed from user_id to passenger_id
        driver_id=trip_data.driver_id,  # Or use nearby_drivers[0]['id'] to auto-assign
        start_location_address=trip_data.start_location_address,
        end_location_address=trip_data.end_location_address,
        status="requested"
    )

    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)

    # Return trip with nearby drivers info
    return {
        "trip": db_trip,
        "nearby_drivers": nearby_drivers,
        "passenger_location": {"lat": lat, "lng": lng}
    }

def get_trip_by_id(db: Session, trip_id: UUID):
    """Get trip by ID"""
    return db.query(models.Trip).filter(models.Trip.id == trip_id).first()


def cancel_trip(db: Session, trip_id: UUID):
    """Cancel a trip"""
    db_trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    if db_trip:
        db_trip.status = "cancelled"
        db.commit()
        db.refresh(db_trip)
    return db_trip

