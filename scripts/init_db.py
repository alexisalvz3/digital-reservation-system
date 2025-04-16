from app.database import engine, Base
from app.models import Reservation, NotificationLog, AdminUser  # all your models

Base.metadata.create_all(bind=engine)
