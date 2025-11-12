# main_trip.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models, schemas, crud
from database import Base, engine, get_db
from uuid import UUID

# Tạo bảng database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Trip Service", version="1.0.0")

@app.get("/")
def root():
    return {"message": "Trip Service is running 🚀"}

# ---- Trip APIs ----
@app.get("/trips/", response_model=List[schemas.Trip])
def read_trips(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_trips(db, skip=skip, limit=limit)

@app.get("/trips/{trip_id}", response_model=schemas.Trip)
def read_trip(trip_id: UUID, db: Session = Depends(get_db)):
    db_trip = crud.get_trip(db, trip_id)
    if db_trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return db_trip

@app.post("/trips/", response_model=schemas.Trip, status_code=status.HTTP_201_CREATED)
def create_trip(trip: schemas.TripCreate, db: Session = Depends(get_db)):
    return crud.create_trip(db=db, trip=trip)

@app.put("/trips/{trip_id}", response_model=schemas.Trip)
def update_trip(trip_id: UUID, trip_in: schemas.TripUpdate, db: Session = Depends(get_db)):
    db_trip = crud.update_trip(db, trip_id=trip_id, trip_in=trip_in)
    if db_trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return db_trip

@app.delete("/trips/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(trip_id: UUID, db: Session = Depends(get_db)):
    db_trip = crud.delete_trip(db, trip_id=trip_id)
    if db_trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return
