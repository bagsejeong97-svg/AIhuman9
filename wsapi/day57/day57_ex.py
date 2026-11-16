# day57_ex.py
# 주제: AI 텍스트 추론, WAV 검사, Perso 지원 언어 목록 조회

# 설치 : python -m pip install python-multipart

import io
import os
import wave
from functools import lru_cache
import httpx
from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from dotenv import load_dotenv
load_dotenv()

MAX_AUDIO_BYTES = 5 * 1024 * 1024 # 업로드 상한 5Mbytes

# PERSO 지원 언어 목록 API
PERSO_LANGUAGES = 'https://api.perso.ai/video-translator/api/v1/languages'

# 데모용 학습 문장: 서비스 운영 시에는 충분한 검증 데이터로 대체
SAMPLES = [
    ('도서관에서 책을 빌리고 싶어요', 'library'),
    ('대출 도서 반납 장소 알려줘', 'library'),
    ('열람실 좌석을 예약할게요', 'library'),
    ('도서관 운영시간 확인해줘', 'library'),
    ('점심 식당 메뉴가 무엇인가요', 'cafeteria'),
    ('학생식당은 어디에 있나요', 'cafeteria'),
    ('오늘 저녁 식사 시간 안내', 'cafeteria'),
    ('식당 메뉴를 추천해 주세요', 'cafeteria'),
    ('면접 준비 상담을 예약할게요', 'career'),
    ('취업지원센터 위치가 궁금해요', 'career'),
    ('채용 공고 찾아 주세요', 'career'),
    ('자기소개서 첨삭 문의합니다', 'career'),
]

ANSWERS = {
    'library': '도서관 안내 페이지를 확인해 주세요.',
    'cafeteria': '학생식당의 메뉴와 시간을 확인해 주세요.',
    'career': '취업지원센터의 상담 일정을 확인해 주세요.',
}

class TestRequest(BaseModel):
    text: str = Field(min_length=2, max_length=500, description='분류할 한국어 질문') # 요청 문자열

class TextResponse(BaseModel):
    intent:str # 의도
    confidence:float # 분류 확률
    answer:str # 응답 문자열

class AudioResponse(BaseModel):
    filename:str # 오디오 파일명
    channels:int # 채널 수
    sample_rate:int # 샘플링 비율
    duration_seconds:float # 재생 시간(초)

# 모델을 LRU(Lease Recently Used) 캐싱
@lru_cache(maxsize=1)
def get_model():
    texts, labels = zip(*SAMPLES)
    model = Pipeline([
        ('tfidf',
         TfidfVectorizer(
            analyzer='char', # 문자 단위
            ngram_range=(2,4)) # 문자 2개 ~ 4개
         ),
        ('classifier',
         LogisticRegression(
             max_iter=500, # 최적화 반복 최대 회수4
             random_state=42)), # 재현성 확보를 위한 난수 시드
    ])
    model.fit(texts, labels) # 예시 데이터 학습
    return model

app = FastAPI(
    title='AI Inference & Perso Integration',
    description= ' 텍스트 추론, WAV 검사 및 perso API 연동',
    version='0.0.1'
)

# Streamlit 접근 허용을 위해 CORS 미들웨어를 앱에 추가
# CORS : 브라우져 교차 출처 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ # 허용하는 URL (Streamlit > uvicorn 접속에 대한 허용 정책)
        'http://localhost:8501',
        'http://127.0.0.1:8501'
    ],
    allow_methods=['GET','POST'], # 허용하는 요청 메소드
    allow_headers=['Content-Type'] # 허용하는 헤터 = 컨텐트 타입
)

@app.get('/api/health') # 서버 상태 확인용
def health():
    return{
        'status': 'ok',
        'model' : 'tfidf-logreg-demo'
    }

@app.post('/api/infer',response_model=TextResponse)
# 입력 문장을 분석하여 의도를 분류하는 함수
def infer(request: TestRequest):
    model = get_model() # 캐싱된 모델 가져요기
    # 각 클래스에 속할 확률
    probabilities = model.predict_proba([request.text])[0]
    # 확률이 가장 높은 클래스의 인덱스
    index = int(probabilities.argmax())
    # 모덱이 학습한 클래스 레이블 목록
    intent = str(model.classes_[index])
    # 예측 확률을 소수점 네자리
    confidence = round(float(probabilities[index]), 4)
    return TextResponse(
        intent=intent, # 예측한 질문의 의도
        confidence=confidence, # 예측 클래스의 확률
        answer=ANSWERS[intent] # 의도에 대응하는 안내 메세지
    )

@app.post('/api/audio/inspect', response_model=AudioResponse)
async def inspect_audio(file: UploadFile = File(...)):

    if not file.filename or not file.filename.lower().endswith('.wav'):
        raise HTTPException(415, 'WAV 파일만 허용합니다')

    try:
        # 제한 용량보다 1바이트 더 읽어서 초과 여부 확인
        data = await file.read(MAX_AUDIO_BYTES + 1)
    finally:
        await file.close() # 파일 자원 해제(반환)

    if len(data) > MAX_AUDIO_BYTES:
        raise HTTPException(413,'파일이 최대 허용 용량을 초과함')

    try:
        with wave.open(io.BytesIO(data), 'rb') as wav:
            channels = wav.getnchannels() # 채널 수
            rate = wav.getframerate()  # 초당 샘플 수 (Hz)
            frames = wav.getnframes()  # 전체 오디오 프레임 수
            if wav.getcomptype() != 'NONE' or rate <= 0:
                raise ValueError('압축 파일 또는 비정상적인 샘플링 레이트')
    except (wave.Error, EOFError,ValueError):
        raise HTTPException(422, '유효한 WAV 파일이 아님')

    duration = round(frames / rate, 3) # 재생시간 = 전체 프레임수 / 샘플링 레이트

    return AudioResponse(
        filename=file.filename,
        channels=channels,
        sample_rate=rate,
        duration_seconds=duration
    )

@app.get('/api/perso/languages')
# PERSO 지원언어 목록
async def perso_languages():
    key = os.getenv('PERSO_API_KEY','').strip()
    if not key:
        raise HTTPException(503,'PERSO_API_KEY 미설정')

    try:

        async with httpx.AsyncClient(timeout=10.0) as client:
            result = await client.get( # 비동기로 GET 요청
                PERSO_LANGUAGES, # 접속 URL
                headers={'XP-API-KEY': key} # API 키
            )
        if result.status_code in (401,403):
            raise HTTPException(502,'PERSO 인증/권한 오류')
        if result.status_code == 429:
            raise HTTPException(503,'PERSO 요청 제한')

        result.raise_for_status() # 나머지  4xx,5xx 오류 시에는 예외 발생시킴

        payload = result.json() # JSON 응답 문자열을 파이썬 딕셔너리로

        if not isinstance(payload, dict):
            raise ValueError('JSON 객체 형식이 아님')

        return {
            'provider' : 'PERSO',
            'data' : payload.get('result',payload)
        }



    except httpx.TimeoutException:
        raise HTTPException(504,'PERSO 응답 시간 초과')
    except httpx.HTTPStatusError:
        raise HTTPException(501,'PERSO 서버 오류')
    except (httpx.RequestError, ValueError):
        raise HTTPException(502,'PERSO 연결/ 응답 형식 오류')











































































































































































