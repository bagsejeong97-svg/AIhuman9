#Streamlit UI : FastAPI 추론, WAV 업로드, Perso 언어 목록

import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_BASE = os.getenv('API_BASE','http://127.0.0.1:8000').rstrip('/')

st.set_page_config(
    page_title='AI API 클라이언트',
    layout='centered',
)

st.title('AI 추론 API, Streamlit 연동')

# FastAPI 서번에 HTTP 요청을 보내고 결과를 반환하는 함수

def send_request(method,path,**kwargs):

    try:

        response = method(API_BASE+path,timeout = (3,15),**kwargs)

        response.raise_for_status()

        return response.json(),None

    except requests.Timeout:
        return None,'요청 시간 초과'
    except requests.ConnectionError:
        return None, 'API 서버 연결 실패'
    except requests.HTTPError as e:
        return None, (
            f'HTTP {e.response.status_code}'
            f'{e.response.text[:200]}'
        )

    except ValueError:
        return None, 'JSON 응답 해석 실패'

# Streamlit UI

st.subheader('AI 텍스트 추론')

with st.form('inference'):
    message = st.text_area('질문 입력','학생식당이 어디 있나요?') # 분류할 질문 입력
    submitted = st.form_submit_button('AI 분류 실행') # form 제출 버튼

if submitted:
    result, error = send_request(requests.post,'/api/infer',json={'text':message})

    if error:
        st.error(error)

    else:
        st.json(result)

st.subheader('WAV 파일 검사')

uploaded = st.file_uploader('WAV 구조 검사', type=['wav'])

if uploaded is not None and st.button('WAV 분석'):
    files = {
        'file': (
            uploaded.name, # 파일명
            uploaded.getvalue(), # 파일 바이트 데이터
            'audio/wav' # MIME 타입
        )
    }

    result, error = send_request(
        requests.post,
        '/api/audio/inspect',
        files=files
    )
    if error:
        st.error(error)
    else:
        st.json(result)

st.subheader('Perso 지원 언어 조회')

if st.button('Perso 지원 언어 조회'):
    result,error = send_request(
        requests.get,
        '/api/perso/languages'
    )
    if error:
        st.error(error)
    else:
        st.json(result)























































































