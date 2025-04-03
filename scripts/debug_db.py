from app.database import SessionLocal
from app.models import Reservation
from sqlalchemy import delete

session = SessionLocal()
reservations = session.query(Reservation).all()

session.query(Reservation).filter(Reservation.name == "Luca Changretti").delete()
session.commit()

#stmt = delete(Reservation).where(Reservation.name == "Luca Changretti")
#session.query(stmt)
print('deleted luca')

session.close()
