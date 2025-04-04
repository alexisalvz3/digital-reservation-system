from datetime import datetime
from typing import Optional
from fastapi import Depends, FastAPI, status , HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
from app.database import SessionLocal
from sqlalchemy.orm import Session


from app.models import Reservation, ReservationStatus

app = FastAPI()

# Pydantic schema for incoming user reservation data
class ReservationCreate(BaseModel):
    name: str
    email: str | Optional[str] = None
    phone: str
    table_size: int
    date_time: datetime
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
class ReservationOut(BaseModel):
    name: str
    phone: str
    table_size: int
    date_time: datetime
    
    model_config = ConfigDict(arbitrary_types_allowed=True,
                              from_attributes=True)
    
class StatusUpdate(BaseModel):
    status: ReservationStatus

# function for dependency-based db session, this way we dont need to call our session manually    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/reservations", response_model=ReservationOut)
async def create_reservation(reservation: ReservationCreate, db: Session = Depends(get_db)):
    try:
        # Convert Pydantic model to dictionary
        data = reservation.model_dump()
        # Create a new SQLAlchemy model instance with the data
        db_model = Reservation(**data)
        # Now user reservation data can be added to db session
        db.add(db_model)
        db.commit()
        db.refresh(db_model)
        
        return db_model
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}") 

@app.get("/reservations", response_model=list[ReservationOut], status_code=status.HTTP_200_OK)
async def get_reservations(db: Session = Depends(get_db)):
    try:
        reservations = db.query(Reservation).all()
        return reservations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.delete("/reservations/{reservation_id}", status_code=status.HTTP_200_OK)
async def delete_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found.")
    db.delete(reservation)
    db.commit()
    
    return JSONResponse(content={"message": "Reservation deleted."})

@app.put("/reservations/{item_id}/status")
async def update_reservation_status(item_id: int, status: StatusUpdate, db: Session = Depends(get_db)):
    try:
        # query the reservation with 'id' equal to {item_id}.
        reservation = db.query(Reservation).filter(Reservation.id == item_id).first()
        if not reservation:
            raise HTTPException(status_code=404, detail="Reservation not found.")
        reservation.status = status.status
        db.commit()
        return JSONResponse(content={"message": f"Reservation has been {status.status.value}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")  
   