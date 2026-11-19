"""FastAPI TestClient — 실제 Perso/DB 연결 없는 검증."""
from fastapi.testclient import TestClient
from backend.main import app

client=TestClient(app)

def test_health():
    response=client.get("/api/health")
    assert response.status_code==200
    assert response.json()["ok"] is True

def test_cost_confirmation_required():
    response=client.post("/api/jobs",json={"space_seq":1,"media_seq":1,"kind":"stt",
                        "is_video_project":False,"confirm_cost":False})
    assert response.status_code==400

def test_upload_extension_validation():
    response=client.post("/api/media/upload",data={"space_seq":"1","kind":"audio"},
                         files={"file":("bad.exe",b"MZ","application/octet-stream")})
    assert response.status_code==422

def test_invalid_target():
    response=client.get("/api/jobs/1/1/download",params={"target":"arbitrary"})
    assert response.status_code==422
