# day55_application.py
# 채용 공고 관리 API

from typing import Literal
from uuid import uuid4
from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field
from util.print_util import pp, up

app = FastAPI(title="Recruiting API")

POSTS = {}

# 회사명, 직무, 경력 구분, 기술 목록, 최소 급여를 검증 BaseModel
class JobInput(BaseModel):
    company: str = Field(min_length=2, max_length=50)
    position: str = Field(min_length=2, max_length=60)
    level: Literal["junior", "mid"]
    skills: list[str] = Field(min_length=1, max_length=8)
    salary_min: int = Field(ge=0)

# 공개 응답에는 공고 식별자만 추가하며 내부 메모는 제외한 모델
class JobOutput(JobInput):
    post_id: str

@app.post("/posts", response_model=JobOutput,
          status_code=status.HTTP_201_CREATED)
def create_post(data: JobInput):
    item = JobOutput(post_id=uuid4().hex, **data.model_dump())
    POSTS[item.post_id] = item
    pp("공고 등록:", item.post_id)
    return item

@app.get("/posts", response_model=list[JobOutput])
def list_posts(
    skill: str | None = Query(default=None),
    min_salary: int = Query(default=0, ge=0)
):
    result = list(POSTS.values())
    if skill is not None:
        result = [p for p in result if skill.lower() in [s.lower() for s in p.skills]]
    return [p for p in result if p.salary_min >= min_salary]

@app.get("/posts/{post_id}", response_model=JobOutput)
def get_post(post_id: str):
    if post_id not in POSTS:
        raise HTTPException(404, detail="공고를 찾을 수 없습니다")
    return POSTS[post_id]

@app.delete("/posts/{post_id}")
def delete_post(post_id: str):
    get_post(post_id)
    del POSTS[post_id]
    return {"deleted": post_id}









