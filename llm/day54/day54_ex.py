# day54_ex.py
# OpenAI Responses API를 이용한 미션 실습
# 4개 미션: meeting, email, sales, career

import csv
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from util.print_util import pp, up

ROOT = Path(__file__).resolve().parent

DATA = ROOT / 'data' # 입력 데이터 경로
OUT = ROOT / 'output' # 출력 데이터 경로

# 미션: meeting(회의록), email(이메일), sales(매출), career(채용)
MISSION = 'meeting'
# MISSION = 'email'
# MISSION = 'sales'
# MISSION = 'career'

# 버젼: 단독 실행할 프롬프트 버젼 (v1 또는 v2)
VERSION = 'v2'

# COMPARE가 True면 v1/v2 각각 API 1회 호출, False면 위 VERSION만 호출
COMPARE = True

# LIMIT: 회의록, 이메일, 채용공고에 적용할 입력 건수 (1 ~ 3)
LIMIT = 1

MISSIONS = {'meeting', 'email', 'sales', 'career'}

# 실습 결과의 정해진 필드명과 허용값을 명시하여 평가 재현성을 높이기 위한 스키마
SCHEMAS = {
    'meeting': {'decisions', 'tasks', 'risks'},
    'email': {'category', 'priority', 'reply', 'needs_human'},
    'sales': {'total_revenue', 'best_month', 'worst_month', 'insights'},
    'career': {'key_skills', 'evidence', 'cover_letter', 'missing'}
}

# system 프롬프트
SYSTEM = (
    '당신은 기업의 실무 데이터 처리 담당자임. 제공된 자료만 근거로 답변할 것.'
    '개인정보나 없는 사실을 지어내지 말 것. 출력은 JSON객체 하나만 작성할 것.'
    'Markdown 코드 블럭과 부가 설명을 붙이지 말 것.'
)

# 파일을 읽어 딕셔너리 리스트로 만드는 함수
# path: CSV파일의 Path
# 반환값: 열 이름을 키로 갖는 딕셔너리 리스트
def read_csv(path):
    with path.open('r', encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

# JSON과 CSV에 공통으로 사용할 파일을 안전하게 기록하는 함수
# path: 출력할 경로
# data: 직렬화할 파이썬 객체
def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True) # 상위 디렉토리 없으면 생성
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8',
    )

# 평가 결과를 CSV로 저장하는 함수
# path: 출력 CSV 파일 경로
# rows: 같은 키를 사용하는 딕셔너리 리스트
def save_csv(path, rows):
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

# 결과 문자열에 포함된 JSON 객체를 해석하는 함수
# raw: API가 생성한 원본 텍스트
# 반환값: 성공하면 dict, 실패하면 ValueError
def parse_json(raw):
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError('JSONDecodeError')
    if not isinstance(value, dict):
        raise ValueError('JSON문자열이 객체형태가 아닙니다.')
    return value

# 미션과 프롬프트 버젼에 알맞은 안내문을 생성하는 함수
# 반환값: API instructions로 전달할 문자열
def build_instructions(mission, version):
    if version == "v1":
        guides = {
            "meeting": "회의록의 중요한 내용을 JSON으로 정리해.",
            "email": "고객 이메일을 분석하고 적절한 답장을 JSON으로 써.",
            "sales": "매출 데이터를 분석하고 JSON 보고서를 써.",
            "career": "채용공고를 분석하고 자기소개서 초안을 JSON으로 써.",
        }
        return SYSTEM + " " + guides[mission]
    # v2
    guides = {
        "meeting": (
            "decisions: 결정된 사실 문자열 목록, "
            "tasks: 담당자/업무/기한이 있는 객체 목록, "
            "risks: 미확인 사항 문자열 목록. "
            "원문에 없는 담당자와 날짜는 '미정'으로 표시. "
            "각 tasks 원소는 owner, task, due 키를 포함."
        ),
        "email": (
            "category는 배송/환불/상품/기타 중 하나, priority는 high/normal "
            "중 하나, reply는 공손한 한국어 답장 초안, "
            "needs_human은 불리언. 금액 환불 확약/정책 추정은 금지. "
            "긴급 피해/법적 위협은 high로 표시."
        ),
        "sales": (
            "total_revenue는 제공된 월별 매출 합산 정수, "
            "best_month/worst_month는 매출 최대/최소의 YYYY-MM, "
            "insights는 수치 근거가 있는 3개 문자열 목록. "
            "증감 원인을 단정하지 말고 숫자 계산을 확인할 것."
        ),
        "career": (
            "key_skills는 공고에 나타난 필수 역량 문자열 목록, "
            "evidence는 지원자 사실로 확인된 근거 목록, "
            "cover_letter는 350자 내외 자기소개서 초안, "
            "missing은 근거 없는 요구 역량 목록. "
            "학력/수상/경력을 날조하지 말 것."
        ),
    }
    return SYSTEM + " 정확한 키: " + guides[mission]

# 실제 API 응답 1회를 요청하는 함수
# client: API키로 초기화된 OpenAI 객체
# model: 사용 가능한 모델 ID
# instructions: 시스템 수준 작업 지시문
# user_input: 모델에 전달하는 업무 자료
# 반환값: 응답 문자열, 토큰 정보, 응답 시간(초)
def call_llm(client, model, instructions, user_input):
    started = time.perf_counter() # 처리 시간 측정 시작
    # 요청을 보내 응답 획득
    response = client.responses.create(
        model=model,
        instructions=instructions,
        input=user_input,
        max_output_tokens=1600, # 출력 토큰 상한
        store=False # 응답을 서버에 저장하지 않음
    )
    elapsed = round(time.perf_counter() - started, 2) # 소요 시간
    # response 객체의 usage 속성이 있으면 값을 획득, 없으면 None 획득
    usage = getattr(response, 'usage', None) # 사용량
    tokens = {
        'input_tokens': getattr(usage, 'input_tokens', None), # 입력 토큰 사용량
        'output_tokens': getattr(usage, 'output_tokens', None) # 출력 토큰 사용량
    }
    return response.output_text, tokens, elapsed # 응답 텍스트, 입/출력토큰사용량, 소요시간

# 사전에 약속한 필드가 포함되어 있는지 점검하는 함수
# mission: 선택된 업무 종류
# data: JSON 파싱된 모델 응답
# 반환값: (0~100 평가 점수, 오류 코드 목록)
def evaluate(mission, data):
    missing = SCHEMAS[mission] - set(data) # 필수 필드 누락 찾기
    errors = [f'MISSING:{key}' for key in sorted(missing)]
    score = round(100 * (1-len(missing)) / len(SCHEMAS[mission]), 2)
    if mission == 'email':
        if data.get('category') not in {'배송', '환불', '상품', '기타'}:
            errors.append('잘못된 카테고리')
            score = max(0, score - 15)
        if data.get('priority') not in {'high', 'normal'}:
            errors.append('잘못된 우선순위')
            score = max(0, score - 15)
        if not isinstance(data.get('needs_human'), bool):
            errors.append('잘못된 needs_human')
            score = max(0, score - 15)
    if mission == 'sales':
        if not isinstance(data.get('total_revenue'), int):
            errors.append('잘못된 total_revenue')
            score = max(0, score - 15)
    return score, errors

# 판매 데이터를 원문으로 전달하기 전에 합계를 검증하는 함수
# rows: 12개월 매출 행
# 반환값: 총 매출, 최대/최소 매출 발생 월
def sales_reference(rows):
    values = [(row['month'], int(row['revenue_krw'])) for row in rows]
    return {
        'total_revenue': sum(amount for _, amount in values),
        'best_month': max(values, key=lambda item: item[1])[0],
        'worst_month': min(values, key=lambda item: item[1])[0]
    }

# 미션별 입력을 구성하는 함수
# mission : 4개 중 선택한 실무 미션
# limit : 입력할 업무 문서 건수. 비용을 줄이기 위해 기본 1건
# 반환값 : (입력 문자열, 참고 정답 또는 None)
def build_input(mission, limit):
    if mission == "meeting":
        rows = read_csv(DATA / "meeting_notes.csv")[:limit]
        text = "\n\n".join(r["meeting_text"] for r in rows)
        return "다음 회의록을 처리해:\n" + text, None
    if mission == "email":
        rows = read_csv(DATA / "customer_emails.csv")[:limit]
        return "다음 이메일을 각각 처리해:\n" + "\n".join(
            f"[{row['id']}] {row['message']}" for row in rows
        ), None
    if mission == "sales":
        rows = read_csv(DATA / "monthly_sales.csv")
        ref = sales_reference(rows)  # 총계 검증 기준은 Python 계산
        text = "\n".join(
            f"{r['month']} 매출={r['revenue_krw']}원, "
            f"주문={r['orders']}건" for r in rows
        )
        return "다음 월별 실적을 보고서로 작성해:\n" + text, ref
    rows = read_csv(DATA / "job_postings.csv")[:limit]
    applicant = (DATA / "fictional_applicant.txt").read_text(
        encoding="utf-8"
    )
    text = "\n".join(f"{r['role']}: {r['requirements']}" for r in rows)
    return f"채용 공고:\n{text}\n가상의 지원자 정보:\n{applicant}", None

def main():

    if MISSION not in MISSIONS:
        raise ValueError('MISSION을 확인해 주세요.')

    if VERSION not in {'v1', 'v2'}:
        raise ValueError('VERSION을 확인해 주세요.')

    if not isinstance(LIMIT, int) or not 1 <= LIMIT <= 3:
        raise ValueError('LIMIT은 1~3 사이의 정수입니다.')

    load_dotenv(ROOT / '.env')

    key = os.getenv('OPENAI_API_KEY', '').strip()

    if not key or not key.startswith('sk-proj'):
        raise SystemExit('.env의 OPENAI_API_KEY를 점검해 주세요!')

    model = os.getenv('OPENAI_MODEL', 'gpt-4.1-mini')

    client = OpenAI(api_key=key, timeout=45, max_retries=1)

    user_input, reference = build_input(MISSION, LIMIT)

    versions = ['v1', 'v2'] if COMPARE else [VERSION]

    pp(f'미션={MISSION}, 모델={model}, API 호출={len(versions)}회')

    rows = []

    for version in versions:

        instruction = build_instructions(MISSION, version)

        try:
            raw, tokens, elapsed = call_llm(client, model, instruction, user_input)
            try:
                data = parse_json(raw)
                score, errors = evaluate(MISSION, data)
            except ValueError as e:
                data, score, errors = {}, 0, [str(e)]
        except (OpenAIError, OSError) as e:
            pp(f'API 호출 실패: {type(e).__name__}')
            continue

        timestamp = datetime.now(timezone.utc).isoformat()

        record = {
            'mission': MISSION,
            'version': version,
            'model': model,
            'created_utc': timestamp,
            'score': score,
            'errors': ';'.join(errors) or 'OK',
            'seconds': elapsed,
            'input_tokens': tokens['input_tokens'],
            'output_tokens': tokens['output_tokens'],
            'response_text': raw
        }

        rows.append(record)

        save_json(OUT / f'{MISSION}_{version}.json', {
            'metadata': record, 'parsed': data, 'reference': reference
        })

        pp(
            f'{version}: 형식 점수={score}, 오류={errors or "없음"}'
            f', 소요={elapsed}초, 토큰={tokens}'
        )

        if reference and isinstance(data, dict):
            checks = {k: data.get(k)==val for k, val in reference.items()}
            pp('Python 정답과 일치 여부: ', checks)

    save_csv(OUT / f'{MISSION}_comparison.csv', rows)

    if len(rows) == 2:
        pp('형식 점수 변화(v2 - v1): ', rows[1]['score'] - rows[0]['score'])

    pp('결과 폴더: ', OUT)

if __name__ == '__main__':
    main()

up(5)































