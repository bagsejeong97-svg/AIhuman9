"""Streamlit은 FastAPI에만 요청하며 Perso 키나 DB 비밀번호를 갖지 않습니다."""
import os
import requests

BASE=os.getenv("FRONTEND_API_URL","http://127.0.0.1:8000").rstrip("/")

class ApiError(Exception):
    pass

def request(method,path,**kwargs):
    try:
        r=requests.request(method,BASE+path,timeout=180,**kwargs)
    except requests.RequestException as exc:
        raise ApiError(f"FastAPI 서버에 연결하지 못했습니다: {exc}") from exc
    if not r.ok:
        try:detail=r.json().get("detail",r.text[:300])
        except ValueError:detail=r.text[:300]
        raise ApiError(f"HTTP {r.status_code}: {detail}")
    return r.json()

def get(path,**params):return request("GET",path,params=params)
def post(path,data):return request("POST",path,json=data)
def upload_file(file,space_seq,kind):
    return request("POST","/api/media/upload",data={"space_seq":space_seq,"kind":kind},
         files={"file":(file.name,file.getvalue(),file.type or "application/octet-stream")})
