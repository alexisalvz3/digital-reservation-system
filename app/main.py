from datetime import datetime
import secrets
from typing import Annotated, Optional
from fastapi import Depends, FastAPI, status , HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, ConfigDict
from app.database import SessionLocal
from sqlalchemy.orm import Session


from app.models import Reservation, ReservationStatus

app = FastAPI()

#initializing HTTPBasic for admin auth
security = HTTPBasic()

# Admin Auth Section:

#   1: write a dpendency function like 'admin_auth'
#   2: use it to protect one of your sensitive routes(like DELETE)

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
# pydantic schema for changing user's reservation status 
class StatusUpdate(BaseModel):
    status: ReservationStatus

# function for dependency-based db session, this way we dont need to call our session manually    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
# create a dependcy to check if username and password are correct for admin login
def check_admin_credentials(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    # convert username and password to to bytes encoding them with UTF-8 
    # This is done in order to use secrets.compare_digest()
    current_username_bytes = credentials.username.encode('utf8')
    correct_username_bytes = b"admin"
    # using .compare_digest() to prevent 'timing attacks'
    is_correct_username = secrets.compare_digest(current_username_bytes, correct_username_bytes)
    # do the same for password
    current_password_bytes = credentials.password.encode('utf8')
    correct_password_bytes = b"1234qwer"
    # perform compare_digest check
    is_correct_password = secrets.compare_digest(current_password_bytes, correct_password_bytes)
    # check status of username and password validation and return value
    if not(is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=f"Authorization error: Incorrect username or password",
            headers={"WWW-AUTHENTICATE": "BASIC"}
        )
    return credentials.username
        

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
async def get_reservations(credentials: HTTPBasicCredentials = Depends(check_admin_credentials), db: Session = Depends(get_db)):
    try:
        reservations = db.query(Reservation).all()
        return reservations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.delete("/reservations/{reservation_id}", status_code=status.HTTP_200_OK)
async def delete_reservation(reservation_id: int, credentials: HTTPBasicCredentials = Depends(check_admin_credentials), db: Session = Depends(get_db)):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found.")
    db.delete(reservation)
    db.commit()
    
    return JSONResponse(content={"message": "Reservation deleted."})

@app.put("/reservations/{item_id}/status")
async def update_reservation_status(item_id: int, status: StatusUpdate, credentials: HTTPBasicCredentials = Depends(check_admin_credentials), db: Session = Depends(get_db)):
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
   