# day50_application.py
# 주제:
import json
from pathlib import Path
from util.print_util import pp

ROOT = Path(__file__).resolve().parent

DATA_DIR = ROOT / 'data'
REPORT_DIR = ROOT / 'reports'

INSTRUCTION = "채용 공고에서 직무, 지역, 경력을 JSON으로 추출하세요"

JOBS = {"백엔드 개발자", "프론트엔드 개발자", "데이터 분석가", "AI 엔지니어", "QA 엔지니어"}
REGIONS = {"서울", "부산", "대전", "대구", "인천"}
EXPERIENCES = {"신입", "경력", "경력 무관"}


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
    ("서울 백엔드 개발자 신입 채용", "백엔드 개발자", "서울", "신입"),
    ("대구 분석업무 모집", "데이터 분석가", "대구", ""),
]

SAMPLES = []
for text, job, region, exp in SOURCE:
    output_dict = {"job": job, "region": region, "experience": exp}
    SAMPLES.append({
        "instruction": INSTRUCTION,
        "input": text,
        "output": json.dumps(output_dict, ensure_ascii=False)
    })

# 구조화 정답 데이터의 필드와 허용 값에 맞는지 확인하는 함수
# text : JSON 문자열 형태의 예상 정답
# 반환값 : (정상 여부 bool, 오류 사유 str)
def validate_output(text):
    if not isinstance(text, str) or not text.strip():
        return False, "정답 문자열이 비어 있음"
    try:
        obj = json.loads(text)  # JSON 문자열을 Python 객체로 변환
    except json.JSONDecodeError:
        return False, "JSON 구문 오류"
    if not isinstance(obj, dict) or set(obj) != {
            "job", "region", "experience"}:
        return False, "정답 JSON 필드 구성 오류"
    if obj["job"] not in JOBS or obj["region"] not in REGIONS:
        return False, "직무 또는 지역 값 오류"
    if obj["experience"] not in EXPERIENCES:
        return False, "경력 조건 값 오류"
    return True, "정상"



# day50_application.py
# 채용 공고의 직무/지역/경력 정보를 JSON 정답으로 생성

import json
from collections import Counter
from pathlib import Path
from util.print_util import pp, up

ROOT = Path(__file__).resolve().parent

INSTRUCTION = "채용 공고에서 직무, 지역, 경력을 JSON으로 추출하세요"

JOBS = {"백엔드 개발자", "프론트엔드 개발자", "데이터 분석가", "AI 엔지니어", "QA 엔지니어"}

REGIONS = {"서울", "부산", "대전", "대구", "인천"}

EXPERIENCES = {"신입", "경력", "경력 무관"}

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
    ("서울 백엔드 개발자 신입 채용", "백엔드 개발자", "서울", "신입"),
    ("대구 분석업무 모집", "데이터 분석가", "대구", "")
]

# 구조화 정답 데이터의 필드와 허용 값에 맞는지 확인하는 함수
# text : JSON 문자열 형태의 예상 정답
# 반환값 : (정상 여부 bool, 오류 사유 str)
def validate_output(text):
    if not isinstance(text, str) or not text.strip():
        return False, "정답 문자열이 비어 있음"
    try:
        obj = json.loads(text)  # JSON 문자열을 Python 객체로 변환
    except json.JSONDecodeError:
        return False, "JSON 구문 오류"
    if not isinstance(obj, dict) or set(obj) != {
            "job", "region", "experience"}:
        return False, "정답 JSON 필드 구성 오류"
    if obj["job"] not in JOBS or obj["region"] not in REGIONS:
        return False, "직무 또는 지역 값 오류"
    if obj["experience"] not in EXPERIENCES:
        return False, "경력 조건 값 오류"
    return True, "정상"

# 채용 공고와 정답 레이블로 지시학습 목록을 작성하는 함수
# source: (공고, 직무, 지역, 경력) 튜플들의 리스트
# 반환값: instruction/input/output 구조를 가진 딕셔너리 리스트
def make_samples(source):
    rows = []
    for notice, job, region, experience in source:
        answer = {'job': job, 'region': region, 'experience': experience}
        rows.append({
            'instruction': INSTRUCTION,
            'input': notice,
            'output': json.dumps(answer, ensure_ascii=False)
        })
    return rows

# 정답 JSON이 올바른 자료만 고유하게 보존하는 함수
# records : 생성한 지시학습 레코드 리스트
# 반환값 : (정상 레코드 리스트, 제외 사유 리스트)
def clean_records(records):
    accepted, rejected, seen = [], [], set()
    for index, row in enumerate(records, 1):
        if not isinstance(row.get("input"), str) or not row["input"].strip():
            rejected.append({"row": index, "reason": "공고 내용 없음"})
            continue
        valid, reason = validate_output(row.get("output"))
        if not valid:
            rejected.append({"row": index, "reason": reason})
            continue
        clean = {key: row[key].strip() for key in
                 ("instruction", "input", "output")}
        key = (clean["instruction"], clean["input"])
        if key in seen:
            rejected.append({"row": index, "reason": "중복 공고"})
            continue
        seen.add(key)
        accepted.append(clean)
    return accepted, rejected

def main():

    data_dir, report_dir = ROOT / 'data', ROOT / 'report'
    data_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    accepted, rejected = clean_records(make_samples(SOURCE))

    target = data_dir / 'application_jobs.jsonl'
    with target.open('w', encoding='utf-8') as f:
        for row in accepted:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')

    counts = dict(Counter(json.loads(row['output'])['job'] for row in accepted))

    report = {
        'total': len(accepted),
        'accepted': len(accepted),
        'rejected': len(rejected),
        'job_counts': counts
    }

    (report_dir / 'application_jobs_report.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )

    pp('정상: ', len(accepted), ', 제외: ', len(rejected))
    pp('직무별 건수: ', counts)
    pp('제외 사유: ', rejected)

if __name__ == '__main__':
    main()

up(5)
























































































