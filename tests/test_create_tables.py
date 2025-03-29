from app.database import engine, Base
from app.models import Reservation

Reservation.metadata.create_all(bind=engine)
print("Tables created successfully.")