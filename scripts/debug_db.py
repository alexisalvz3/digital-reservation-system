from app.database import SessionLocal
from app.models import Reservation

session = SessionLocal()
reservations = session.query(Reservation).all()
for r in reservations:
    print(f"{r.id} | {r.name} | {r.date_time} | {r.email} | {r.phone} | {r.table_size} | {r.table_number}")
session.close()
