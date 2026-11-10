# day53_basic.py
# 주제:

import json
from util.print_util import pp, up

CATEGORIES = {"결제", "배송", "반품"}

URGENCIES = {"일반", "긴급"}

# 문의 객체의 필수 필드/허용값/문자열을 검증하는 함수
# data: json.loads()로 변환된 Python 객체
# 반환값: 검증을 통과한 dict 객체
def validate_inquiry(data):
    if not isinstance(data, dict):
        raise TypeError("객체가 필요합니다.")
    if set(data) != {"category", "urgency", "summary"}:
        raise ValueError("필드 구성이 올바르지 않습니다.")
    if data["category"] not in CATEGORIES:
        raise ValueError("지원하지 않는 문의 유형입니다.")
    if data["urgency"] not in URGENCIES:
        raise ValueError("긴급도가 올바르지 않습니다.")
    summary = data["summary"]
    if not isinstance(summary, str) or not summary.strip():
        raise ValueError("문의 요약이 비어 있습니다.")
    return data

def main():

    samples = [
        '{"category":"배송","urgency":"긴급","summary":"지연 문의"}',
        '{"category":"결제","urgency":"일반","summary":"확인"}',
    ]

    for raw in samples:
        try:
            result = validate_inquiry(json.loads(raw))
            pp(json.dumps(result, ensure_ascii=False))
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            pp("검증 실패:", exc)

if __name__ == '__main__':
    main()


















































