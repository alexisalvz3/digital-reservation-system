import datetime
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from app.database import SessionLocal
from sqlmodel import Session

app = FastAPI()

class ReservationCreate(BaseModel):
    name: str
    email: str | Optional[str] = None
    phone: str
    table_size: int
    date_time: datetime
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/reservations")
async def create_reservation(reservation: ReservationCreate, db: Session = Depends(get_db)):
  return reservation
    