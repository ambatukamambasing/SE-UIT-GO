Real-Time Driver Service (FastAPI & Redis - Simplified)This project demonstrates a simplified microservice for managing real-time driver locations and status using FastAPI and Redis.This version has been simplified for educational purposes and removes Kafka.Architecturedocker-compose.yml: Starts the necessary infrastructure:Redis: The database for storing driver status (Hashes) and geospatial locations (GeoSets).main.py (FastAPI Server):POST /drivers/{driver_id}/status: Allows a driver to go "online" or "offline".Going "online" adds/updates their location in the Redis GeoSet.Going "offline" removes them from the Redis GeoSet.POST /drivers/{driver_id}/location: (New) Allows an online driver to send real-time location updates. This endpoint updates the driver's position in the Redis GeoSet.GET /drivers/nearby: Finds all "online" drivers within a specified radius by querying the Redis GeoSet.How to RunYou will need 2 separate terminal windows.Terminal 1: Start InfrastructureFirst, make sure you have Docker and Docker Compose installed.# Start Redis in the background
docker-compose up -d
(To stop them later, run docker-compose down)Terminal 2: Run the FastAPI ServerThis process runs the main API.# Install Python dependencies
pip install -r requirements.txt

# Run the FastAPI server
uvicorn main:app --reload
The API will be available at http://127.0.0.1:8000. You can see the docs at http://127.0.0.1:8000/docs.Example API UsageNow you can interact with the service.1. Set driver_1 to "online":This sets the driver's status and adds their initial location.curl -X POST "[http://127.0.0.1:8000/drivers/driver_1/status](http://127.0.0.1:8000/drivers/driver_1/status)" \
-H "Content-Type: application/json" \
-d '{
    "status": "online",
    "service_type": "premium",
    "lat": 40.7128,
    "lng": -74.0060
}'
Response: {"driver_id":"driver_1","status":"online"}2. Send a location update for driver_1:Simulate the driver moving to a new location.curl -X POST "[http://127.0.0.1:8000/drivers/driver_1/location](http://127.0.0.1:8000/drivers/driver_1/location)" \
-H "Content-Type: application/json" \
-d '{
    "lat": 40.7130,
    "lng": -74.0062
}'
Response: {"driver_id":"driver_1","status":"location_updated"}3. Find nearby drivers:Let's search near the new location.curl -X GET "[http://127.0.0.1:8000/drivers/nearby?lat=40.7129&lng=-74.0063&radius_km=1](http://127.0.0.1:8000/drivers/nearby?lat=40.7129&lng=-74.0063&radius_km=1)"
Response:[
  {
    "driver_id": "driver_1",
    "status": "online",
    "service_type": "premium",
    "lat": 40.713,
    "lng": -74.0062,
    "distance_km": 0.02
  }
]
4. Set driver_1 to "offline":curl -X POST "[http://127.0.0.1:8000/drivers/driver_1/status](http://127.0.0.1:8000/drivers/driver_1/status)" \
-H "Content-Type: application/json" \
-d '{"status": "offline"}'
Response: {"driver_id":"driver_1","status":"offline"}5. Find nearby drivers again:curl -X GET "[http://127.0.0.1:8000/drivers/nearby?lat=40.7129&lng=-74.0063&radius_km=1](http://127.0.0.1:8000/drivers/nearby?lat=40.7129&lng=-74.0063&radius_km=1)"
Response: []The driver is no longer returned because they are offline.