from fastapi.testclient import TestClient
from app.api.main import app

def test_executive_brief_endpoint() -> None:
    client = TestClient(app)
    response = client.post('/briefs/executive', json={
        'user_name': 'Christopher Byrne',
        'goal': 'Launch Busy Bee Holdings LLC',
        'risk_tolerance': 'moderate',
        'time_horizon_days': 90,
    })
    assert response.status_code == 200
    body = response.json()
    assert body['approved'] is True
    assert body['brief']['system_status']
