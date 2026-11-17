# day57_challenge.py
# 여행 추천 API: 인증, 입력 검증, 간단한 추천 로직

import os
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title='여행 추천 API')

PLACES = {
    '서울': {'역사': '경복궁', '자연': '서울숲', '음식': '광장시장'},
    '부산': {'역사': '감천문화마을', '자연': '해운대', '음식': '부평깡통시장'},
}

class TripRequest(BaseModel):
    city: str = Field(min_length=2, max_length=20)
    days: int = Field(ge=1, le=5)
    interests: list[str] = Field(min_length=1, max_length=3)

@app.post('/trip/recommend')
def recommend_trip(
    item: TripRequest,
    x_travel_key: str | None = Header(default=None)
):

    key = os.getenv('TRAVEL_API_KEY')

    if not key:
        raise HTTPException(503, detail='키 미설정')

    if x_travel_key != key:
        raise HTTPException(401, detail='인증 오류')

    if item.city not in PLACES:
        raise HTTPException(404, detail='지원하지 않는 도시')

    locations = PLACES[item.city]

    selected = [locations[tag] for tag in item.interests if tag in locations]

    if not selected:
        raise HTTPException(422, detail='유효한 관심 분야 없음')

    return {
        'city': item.city,
        'days': item.days,
        'recommendations': selected[:item.days]
    }
































