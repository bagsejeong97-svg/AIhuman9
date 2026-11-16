# day55_basic.py
# 도서 대여 요청 관리

from uuid import uuid4
from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field
from util.print_util import pp, up

app = FastAPI(title = 'Library Loan API')

LOANS = {}

# 대여 요청의 책 제목, 사용자, 대여 기간 유효성을 검사하는 BaseModel
class LoanInput(BaseModel):
    book_title: str = Field(min_length=2, max_length=80)
    borrower: str = Field(min_length=2, max_length=30)
    days: int = Field(ge=1, le=30)

# 생성 응답에 대여 ID를 추가한 모델
class LoanOutput(LoanInput):
    loan_id: str

@app.post('/loans', status_code=status.HTTP_201_CREATED, response_model=LoanOutput)
def create_loan(data: LoanInput):
    loan = LoanOutput(loan_id=uuid4().hex, **data.model_dump())
    LOANS[loan.loan_id] = loan
    pp('대여 접수: ', loan.loan_id)
    return loan

@app.get('/loans', response_model=list[LoanOutput])
def list_loans(limit: int = Query(default=10, ge=1, le=50)):
    return list(LOANS.values())[:limit]

@app.get('/loans/{loan_id}', response_model=LoanOutput)
def get_loan(loan_id: str):
    if loan_id not in LOANS:
        raise HTTPException(404, detail='대여 내역이 없습니다.')
    return LOANS[loan_id]

up(5)

































