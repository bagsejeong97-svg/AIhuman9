# day50_application.py
# 주제:
import json
from pathlib import Path
from util.print_util import pp

ROOT = Path(__file__).resolve().parent

DATA_DIR = ROOT / 'data'  # 학습 데이터 저장 폴더 (`data/application_jobs.jsonl`)
REPORT_DIR = ROOT / 'reports'  # 품질 검사 보고서 저장 폴더 (`reports/application_jobs_report.json`)

INSTRUCTION = "채용 공고에서 직무, 지역, 경력을 JSON으로 추출하세요"

JOBS = {"백엔드 개발자", "프론트엔드 개발자", "데이터 분석가", "AI 엔지니어", "QA 엔지니어"}
REGIONS = {"서울", "부산", "대전", "대구", "인천"}
EXPERIENCES = {"신입", "경력", "경력 무관"}

# 11건의 소스 데이터 (정상, 중복, 오류 데이터 포함)
SOURCE = [
    ("서울 백엔드 개발자 신입 채용", "백엔드 개발자", "서울", "신입"),
    ("부산 데이터 분석가 경력 3년 이상", "데이터 분석가", "부산", "경력"),
    ("대전 AI 엔지니어 경력 무관 채용", "AI 엔지니어", "대전", "경력 무관"),
    ("대구 프론트엔드 개발자 신입 모집", "프론트엔드 개발자", "대구", "신입"),
    ("인천 QA 엔지니어 경력 채용", "QA 엔지니어", "인천", "경력"),
    ("서울 데이터 분석가 신입 공고", "데이터 분석가", "서울", "신입"),
    ("대전 백엔드 개발자 경력자 채용", "백엔드 개발자", "대전", "경력"),
    ("부산 QA 엔지니어 경력 무관", "QA 엔지니어", "부산", "경력 무관"),
    ("인천 AI 엔지니어 신입 모집", "AI 엔지니어", "인천", "신입"),
    ("서울 백엔드 개발자 신입 채용", "백엔드 개발자", "서울", "신입"),  # 중복 데이터
    ("대구 분석업무 모집", "데이터 분석가", "대구", ""),  # 빈 경력 값 (오류)
]

# 원본 SAMPLES 구성 (output은 JSON 문자열 형태로 생성)
SAMPLES = []
for text, job, region, exp in SOURCE:
    output_dict = {"job": job, "region": region, "experience": exp}
    SAMPLES.append({
        "instruction": INSTRUCTION,
        "input": text,
        "output": json.dumps(output_dict, ensure_ascii=False)
    })


# 4. 출력 JSON의 문법, 키, 허용 값 검사 함수
def validate_output(output_str):
    try:
        data = json.loads(output_str)
    except json.JSONDecodeError:
        return False, 'JSON 파싱 오류'

    if not isinstance(data, dict):
        return False, 'JSON 구조가 딕셔너리가 아님'

    required_keys = {"job", "region", "experience"}
    if set(data.keys()) != required_keys:
        return False, '필수 키(job, region, experience) 누락 또는 초과'

    if data["job"] not in JOBS:
        return False, f"유효하지 않은 직무: {data['job']}"
    if data["region"] not in REGIONS:
        return False, f"유효하지 않은 지역: {data['region']}"
    if data["experience"] not in EXPERIENCES:
        return False, f"유효하지 않은 경력 조건: {data['experience']}"

    return True, '정상'


# 5, 6. 전체 레코드 검증 및 중복 제거 함수
def clean_samples(samples):
    accepted, rejected, seen = [], [], set()
    for row_number, item in enumerate(samples, start=1):
        # 기본 딕셔너리 및 필드 검사
        if not isinstance(item, dict):
            rejected.append({'row': row_number, 'reason': '딕셔너리 형식이 아님'})
            continue

        valid_fields = True
        for field in ('instruction', 'input', 'output'):
            if field not in item or not isinstance(item[field], str) or not item[field].strip():
                rejected.append({'row': row_number, 'reason': f'{field} 누락 또는 빈 문자열'})
                valid_fields = False
                break
        if not valid_fields:
            continue

        # output JSON 유효성 및 허용 값 검사
        is_valid_out, reason = validate_output(item['output'])
        if not is_valid_out:
            rejected.append({'row': row_number, 'reason': reason})
            continue

        cleaned = {
            'instruction': item['instruction'].strip(),
            'input': item['input'].strip(),
            'output': item['output'].strip()
        }

        # 중복 체크 키 (instruction, input, output 모두 일치하는지 확인)
        key = (cleaned['instruction'], cleaned['input'], cleaned['output'])
        if key in seen:
            rejected.append({'row': row_number, 'reason': '중복 데이터'})
            continue

        seen.add(key)
        accepted.append(cleaned)

    return accepted, rejected


# JSONL 파일 저장 함수
def save_jsonl(path, rows):
    with path.open('w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    pp('[Application 과제] 채용 공고 핵심 정보 추출 데이터 정제 시작')
    accepted, rejected = clean_samples(SAMPLES)

    # 6. data/application_jobs.jsonl 저장
    jsonl_path = DATA_DIR / 'application_jobs.jsonl'
    save_jsonl(jsonl_path, accepted)

    # 8. 직무별 샘플 수 집계 및 출력
    job_counts = {job: 0 for job in JOBS}
    for item in accepted:
        out_data = json.loads