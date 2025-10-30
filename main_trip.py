# main_trip.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models, schemas, crud
from database import Base, engine, get_db

# --- Khởi tạo DB ---
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Trip Service", version="1.0.0")

# --- API ví dụ ---
@app.get("/trips/", response_model=List[schemas.Trip])
def get_trips(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    trips = crud.get_trips(db, skip=skip, limit=limit)
    return trips

@app.post("/trips/", response_model=schemas.Trip, status_code=status.HTTP_201_CREATED)
def create_trip(trip: schemas.TripCreate, db: Session = Depends(get_db)):
    return crud.create_trip(db=db, trip=trip)
