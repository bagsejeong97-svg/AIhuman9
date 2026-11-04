# day49_ex1.py
# 주제: 대화형 LLM의 역할 구분, 메세지 검증, 문맥 관리, Chat Template

'''
[대화형 생성의 입력 단위]

[개념]
질문 하나가 아니라 messages 리스트를 모델 입력으로 구성

[용어]
- messages : 발화자와 발화 내용의 묶음, 발화자와 발화 내용은 message
- role : 누가 말했는지 구분하는 키
- content : 실제 텍스트가 들어가는 키
- messages는 message들을 담고 있는 리스트, message는 role과 content 키로 구성된 딕셔너리

[역할이 필요한 이유]

[개념]
같은 문장이라도 말한 주체(발화자)에 따라 의미가 달라짐

[용어]
- system : 서비스의 정책과 답변 방식 지침
- user : 질문, 자료, 요청
- assistant : 맥락을 유지하기 위한 모델의 이전 응답

[대화 순서의 의미]

[개념]
메세지 리스트의 순서가 질문과 답변의 흐름을 결정

[일반적 구조]
system > user > assistant > user > assistant ...

[멀티턴(Multi-Turn) 대화]

[개념]
여러번 질문과 답변이 이어지는 대화

[메시지 수]
system 1개 + user 2개 + assistant 2개 = 총 5개

[Context Window]

[개념]
모델이 한 번에 처리할 수 있는 토큰 용량

[입력 예산(Budget)]

[개념]
응답에 필요한 공간을 남긴 뒤 입력 기록 배치

[수식]
가용 입력 토큰 = 총 한도 - 예약 출력 토큰 - 안전 여유

[수식 예시]
2,048 - 256 - 128 = 1,664

[Chat Template]

[개념]
role/content 메시지를 모델 전용 문자열 형식으로 변환한 포멧

[특징]
모델별 역할 토큰, 시작/종료 구분자가 다를 수 있음 = 모델마다 다른 챗템플릿을 사용할 수 있음

[관련 API]
- tokenizer.apply_chat_template(messages, tokenize=False): 토큰 문자열 서식화
- tokenizer.apply_chat_template(messages, tokenize=True): 토큰 ID 서식화
'''
import json
from pathlib import Path
from util.print_util import pp

ROOT = Path(__file__).resolve().parent

ROLE_SET = {'system','user','assistant'}

TOKENIZER_MODEL_ID = 'Qwen/Qwen2.5-0.5B-Instruct'

# 각 메시지가 role/content 구조와 자료형 조건을 만족하는지 검사하는 함수
# 변환값 : 모든 메시지가 올바르면 True, 오류가 있으면 예외 발생
def validate_messages(messages):
    if not isinstance(messages, list): # messages가 list가 아니면
        raise TypeError('messages는 리스트여야 합니다.')
    for index, message in enumerate(messages): # 각 메세지와 번호를 추출
        if not isinstance(message,dict): # message가 dict가 아니면
            raise TypeError(f'{index}번 메세지는 딕셔너리여야 합니다.')
        if message.get('role') not in ROLE_SET:
            raise ValueError(f'{index}번 메시지의 역할이 올바르지 않습니다.')
        if not isinstance(message.get('content'), str): # 콘텐츠로 가져온게 문자열이 아니라면
            raise TypeError(f'{index}번 메시지는 문자열이어야 합니다.')
    return True

# messages를 구성하는 함수

def make_history():
    # 5개의 메시지로 구성된 messages, 2턴
    return[
        {'role' : 'system', 'content' : '당신은 취업 준비 면접 코치입니다. 간결하고 구체적으로 답하세요.'},
        {'role' : 'user', 'content' : '데이터 분석 면접 준비 방법 2개만 알려줘.'},
        {'role' : 'assistant', 'content' : '1. SQL 문제 풀이 2. 프로젝트 설명 준비'},
        {'role' : 'user', 'content' : '그 중 두번째는 어떻게 준비해야해?'},
        {'role' : 'assistant', 'content' : '문제, 역할, 성과 순서로 정리하세요.'}
    ]

# 원본 대화를 유지하면서 질문과 답변 1쌍을 추가하는 함수
# messages : 기존 역할별 메시지 리스트
# question : 추가할 user 질문 문자열
# answer : 추가할 assistant 응답 문자열
def add_turn(messages, question, answer):
    result = list(messages) # 기존 리스트는 보존하기 위해서 새 리스트 생성
    # user 메시지와 assistant 메시지를 추가 (1턴 추가)
    result.append({'role' : 'user','content':question})
    result.append({'role' : 'assistant','content':answer})
    validate_messages(result) # 새로 만든 messages 검증
    return result

# system 메시지와 최근 완성된 질문/응답 쌍만 남기는 함수
# max_turns : 남길 최근 질문/응답 쌍의 개수
def keep_recent_turn(messages,max_turns = 2):
        validate_messages(messages)
        if isinstance(max_turns, bool) or not isinstance(max_turns, int):
            raise TypeError('max_turn는 정수여야 합니다.')
        if max_turns <= 0:
            raise ValueError('max_turns는 0 이상이어야 합니다.')
        system = [m for m in messages if m['role'] == 'system'] # system메시지 추출
        dialog = [m for m in messages if m['role'] != 'system'] # system메시지 아닌 메시지들 추출
        # 전체 메세지에서 system메시지 제외한 메시지들을 user > assistant 순으로 짝지어져 있어야 함
        if len(dialog)%2 or any(
            dialog[i]['role']!='user' or dialog[i+1]['role']!='assistant'
            for i in range(0, len(dialog),2)
        ):
            raise ValueError('대화 기록은 완성된 user/assistent 쌍으로 구성되어야 합니다.')
        return system + (dialog[-2*max_turns:] if max_turns else [])

# 메시지 본문의 문자 수 합계가 제한 이내인지 확인하는 함수
# limit : 허용할 문자 수
def char_budget(messages, limit = 150):
    validate_messages(messages)
    total = sum(len(m['content']) for m in messages) # 본문 길이 합산
    return  total <= limit

# 메시지를 UTF-8 JSON 파일로 저장하는 함수
def save_json(messages, filename):
    validate_messages(messages)
    text = json.dumps(
        messages,
        ensure_ascii = False, # 한글을 ASCII로 변환하지 않음
        indent = 2, # 들여쓰기 공백 수
    )
    Path(filename).write_text(text,encoding='utf-8') # 파일 저장


# 모델의 Chat Template과 토큰 수를 확인하는 함수
def inspect_template(messages,model_id):
    validate_messages(messages)
    try:
        from transformers import AutoTokenizer
    except ImportError:
        pp('transformers 미설치')
        return
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if not tokenizer.apply_chat_template: # 모델이 chat template을 지원하지 않으면
        pp('모델이 chat template을 지원하지 않음')
        return
    # messages를 chat template으로 변환(적용)
    formatted = tokenizer.apply_chat_template(
        messages,
        tokenize=False, # 토큰 문자열
        add_generation_prompt = True # assistant 응답 시작 위치 표시 여부
    )
    ids = tokenizer.apply_chat_template(
        messages,
        tokenize=True,  # 토큰 ID
        add_generation_prompt=True  # assistant 응답 시작 위치 표시 여부
    )
    pp('시긱화 결과: ', formatted[:1200])
    pp('토큰 개수: ', len(ids))
    pp('모델 최대 길이 메타정보: ', tokenizer.model_max_length)



def main():

    original = make_history() # system 1개 + 대화 2쌍

    validate_messages(original)

    pp('[원본] 메시지 수 : ', len(original) )
    pp(' [원본] 문자 제한 150 이내: ', char_budget(original,150))

    expanded = add_turn(
        original,
        'SQL 답변 예시는요?',
        'JOIN 사례를 준비하세요.'
    )

    recent = keep_recent_turn(expanded, max_turns = 2) # 최근 2쌍

    pp('[최근 2턴] 발화 역할: ', [m['role'] for m in recent])
    pp('[최근 2턴] 문잔 제한 150 이내: ', char_budget(recent,150))

    file_path = ROOT / 'day40_history.json'
    save_json(recent, file_path)

    pp(f'저장 완료: {file_path}')

    if TOKENIZER_MODEL_ID:
        inspect_template(recent, TOKENIZER_MODEL_ID)


if __name__ == '__main__':
    main()



























































