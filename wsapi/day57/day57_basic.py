# day57_basic.py
# 주제:
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(
    title="채용공고 키워드 분류  API",
    description= '텍스트를 용한 카테고리 추론',
    version = '0.0.1'
)

class JobsRequest(BaseModel):
    title : str = Field(min_length=3, max_length=120)

class JobsResponse(BaseModel):
    title : str
    category : str
    keyword_matched : str | None

@app.post('/jobs/classify',response_model=JobsResponse)
def classify_jobs(request: JobsRequest):
    title = request.title

    if '데이터' in title:
        category  = 'data'
        keyword_matched = '데이터'

    elif '백엔드' in title:
        category = 'backend'
        keyword_matched = '백엔드'

    else:
        category = 'general'
        keyword_matched = None

    return JobsResponse(
        title=title,
        category=category,
        keyword_matched=keyword_matched
    )





































