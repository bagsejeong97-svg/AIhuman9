"""프로젝트 실행 진입점: uvicorn backend.main:app --reload"""
from fastapi import FastAPI
from backend.routers.perso_router import router

app=FastAPI(title="Day60 Perso AI Integrated Studio",version="1.0.0")
app.include_router(router)
