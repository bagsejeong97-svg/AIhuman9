# day49_ex2.py
# Streamlit + OpenAI API를 이용한 역할 메시지 기반 멀티턴 챗봇

# 설치 : python -m pip install openai
# .env 파일에 OPENAI_API_KEY 변수 등록

import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from openai import APIError, AuthenticationError, RateLimitError

load_dotenv()

MODEL_ID = 'gpt-4.1-mini'

SYSTEM_DEFAULT = '너는 친절한 Python 전문 강사야. 알기 쉽게 설명해 줘.'

ROLE_SET = {'system', 'user', 'assistant'}

# 메세지 검증 함수
def validate_messages(messages):
    if not isinstance(messages, list): # messages가 list가 아니면
        raise TypeError('messages는 리스트여야 합니다.')
    for index, message in enumerate(messages): # 각 메시지와 번호
        if not isinstance(message, dict): # message가 dict가 아니면
            raise TypeError(f'{index}번 메시지는 딕셔너리여야 합니다.')
        if message.get('role') not in ROLE_SET:
            raise ValueError(f'{index}번 메시지의 역할이 올바르지 않습니다.')
        if not isinstance(message.get('content'), str):
            raise TypeError(f'{index}번 메시지는 문자열이어야 합니다.')
    return True

# 최근 N개의 완성된 질문/답변 쌍만 선택하는 함수
def keep_recent_turns(messages, max_turns=3):
    validate_messages(messages)
    if isinstance(max_turns, bool) or not isinstance(max_turns, int):
        raise TypeError('max_turns는 정수여야 합니다.')
    if max_turns < 0:
        raise ValueError('max_turns는 0 이상이어야 합니다.')
    if len(messages)%2 or any(
        messages[i]['role']!='user' or messages[i+1]['role']!='assistant'
        for i in range(0, len(messages), 2)
    ):
        raise ValueError('대화 기록은 완성된 user/assistant 쌍으로 구성되어야 합니다.')
    if max_turns == 0:
        return []
    return messages[-2*max_turns:]

# API에 전달할 system + 과거 대화 + 현재 질문 구성하는 함수
def build_messages(system_text, history, question, max_turns):
    recent = keep_recent_turns(history, max_turns)
    messages = [{'role': 'system', 'content': system_text}] # system 메세지
    messages.extend(recent) # system 메시지 뒤에 이전 대화 추가
    messages.append({'role': 'user', 'content': question}) # 뒤에 새로운 질문 추가
    validate_messages(messages)
    return messages

# 실제 ChatGPT 모델을 호출하고 assistant 응답을 받는 함수
# 반환값 : (답변 문자열, 입력 토큰 수, 출력 토큰 수)
def ask_chatgpt(api_key, messages):
    client = OpenAI(
        api_key=api_key, # OpenAI API Key
        timeout=40.0 # 요청 후 응답까지 대기 최대 시간 (초)
    )
    # 요청 후 응답 획득
    response = client.chat.completions.create(
        model = MODEL_ID,
        messages = messages,
        max_completion_tokens=400 # 출력 길이 상한
    )
    answer = response.choices[0].message.content or '' # 답변 텍스트
    usage = response.usage # 이번 호출의 토큰 사용량
    input_tokens = usage.prompt_tokens if usage else 0 # 입력 토큰 수
    ouput_tokens = usage.completion_tokens if usage else 0 # 출력 토큰 수
    return answer, input_tokens, ouput_tokens

def main():

    st.set_page_config(page_title="대화형 LLM 실습", page_icon="💬")
    st.title("💬 System · User · Assistant 챗봇")
    st.caption("Streamlit + OpenAI API | 역할 메시지와 최근 N턴 문맥 관리")

    if "history" not in st.session_state:
        st.session_state.history = []  # 완료된 대화만 보관

    if "last_payload" not in st.session_state:
        st.session_state.last_payload = []  # 최근 전송 메시지 확인용

    if "usage" not in st.session_state:
        st.session_state.usage = (0, 0)  # 최근 입력·출력 토큰 수

    with st.sidebar:

        st.subheader("챗봇 설정")

        st.text_input("모델", value=MODEL_ID, disabled=True)

        system_text = st.text_area(
            "System 메시지", value=SYSTEM_DEFAULT, height=110,
            help="AI가 어떤 역할과 답변 방식을 따를지 지정합니다.",
        )

        max_turns = st.slider(
            "전달할 과거 대화(턴)", min_value=0, max_value=10,
            value=3, help="1턴은 user 질문 1개와 assistant 답변 1개입니다.",
        )

        env_key = os.getenv("OPENAI_API_KEY", "")  # .env / 환경변수

        entered_key = st.text_input(
            "OpenAI API Key (환경변수가 없다면 입력)",
            type="password", help="입력값은 화면에 표시되지 않습니다.",
        )

        api_key = entered_key.strip() or env_key.strip()

        if api_key:
            st.success("API 키가 설정되었습니다.")
        else:
            st.warning("API 키를 먼저 입력하거나 .env에 설정하세요.")

        if st.button("대화 초기화", use_container_width=True):
            st.session_state.history = []  # 이전 대화 내용 삭제
            st.session_state.last_payload = []
            st.session_state.usage = (0, 0)
            st.rerun()  # 초기화된 화면 다시 표시

    for msg in st.session_state.history:  # 전체 대화는 화면에 표시
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input(
        "질문을 입력하세요. 예: Python 자료형 2가지를 알려줘.",
        disabled=not bool(api_key),
    )

    if question:

        # API 호출 시의 문맥과 화면에 보관할 전체 기록을 구분
        payload = build_messages(
            system_text, st.session_state.history, question, max_turns,
        )

        st.session_state.last_payload = payload  # 역할 구조 살펴보기

        with st.chat_message("user"):
            st.markdown(question)  # 현재 질문을 화면에 표시
        try:
            with st.chat_message("assistant"):
                with st.spinner("ChatGPT가 답변을 생성하고 있습니다..."):
                    answer, in_tokens, out_tokens = ask_chatgpt(
                        api_key, payload,
                    )
                if not answer.strip():
                    raise ValueError("API가 빈 답변을 반환했습니다.")
                st.markdown(answer)
        except AuthenticationError:
            st.error("인증 실패: API 키를 확인하세요.")
        except RateLimitError:
            st.error("요청 또는 사용량 한도 초과: 계정 한도를 확인하세요.")
        except APIError:
            st.error("OpenAI API 요청에 실패했습니다. 잠시 뒤 다시 시도하세요.")
        except Exception as exc:
            st.error(f"오류: {type(exc).__name__}. 설정을 확인하세요.")
        else:
            # 성공한 질문·답변만 세션에 저장, 다음 요청의 문맥이 됨
            st.session_state.history.extend([
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer},
            ])
            st.session_state.usage = (in_tokens, out_tokens)

    with st.expander("학습 확인: API에 전달한 messages 구조"):
        st.write("System 1개 + 최근 N턴 + 현재 User 1개")
        st.json(st.session_state.last_payload)  # API 키는 포함되지 않음
        st.write("전체 저장된 대화 쌍:", len(st.session_state.history) // 2)
        st.write("최근 API 입력/출력 토큰:", st.session_state.usage)
        st.caption("최근 N턴은 토큰 제한을 자동 보장하지 않습니다.")

if __name__ == "__main__":
    main()























