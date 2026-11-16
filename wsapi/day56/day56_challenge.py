# day56_challenge.py
# 주제:
import httpx
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query

app = FastAPI(title='환율 참고 정보 API')

BASE_URL = 'https://api.frankfurter.dev/v1/latest' #일자별 유료화 환율

# base : 기준 통화의 ISO 4217 코드 (예: USD)
def fetch_rates(base):
    try:
        with httpx.Client(timeout=10.0) as client: # 동기 HTTP 클라이언트
            res = client.get(BASE_URL,params={'base':base})
        res.raise_for_status()
        payload = res.json() # 응답 JSON문자열을 딕셔너리로
        if not isinstance(payload.get('rates'), dict):
            raise HTTPException(502, '환율 응답에 rates가 없음')
        return payload

    except httpx.TimeoutException:
        raise  HTTPException(504,' 환율API 응답 지연')
    except httpx.RequestError:
        raise HTTPException(502,'환울 API 요청 실패')
    except (httpx.RequestError, ValueError):
        raise HTTPException(502, '환울 API 얀걀/ 응답 오류')

@app.get('/rates/{base}')
def rates(base:str):
    if len(base) != 3 or not base.isalpha():
        raise HTTPException(422,'통화코드는 영문 3자리여야 함')
    return fetch_rates(base.upper())

@app.get('/convert')
def convert(base : str = 'USD',  # 기준 통화
            quote:str = 'KRW',  # 변환 통화
            amount:float | int = Query(10, gt=0)): # 통화량
    if len(base) != 3 or len(quote) != 3:
        raise HTTPException(422,'통화코드는 3자리여야 함')
    if base == quote:
        return {'base':base,'quote':quote,'amount':amount,'converted':amount,'rate':1.0}
    data = fetch_rates(base)
    rate = data['rates'].get(quote)
    if not isinstance(rate,(int,float)):
        raise HTTPException(404,'지원하지 않는 상대 통화힙니다.')
    return {
        'base': base,
        'quote': quote,
        'amount': amount,
        'converted': round(amount * rate,4),
        'rate': rate
    }


































