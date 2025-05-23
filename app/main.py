from datetime import datetime
import os
import secrets
from typing import Annotated, Optional
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, status , HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, ConfigDict
from sqlalchemy import insert
from app.database import SessionLocal
from sqlalchemy.orm import Session
from app.auth_utils import get_secret


from app.models import NotificationLog, NotificationStatus, Reservation, ReservationStatus
from app.sns import send_sms

app = FastAPI()
admin_credentials = get_secret()
load_dotenv()

#ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
#ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

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

class NotificationLogOut(BaseModel):
    id: int
    name: str
    recipient_email: str
    recipient_phone: str
    message: str
    time_sent: datetime
    type: str
    status: NotificationStatus
    
    model_config = ConfigDict(arbitrary_types_allowed=True,
                              from_attributes=True)

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
    correct_username_bytes = admin_credentials["admin_username"].encode("utf8")
    # using .compare_digest() to prevent 'timing attacks'
    is_correct_username = secrets.compare_digest(current_username_bytes, correct_username_bytes)
    # do the same for password
    current_password_bytes = credentials.password.encode('utf8')
    correct_password_bytes = admin_credentials["admin_password"].encode("utf8")
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
        type = status.status.value
        status_log = NotificationLog(name = reservation.name,
                                     recipient_phone = reservation.phone,
                                     recipient_email = reservation.email,
                                     message = f"Reservation has been {type}",
                                     type = f"reservation_{type}",
                                     status = NotificationStatus.SENT.value)
        db.add(status_log)
        db.commit()
        # grabbing twilio credentials to send sms via api
        account_sid = admin_credentials["TWILIO_ACCOUNT_SID"]
        auth_token = admin_credentials["TWILIO_AUTH_TOKEN"]
        # call sms twilio function to send sms text on reservation update
        send_sms(status_log.message, account_sid, auth_token)
        return JSONResponse(content={"message": f"Reservation has been {type}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")  
    
@app.get("/notifications", response_model=list[NotificationLogOut], status_code=status.HTTP_200_OK)
def get_notifications(credentials: HTTPBasicCredentials = Depends(check_admin_credentials), db: Session = Depends(get_db)):
    try:
        notification_logs = db.query(NotificationLog).all()
        return notification_logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
   