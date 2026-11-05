import json
from pathlib import Path
from util.print_util import pp

ROOT = Path(__file__).resolve().parent

DATA_DIR = ROOT / 'data'  # 학습 데이터 저장 폴더
REPORT_DIR = ROOT / 'reports'  # 품질 검사 보고서 저장 폴더

# 과제 요구사항에 따른 지시문과 카테고리 정의
INSTRUCTION = "학사 공지를 수업, 장학, 시설 중 하나로 분류하세요"
CATEGORIES = {"수업", "장학", "시설"}

# 대학 캠퍼스 공지사항 RAW 데이터 (정상 9건 + 중복 1건 + 빈 정답 1건)
RAW = [
    ("오늘 프로그래밍 강의실이 301호로 변경되었습니다", "수업"),
    ("자료구조 수업은 학과 행사로 휴강합니다", "수업"),
    ("금요일 알고리즘 보강 수업을 진행합니다", "수업"),
    ("국가장학금 신청 기간이 시작되었습니다", "장학"),
    ("교내 성적우수장학생 명단을 안내합니다", "장학"),
    ("근로장학금 신청서를 제출하세요", "장학"),
    ("중앙도서관 열람실 운영 시간을 연장합니다", "시설"),
    ("체육관 바닥 보수로 이용이 제한됩니다", "시설"),
    ("학생회관 출입문 공사를 진행합니다", "시설"),
    ("오늘 프로그래밍 강의실이 301호로 변경되었습니다", "수업"),  # 중복 데이터
    ("다음 학기 장학 심사 안내", " "),  # 빈 정답 데이터
]

# SAMPLES 구성
SAMPLES = [{"instruction": INSTRUCTION, "input": text, "output": label} for text, label in RAW]


# 1. 필수 필드 및 값의 형식 검사 함수
def validate_record(item):
    if not isinstance(item, dict):
        return False, '딕셔너리 형식이 아님'
    for field in ('instruction', 'input', 'output'):
        if field not in item or not isinstance(item[field], str):
            return False, f'{field} 누락 또는 문자열 형식 오류'
    if not item['instruction'].strip():
        return False, '지시가 비어있음'
    if not item['output'].strip():
        return False, '정답이 비어 있음'
    if item['output'] not in CATEGORIES:
        return False, '유효하지 않은 카테고리'
    return True, '정상'


# 2. 공백 정리 및 중복·오류 데이터 제거 함수
def clean_records(records):
    accepted, rejected, seen = [], [], set()
    for row_number, item in enumerate(records, start=1):
        valid, reason = validate_record(item)
        if not valid:
            rejected.append({'row': row_number, 'reason': reason})
            continue

        # 앞뒤 공백 정리
        cleaned = {field: item[field].strip() for field in ('instruction', 'input', 'output')}

        # 중복 체크 키 생성
        key = (cleaned['instruction'], cleaned['input'], cleaned['output'])
        if key in seen:
            rejected.append({'row': row_number, 'reason': '중복 데이터'})
            continue

        seen.add(key)
        accepted.append(cleaned)
    return accepted, rejected


# 3. JSONL 저장 함수
def save_jsonl(path, rows):
    with path.open('w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    pp('[ 과제 수행 ] 캠퍼스 공지사항 데이터셋 정제 시작')
    accepted, rejected = clean_records(SAMPLES)

    # JSONL 파일 저장
    jsonl_path = DATA_DIR / 'basic_campus_train.jsonl'
    save_jsonl(jsonl_path, accepted)

    # 카테고리별 건수 집계
    category_counts = {cat: 0 for cat in CATEGORIES}
    for item in accepted:
        if item['output'] in category_counts:
            category_counts[item['output']] += 1

    # 품질 보고서(JSON) 작성 및 저장
    report = {
        'total_count': len(SAMPLES),
        'accepted_count': len(accepted),
        'rejected_count': len(rejected),
        'category_counts': category_counts,
        'rejected_details': rejected
    }

    report_path = REPORT_DIR / 'basic_campus_report.json'
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

    # 결과 출력
    pp('원본 전체 건수:', len(SAMPLES))
    pp('정상 데이터 건수:', len(accepted))
    pp('제외 데이터 건수:', len(rejected))
    pp('카테고리별 건수:', category_counts)

    for issue in rejected:
        pp(f"제외 행: {issue['row']}, 사유: {issue['reason']}")

    pp('저장된 JSONL 파일:', jsonl_path)
    pp('저장된 리포트 파일:', report_path)


if __name__ == '__main__':
    main()