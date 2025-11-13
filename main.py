import redis.asyncio as aioredis
from redis.commands.core import AsyncScript
from fastapi import FastAPI, Depends, HTTPException, Query, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from contextlib import asynccontextmanager
from typing import List, Optional
import os

# --- Configuration ---
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
# This is for internal microservice communication.
# In a real app, load this from environment variables!
INTERNAL_SERVICE_API_KEY = "my-secret-microservice-key"

# Redis Keys
# GeoSet: Stores driver locations for online drivers
GEO_KEY = "driver_locations"
# GeoSet: Stores passenger locations
PASSENGER_GEO_KEY = "passenger_locations"
# Hash: Stores status and info for each driver
STATUS_KEY_PREFIX = "driver_status:"


# --- Pydantic Models ---
class DriverStatus(BaseModel):
    status: str  # "online" or "offline"
    service_type: Optional[str] = "standard"
    lat: Optional[float] = None  # Required when going online
    lng: Optional[float] = None  # Required when going online


class LocationUpdate(BaseModel):
    lat: float
    lng: float


class DriverInfo(BaseModel):
    driver_id: str
    status: str
    service_type: str
    lat: float
    lng: float
    distance_km: float


class PassengerLocationResponse(BaseModel):
    passenger_id: str
    lat: float
    lng: float


# --- Redis Connection Management ---
redis_pool = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_pool
    print("Connecting to Redis...")
    redis_pool = aioredis.ConnectionPool.from_url(
        f"redis://{REDIS_HOST}:{REDIS_PORT}",
        max_connections=20,
        decode_responses=True
    )
    # Ping to check connection
    async with aioredis.Redis(connection_pool=redis_pool) as r:
        await r.ping()
    print("Connected to Redis.")
    yield
    print("Closing Redis connection pool...")
    await redis_pool.disconnect()
    print("Redis connection pool closed.")


async def get_redis():
    if not redis_pool:
        raise HTTPException(status_code=503, detail="Redis connection pool not initialized")
    async with aioredis.Redis(connection_pool=redis_pool) as r:
        yield r


# --- Security Dependency ---
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


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


app = FastAPI(
    title="DriverService",
    description="Manages driver status and real-time location",
    lifespan=lifespan
)


# --- API Endpoints ---

@app.post("/drivers/{driver_id}/status", status_code=200)
async def update_driver_status(
        driver_id: str,
        body: DriverStatus,
        r: aioredis.Redis = Depends(get_redis)
):
    """
    Update a driver's status (online/offline).
    When going "online", lat/lng are required.
    """
    status_key = f"{STATUS_KEY_PREFIX}{driver_id}"

    async with r.pipeline(transaction=True) as pipe:
        try:
            if body.status == "online":
                if body.lat is None or body.lng is None:
                    raise HTTPException(
                        status_code=400,
                        detail="lat and lng are required to go online"
                    )

                # 1. Add to GeoSet
                await pipe.geoadd(GEO_KEY, (body.lng, body.lat, driver_id))

                # 2. Update status Hash
                await pipe.hset(status_key, mapping={
                    "status": "online",
                    "service_type": body.service_type or "standard"
                })

                await pipe.execute()
                return {"driver_id": driver_id, "status": "online"}

            elif body.status == "offline":
                # 1. Remove from GeoSet
                await pipe.zrem(GEO_KEY, driver_id)

                # 2. Update status Hash
                await pipe.hset(status_key, "status", "offline")

                await pipe.execute()
                return {"driver_id": driver_id, "status": "offline"}

            else:
                raise HTTPException(status_code=400, detail="Status must be 'online' or 'offline'")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {e}")


@app.post("/drivers/{driver_id}/location", status_code=200)
async def update_driver_location(
        driver_id: str,
        body: LocationUpdate,
        r: aioredis.Redis = Depends(get_redis)
):
    """
    Update a driver's location.
    This will only update the GeoSet if the driver is "online".
    """
    status_key = f"{STATUS_KEY_PREFIX}{driver_id}"

    try:
        # Check if driver is online
        status = await r.hget(status_key, "status")

        if status == "online":
            # Update the driver's location in the GeoSet
            await r.geoadd(GEO_KEY, (body.lng, body.lat, driver_id))
            return {"driver_id": driver_id, "status": "location_updated"}
        elif status == "offline":
            # Driver is offline, so we don't track their location
            return {"driver_id": driver_id, "status": "offline", "info": "Location not updated"}
        else:
            # Driver doesn't exist
            raise HTTPException(status_code=404, detail="Driver not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@app.post("/passenger/location", status_code=200)
async def update_passenger_location(
        passenger_id: str,
        body: LocationUpdate,
        r: aioredis.Redis = Depends(get_redis)
):
    """
    Update a passenger's location.
    This is used to find drivers *near the passenger*.
    """
    try:
        # Simply add/update the passenger's location in their GeoSet
        await r.geoadd(PASSENGER_GEO_KEY, (body.lng, body.lat, passenger_id))
        return {"passenger_id": passenger_id, "status": "location_updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@app.get("/passenger/location", response_model=PassengerLocationResponse)
async def get_passenger_location(
        r: aioredis.Redis = Depends(get_redis),
        user_id: str = Query(...),
        _api_key: str = Depends(verify_api_key)
):
    """
    Get a passenger's last known location based on user_id.
    """
    try:
        # GEOPOS returns a list of [lng, lat] coordinates for the members
        location_data = await r.geopos(PASSENGER_GEO_KEY, user_id)

        if not location_data or location_data[0] is None:
            raise HTTPException(status_code=404, detail="Passenger location not found")

        # location_data is a list, e.g., [[-74.0063, 40.7129]]
        lng, lat = location_data[0]

        return PassengerLocationResponse(
            passenger_id=user_id,
            lat=lat,
            lng=lng
        )
    except HTTPException as e:
        raise e  # Re-raise 404
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@app.get("/drivers/nearby", response_model=List[DriverInfo])
async def find_nearby_drivers(
        lat: float,
        lng: float,
        radius_km: float = Query(5.0, gt=0),
        service_type: Optional[str] = Query(None),
        r: aioredis.Redis = Depends(get_redis),
        _api_key: str = Depends(verify_api_key)  # <-- This secures the endpoint
):
    """
    Find suitable drivers within a given radius.

    This is a protected endpoint and requires a valid 'X-API-Key' header
    for service-to-service communication.
    """

    # 1. Query Redis GeoSet for nearby drivers
    # GEORADIUS returns [
    #   ['driver_1', '1.2345', ['-73.9876', '40.7654']],
    #   ['driver_2', '2.3456', ['-73.9877', '40.7655']]
    # ]
    try:
        nearby_drivers = await r.georadius(
            GEO_KEY,
            longitude=lng,
            latitude=lat,
            radius=radius_km,
            unit="km",
            withdist=True,
            withcoord=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis GEORADIUS error: {e}")

    if not nearby_drivers:
        return []

    # 2. Get status for each nearby driver
    # We use a pipeline for efficiency
    async with r.pipeline(transaction=False) as pipe:
        for driver_data in nearby_drivers:
            driver_id = driver_data[0]
            await pipe.hgetall(f"{STATUS_KEY_PREFIX}{driver_id}")

        driver_statuses = await pipe.execute()

    # 3. Combine, filter, and format results
    results = []
    for i, driver_data in enumerate(nearby_drivers):
        driver_id = driver_data[0]
        distance = float(driver_data[1])
        coords = driver_data[2]
        status_info = driver_statuses[i]

        # Ensure status_info is a dict and driver is still online
        if isinstance(status_info, dict) and status_info.get("status") == "online":
            # Apply service_type filter if provided
            driver_service = status_info.get("service_type", "standard")
            if service_type and service_type != driver_service:
                continue

            results.append(DriverInfo(
                driver_id=driver_id,
                status="online",
                service_type=driver_service,
                lat=float(coords[1]),  # lat is index 1
                lng=float(coords[0]),  # lng is index 0
                distance_km=round(distance, 2)
            ))

    # Sort by distance
    results.sort(key=lambda d: d.distance_km)

    return results

# To run: uvicorn main:app --reload




