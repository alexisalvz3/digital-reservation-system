from fastapi.testclient import TestClient
import base64
from app.sns import send_sms
from pytest_mock import mocker
from unittest.mock import patch
from app.main import StatusUpdate, app
from app.database import SessionLocal
from app.models import Reservation

client = TestClient(app)

def test_get_reservations():
    # include basic auth for header
    # Encode Basic Auth credentials
    username = "admin"
    password = "1234qwer"
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}"
    }
    response = client.get('/reservations', headers=headers)
    print(response.json())
    #assert response.status_code == 200
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
    
def test_delete_with_auth():
    # Create DB session and get the reservation to delete
    session = SessionLocal()
    res = session.query(Reservation).filter_by(name="Winston Churchill").first()
    session.close()

    assert res is not None
    reservation_id = res.id

    # Encode Basic Auth credentials
    username = "admin"
    password = "1234qwer"
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}"
    }

    # Send DELETE request with auth headers
    response = client.delete(f"/reservations/{reservation_id}", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"message": "Reservation deleted."}

def test_update_reservation_status():
    session = SessionLocal()
    res_id = 3
    # In this test we will test that our reservation status has been changed from 
    # PENDING to CANCELLED.
    # this function receives a reservation ID and a new Status. all we need to do is 
    # test or ASSERT that our reservation status has been updated to CANCELLED.
    # Encode Basic Auth credentials
    username = "admin"
    password = "1234qwer"
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}"
    }

    response = client.put(f"/reservations/{res_id}/status", headers=headers, json = {
            "status": "confirmed"
        })
    assert response.status_code == 200
    assert response.json() == {"message": "Reservation has been confirmed"}
    res = session.query(Reservation).filter(Reservation.id == res_id).first()
    assert res.status.value == "confirmed"
    print(res.status)
    session.close()
    
def test_delete_without_auth():
    # calling test reservation id to delete
    res_id = 5
    # attempt to delete the reservation
    delete_response = client.delete(f"/reservations/{res_id}")
    assert delete_response.status_code == 401
    
def test_get_notifications():
    username = "admin"
    password = "1234qwer"
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    headers = {
        "Authorization": f"Basic {encoded_credentials}"
    }
    response = client.get("/notifications", headers=headers)
    assert response.status_code == 200
    

'''
Test that verifies:
    1. this app attempts to send an SMS via twilio when an admin updates a reservation's
    status to "confirmed" or "cancelled"
    2. the notification is logged in the NotificationLog table even if SMS fails or is
    mocked.

We're NOT sending real SMS messages in this test, so we'll use a mock to simulate the 
behavior.
'''

# in this patch we are intercepting CONSTRUCTION of that Client to fake out its 
# messages.create method
@patch('app.sns.Client')
def test_sms_on_status_update(mock_client_class):
    # mock_client_class is the fake Client *class*
    mock_client = mock_client_class.return_value
    # now mock the instance's message.create()
    expected_sid = 'SMFAKEID123'
    mock_client.messages.create.return_value.sid = expected_sid
    
    #build basic-auth header
    username = "admin"
    password = "1234qwer"
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}"
    }

    # query and assert reservation to test update exists
    session = SessionLocal()
    reservation = session.query(Reservation).filter_by(name="kambala").first()
    session.close()
    
    assert reservation is not None
    res_id = reservation.id
    

    response = client.put(f"/reservations/{res_id}/status", headers=headers, json = {
            "status": "confirmed"
        })
    assert response.status_code == 200
    mock_client.messages.create.assert_called_once()
    
    