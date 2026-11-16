# day55_ex2.py
# 주제: FastAPI, JSONPlaceholder users CRUD, Pydantic

from typing import Annotated
import httpx # 비동기 통신 라이브러리
from fastapi import Depends, FastAPI, HTTPException, Path, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field


BASE_URL = 'https://jsonplaceholder.typicode.com'

app = FastAPI(
    title='JSONPlaceholder users CRUD 실습',
    description='JSONPlaceholder users CRUD 실습입니다.',
    version='0.1',
)

# Pydantic 데이터 모델
class Geo(BaseModel):
    lat: str # 위도
    lng: str # 경도

class Address(BaseModel):
    street: str # 스트리트 거리
    suite: str ='' # 아파트/동호수
    city: str ='' # 도시
    zipcode: str # 우편번호
    geo: Geo | None = None # 위/경도

class Company(BaseModel):
    name: str # 회사명
    catchPhrase: str # 홍보 문구
    bs : str # 회사 소개 문구

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    username: str = Field(min_length=2, max_length=40)
    email: EmailStr # 이메일 형식 검즘
    phone: str  | None = None
    website: str | None = None
    address: Address | None = None
    company: Company | None = None
    # 모델 설정: 미정의된 필드는 차단(금지)
    model_config = ConfigDict(extra='forbid')

class UserReplace(UserCreate):
    pass # 추가 정의 없음

class UserPath(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=80)
    username: str | None = Field(default=None, min_length=2)
    email: EmailStr | None = None
    phone: str | None = None
    website: str | None = None
    model_config = ConfigDict(extra='forbid')

class UserOut(BaseModel):
    id: int
    name: str | None
    username: str | None
    email: EmailStr | None
    phone: str | None
    website: str | None
    address: Address | None
    company: Company | None
    model_config = ConfigDict(extra='ignore')

# 외부 API 연결 함수
def get_client():
    # 비동기 요청 클라이언트
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        # yield: 클라이언트를 FastAPI에 제공하고 처리 후 정리
        yield client

# HTTP 클라이언트를 FastAPI 의존성 주입(Dependency Injection)
# Annotated: 데이터타입(httpx.Client)에 추가 정보 (Depends)를 결합
Client = Annotated[httpx.Client, Depends(get_client)]

# 사용자 ID에 정수형 및 URL 경로 파라미터 검증 조건 지정
# 쉽게 말해서 사용자 ID는 정수로 1 이상 이어야 함
UserID = Annotated[int, Path(ge=1)]

# API 호출하는 함수
# client: HTTP Client
# method : HTTP Request Method (Get, Post, ...)
# path: 호출경로
# **kwargs: 함수에 전달되는 추가 인자들을 받을 파라미터
# 반환 타입: httpx.Response
def call_api(client:httpx.Client, method:str, path: str, **kwargs) -> httpx.Response:
    try:
        # method: HTTP요청메소드, path: 요청URL, **kwargs: POST/PUT/PATCH요청시 전달할 Payload
        response = client.request(method, path, **kwargs) # 요청 후 응답 획득
        response.raise_for_status() # 응답 상태 코드가 4XX / 5XX면 예외 발생
        return response
    except httpx.TimeoutException as e:
        raise HTTPException(status_code=504,detail="외부 api 응답시간 초과" )
    except httpx.HTTPStatusError as e:
        code = e.response.status_code # 응답상태 코드
        if code == 404: # Not Found
            raise HTTPException(404, detail='해당 사용자 정보를 찾을 수 없음')
        raise HTTPException(status_code=502, detail=f'외부 API 오류: HTTP{code}')
    except httpx.RequestError as e:
        raise HTTPException(502, '와부 API에 연결할 수 없음')

# 응답 모델 검증 함수
# 응답객체를 받아서 검증한 응답 모델 리턴
def parse_user(response: httpx.Response) -> UserOut:
    try:
        # 응답 모델의 문자열 검증해서 응답 모델 리턴
        return UserOut.model_validate(response.json())
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=502, detail='외부 API의 응답이 올바르지 않음')

# GET: 전체 목록과 한건 조회

@app.get('/users', response_model=list[UserOut])
# 전체 user 조회
def user_list(client: Client):
    response = call_api(client, 'GET', '/users')
    try:
        # 각 JSON 검증 후 리스트로 반환
        return [UserOut.model_validate(user) for user in response.json()]
    except (ValueError, TypeError) as e:
        raise HTTPException(502,'사용자 목록 응답 형식 오류')

@app.get('/users/{user_id}', response_model=UserOut)
def user_get(user_id: UserID, client: Client):
    return parse_user(call_api(client, 'GET', f'/users/{user_id}'))

@app.post('/users', response_model=UserOut, status_code=status.HTTP_201_CREATED)
def user_create(data: UserCreate, client: Client):
    # model_dump: 딕셔너리로 변환
    # exclude_none=True: none 미포함
    payload = data.model_dump(exclude_none=True)
    response = call_api(client, 'POST', f'/users', json=payload)
    return parse_user(response)

# PUT: 사용자 전체 수정
@app.put('/users/{user_id}', response_model=UserOut)
def user_put(user_id: UserID, data: UserReplace, client: Client):
    payload = data.model_dump(exclude_none=True)
    payload['id'] = user_id # 수정할 사용자 ID
    response = call_api(client, 'PUT', f'/users/{user_id}', json=payload)
    return parse_user(response)

# PATCH: 사용자 정보 부분 수정
@app.patch('/users/{user_id}', response_model=UserOut)
def user_patch(user_id: UserID, data: UserReplace, client: Client):
    payload = data.model_dump(exclude_none=True)
    if not payload:
        raise HTTPException(422,'수정할 필드를 하나 이상 지정하세요')
    response = call_api(client, 'PATCH', f'/users/{user_id}', json=payload)
    return parse_user(response)

# DELETE: 사용자 정보 삭제
@app.delete('/users/{user_id}')
def user_delete(user_id: UserID, client: Client):
    response = call_api(client, 'DELETE', f'/users/{user_id}')
    return {
        'id': user_id,
        'status_code': response.status_code,
        'message': '삭제 성공'
    }




