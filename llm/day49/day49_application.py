# day49_application.py
# 주제:
import json
from pathlib import Path
from util.print_util import pp

ROOT = Path(__file__).resolve().parent

ROLE_SET = {'system','user','assistant'}

TOKENIZER_MODEL_ID = 'Qwen/Qwen2.5-0.5B-Instruct'


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


def make_history():
    return [{'role':'system','content' :'쇼핑몰 고객지원 센터 입니다.'}]


def add_history(messages,question,answer):
    result = list(messages)

    result.append({'role':'user','content':question})
    result.append({'role':'assistant','content':answer})
    validate_messages(result)
    return result


def recent_turn(messages,max_turns = 2):
    validate_messages(messages)
    if isinstance(max_turns, bool) or not isinstance(max_turns, int):
        raise TypeError('최근봐야할 값의 갯수는 정수로 설정하여야 합니다.')
    if max_turns <= 0:
        raise ValueError('최근바야할 값의 갯수는 0이상이야 합니다.')
    system = [m for m in messages if m['role']=='system']
    dialog = [m for m in messages if m['role']!='system']

    if len(dialog)%2 or any(dialog[i]['role']!='user' or dialog[i+1]['role']!='assistant' for i in range(0, len(dialog),2)):
        raise ValueError('대확 기록은 user/assistant 형태로 구성 되어야 합니다.')
    return system + (dialog[-2*max_turns:] if max_turns else [] )


def save_json(messages, filename):
    validate_messages(messages)
    text = json.dumps(
        messages,
        ensure_ascii = False, # 한글을 ASCII로 변환하지 않음
        indent = 2, # 들여쓰기 공백 수
    )
    Path(filename).write_text(text,encoding='utf-8') # 파일 저장


def main():
    history = make_history()



    pairs = [
        ("배송은 언제인가요?", "주문 상태를 확인하세요."),
        ("교환 절차는요?", "교환 신청 메뉴를 이용하세요."),
        ("환불은 어떻게 하나요?", "환불 규정을 확인하세요."),
    ]


    for answer,question in pairs:
        history = add_history(history,answer,question)


    recent = recent_turn(history,max_turns = 2)

    file_path = ROOT / 'day40_application.json'
    save_json(recent, file_path)

    pp(f'저장완료: {file_path}')

if __name__ == '__main__':
    main()


































