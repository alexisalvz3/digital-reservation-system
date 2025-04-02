from datetime import datetime
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from app.database import SessionLocal
from sqlmodel import Session

from app.models import Reservation

app = FastAPI()

# Pydantic schema for incoming user reservation data
class ReservationCreate(BaseModel):
    name: str
    email: str | Optional[str] = None
    phone: str
    table_size: int
    date_time: datetime
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

# function for dependency-based db session, this way we dont need to call our session manually    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/reservations")
async def create_reservation(reservation: ReservationCreate, db: Session = Depends(get_db)):
  # Create a Reservation SQLAlchemy object
  data = reservation.model_dump()
  db_model = Reservation(**data)
  
  db.add(db_model)
  db.commit()
  db.refresh(db_model)
  
  return db_model