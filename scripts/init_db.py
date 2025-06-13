from datetime import datetime
from app.database import SessionLocal, engine, Base
from app.models import Reservation, NotificationLog, AdminUser  # all your models

Base.metadata.create_all(bind=engine)

reservations = [
        {
            "name": "kambala",
            "email": "kambala@gmail.com",
            "phone": "507-2424",
            "table_size": 10,
            "date_time": datetime.fromisoformat("2025-04-02T19:51:11.161000")
        },
        {
            "name": "Thomas Shelby",
            "email": "tommy@gmail.com",
            "phone": "432-4653",
            "table_size": 3,
            "date_time": datetime.fromisoformat("2025-04-03T02:18:15.356000")
        },
        {
            "name": "Luca Changretti",
            "email": "luca@gmail.com",
            "phone": "333-3690",
            "table_size": 10,
            "date_time": datetime.fromisoformat("2025-04-03T23:05:32.826000")
        }
    ]
db = SessionLocal()
for r in reservations:
    db.add(Reservation(**r))
db.commit()
db.close()
