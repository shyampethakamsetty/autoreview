from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_unauthorized():
    res = client.get('/reviews')
    assert res.status_code == 401
