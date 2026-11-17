# day57_challenge_client.py
# 여행 추천 서버를 호출하는 CLI 클라이언트

import os
import requests
from util.print_util import pp, up
from dotenv import load_dotenv

load_dotenv()

URL = 'http://127.0.0.1:8000/trip/recommend'

key = os.getenv('TRAVEL_API_KEY', '')

request_data = {'city': '서울', 'days': 2, 'interests': ['자연', '역사']}

try:
    response = requests.post(
        URL,
        json=request_data,
        headers={'X-Travel-Key': key},
        timeout=10
    )
    response.raise_for_status()
    pp(response.json())

except requests.Timeout:
    pp('서버 응답 시간 초과')
except requests.RequestException:
    pp('네트워크 또는 HTTP 오류')

up(5)






























