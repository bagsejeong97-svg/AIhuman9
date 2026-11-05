# day49_challenge.py
# 주제:
import json
from pathlib import Path
from util.print_util import pp

ROOT = Path(__file__).resolve().parent

ROLE_SET = {'system','user','assistant'}

TOKENIZER_MODEL_ID = 'Qwen/Qwen2.5-0.5B-Instruct'

MAX_TURNS = 4




def validate_messages(messages):
    if not isinstance(messages, list):
        raise TypeError('messages는 리스트여야 합니다.')
    for index, message in enumerate(messages):
        if not isinstance(message, dict):
            raise TypeError(f'{index}번 메세지는 딕셔너리여야 합니다.')
        if message.get('role') not in ROLE_SET:
            raise ValueError(f'{index}번 메시지의 역할이 올바르지 않습니다.')
        if not isinstance(message.get('content'), str):
            raise TypeError(f'{index}번 메시지는 문자열이어야 합니다.')
    return True


def make_history(facts):
    # 요구사항 3: system 본문에 사실 메모를 결합
    fact_str = ", ".join([f"{k}: {v}" for k, v in facts.items()])
    system_content = f"여행 일정 상담사입니다.\n확인된 정보: {fact_str}"

    return [{'role': 'system', 'content': system_content}]


def add_turn(messages, question, answer):
    result = list(messages)
    result.append({'role': 'user', 'content': question})
    result.append({'role': 'assistant', 'content': answer})
    validate_messages(result)
    return result


def keep_recent_turn(messages, max_turns=2):
    validate_messages(messages)
    system = [m for m in messages if m['role'] == 'system']
    dialog = [m for m in messages if m['role'] != 'system']
    return system + (dialog[-2 * max_turns:] if max_turns else [])


def main():
    facts = {"도시": "부산", "예산": "20만원", "이동수단": "대중교통"}

    # 1. 사실이 포함된 시스템 메시지로 시작
    history = make_history(facts)

    pairs = [
        ("부산 여행을 갈게요.", "부산 여행 계획을 도와드리겠습니다."),
        ("예산은 20만원이에요.", "20만원 기준으로 제안하겠습니다."),
        ("대중교통을 이용해요.", "버스와 지하철 중심으로 정리하겠습니다."),
        ("마지막 날 코스를 추천해 주세요.", "해변과 시장을 추천합니다."),
    ]

    # 2. 4턴 대화 누적 추가
    for q, a in pairs:
        history = add_turn(history, q, a)

    # 3. 최근 2턴만 남기기
    recent = keep_recent_turn(history, max_turns=2)

    # 4. 요구사항 6: 문맥(예산 등) 보존 성공 여부를 assert로 자동 검증
    # 최근 2턴으로 잘렸어도 시스템 메시지 덕분에 '20만원' 정보가 유지되어야 함
    system_content = recent[0]['content']
    assert "20만원" in system_content, "예산 정보가 시스템 메시지에 유지되어야 합니다!"
    assert "부산" in system_content, "도시 정보가 시스템 메시지에 유지되어야 합니다!"
    pp("Assertion 검증 통과: 핵심 사실이 잘 보존되었습니다.")

    # 5. JSON 저장 (개인정보 제외)
    file_path = ROOT / 'day49_travel_history.json'
    text = json.dumps(recent, ensure_ascii=False, indent=2)
    Path(file_path).write_text(text, encoding='utf-8')
    pp(f"저장 완료: {file_path}")


if __name__ == '__main__':
    main()


























































