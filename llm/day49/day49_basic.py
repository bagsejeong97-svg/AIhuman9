# day49_basic.py
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



def make_library_history():
    return [{"role": "system", "content": "도서관 안내 도우미입니다."}]


def append_pair(history,question,answer):
    result = list(history)
    result.append({'role': 'user', 'content': question})
    result.append({'role': 'assistant', 'content': answer})
    validate_messages(result)
    return result


def save_json(messages, filename):
    validate_messages(messages)
    text = json.dumps(
        messages,
        ensure_ascii = False, # 한글을 ASCII로 변환하지 않음
        indent = 2, # 들여쓰기 공백 수
    )
    Path(filename).write_text(text,encoding='utf-8')




def main():
    history = make_library_history()

    history = append_pair(history, "열람실은 어디인가요?", "본관 3층입니다.")
    history = append_pair(history, "반납함은 어디인가요?", "1층 출입구입니다.")
    history = append_pair(history, "주말도 운영하나요?", "운영시간을 확인하세요.")

    validate_messages(history)


    file_path = ROOT / 'day49_basic.json'
    save_json(history, file_path)

    pp(f'저장 : {file_path}')

if __name__ == '__main__':
    main()



































