from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_get_reservations():
    response = client.get('/reservations')
    assert response.status_code == 200
    assert response.json() == [
        {
            "name": "Alex",
            "phone": "555-1234",
            "table_size": 2,
            "date_time": "2025-04-15T19:00:00"
        },
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
        }
    ]

def test_create_reservation():
    response = client.post('/reservations', json={
        "name": "Luca Changretti",
        "email": "luca@blackhand.com",
        "phone": "333-3690",
        "table_size": 10,
        "date_time": "2025-04-03T23:05:32.826000"
    })
    assert response.status_code == 200
    assert response.json() == {
        "name": "Luca Changretti",
        "phone": "333-3690",
        "table_size": 10,
        "date_time": "2025-04-03T23:05:32.826000"
    }