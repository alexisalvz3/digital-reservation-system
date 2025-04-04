from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models import Reservation

client = TestClient(app)

def test_get_reservations():
    response = client.get('/reservations')
    assert response.status_code == 200
    assert response.json() == [
        {
            "name": "kambala",
            "phone": "507-2424",
            "table_size": 10,
            "date_time": "2025-04-02T19:51:11.161000"
        },
        {
            "name": "Thomas Shelby",
            "phone": "432-4653",
            "table_size": 3,
            "date_time": "2025-04-03T02:18:15.356000"
        },
        {
            "name": "Luca Changretti",
            "phone": "333-3690",
            "table_size": 10,
            "date_time": "2025-04-03T23:05:32.826000"
        }
    ]

def test_create_reservation():
    response = client.post('/reservations', json={
        "name": "Winston Churchill",
        "email": "winston@brit.com",
        "phone": "924-1942",
        "table_size": 1,
        "date_time": "2025-04-04T00:47:36.390000"
    })
    assert response.status_code == 200
    assert response.json() == {
        "name": "Winston Churchill",
        "phone": "924-1942",
        "table_size": 1,
        "date_time": "2025-04-04T00:47:36.390000"
    }
    
def test_delete_reservation():
    # creating database session to query reservation to delete
    session = SessionLocal()
    res = session.query(Reservation).filter_by(name="Winston Churchill").first()
    session.close()
    # make sure the reservation we want to delete exists
    assert res is not None
    reservation_id = res.id
    
    # now delete the reservation
    delete_response = client.delete(f"/reservations/{reservation_id}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": "Reservation deleted."}