from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)

def test_ingest_and_list():
    data = [
        {"id": 100, "location": "Test", "rating": 4, "text": "Nice", "date": "2025-09-10"}
    ]
    res = client.post('/ingest', json=data, headers={'x-api-key':'supersecret'})
    assert res.status_code == 200
    list_res = client.get('/reviews', headers={'x-api-key':'supersecret'})
    assert list_res.status_code == 200
    assert any(r['id']==100 for r in list_res.json())
