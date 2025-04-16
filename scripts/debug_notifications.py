from app.database import SessionLocal
from app.models import NotificationLog

session = SessionLocal()
notifications = session.query(NotificationLog).all()
if not notifications:
    print("no notifications found")
else:
    print("HELLO!!")
    for r in notifications:
        print(f"{r.id} | {r.recipient_phone} | {r.recipient_email} | {r.message} | {r.type}")
session.close()
