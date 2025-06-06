from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.types import Enum as SAEnum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from enum import Enum

from app.database import Base

class ReservationStatus(Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    CANCELLED = 'cancelled'
    
class NotificationStatus(str, Enum):
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)  # Customer name
    email = Column(String, nullable=False)  # Customer email
    phone = Column(String, nullable=False)  # Customer phone number
    table_size = Column(Integer, nullable=False)
    table_number = Column(Integer, nullable=True)
    date_time = Column(DateTime, nullable=False)
    status = Column(SAEnum(ReservationStatus), nullable=False, default=ReservationStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    
class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="admin")

class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    recipient_phone = Column(String, nullable=False)
    recipient_email = Column(String, nullable=False)
    message = Column(String, nullable=False)
    time_sent = Column(DateTime, default=datetime.utcnow)
    type = Column(String)
    status = Column(SAEnum(NotificationStatus))