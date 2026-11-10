# day50_challenge.py
# 주제:
# day50_challenge.py
# IT 보안 이벤트의 위험도 분류 데이터셋 제작과 규칙 기준선 평가

import json
import re
from collections import Counter
from pathlib import Path
from util.print_util import pp, up

ROOT = Path(__file__).resolve().parent

INSTRUCTION = "보안 이벤트 위험도를 높음, 보통, 낮음으로 분류하세요"

LABELS = {"높음", "보통", "낮음"}

EVENTS = [
    ("사내 파일 서버에서 랜섬웨어 의심 파일 발견", "높음"),
    ("관리자 계정에 외부인 침해 흔적 확인", "높음"),
    ("업무용 PC에서 데이터 유출 의심 행위 발견", "높음"),
    ("관리자 로그인 성공 후 낯선 해외 접속 탐지", "높음"),
    ("사내 메일로 악성 링크 신고 접수", "보통"),
    ("직원 계정의 로그인 실패 반복", "보통"),
    ("의심스러운 첨부파일 다운로드 시도", "보통"),
    ("공용 와이파이에서 비정상 접속 알림", "보통"),
    ("정기 보안 업데이트 정상 완료", "낮음"),
    ("예정된 서버 점검 작업 종료", "낮음"),
    ("백업 시스템 정상 동작 확인", "낮음"),
    ("사내 보안 교육 수강 완료", "낮음"),
    ("서버에서 대량의 파일이 암호화된 정황 확인", "높음"),
    ("반복 로그인 실패 신고 접수", "보통"),
    ("정기 시스템 점검 정상 완료", "낮음"),
    ("사내 파일 서버에서 랜섬웨어 의심 파일 발견", "높음"),
    ("정체불명의 이벤트", ""),
]

# 띄어쓰기와 영문 대소문자 차이를 무시한 중복 식별키 생성 함수
# text: 정규화하려는 이벤트 설명 문자열
def normalize_text(text):
    return re.sub(r"\s+", "", text).casefold()

# 원본 보안 이벤트에서 지시학습 데이터와 제외 내역을 만드는 함수
# events: (보안 이벤트 내용, 위험도 정답) 튜플 리스트
# 반환값: (정상 샘플, 제외 이력), 각각 딕셔너리 리스트
def prepare_samples(events):
    accepted, rejected, seen = [], [], set()
    for index, (text, label) in enumerate(events, 1):
        if not text.strip() or label not in LABELS:
            rejected.append({'row': index, 'reason': '입력/정답 오류'})
            continue
        key = normalize_text(text)
        if key in seen:
            rejected.append({'row': index, 'reason': '중복 이벤트'})
            continue
        seen.add(key)
        accepted.append({
            'instruction': INSTRUCTION,
            'input': text.strip(),
            'output': label
        })
    return accepted, rejected

# 학습과 평가의 입력 문장이 겹치지 않도록 그룹을 나누는 함수
# rows: 중복 제거된 지시학습 데이터 리스트
# test_every: 몇 건마다 하나를 테스트로 둘지 결정하는 양의 정수
# 반환값: (train, test) 두 개의 분할 리스트
def split_records(rows, test_every=4):
    if not isinstance(test_every, int) or test_every < 2:
        raise ValueError("test_every 2이상의 정수여야 함")
    train, test = [], []
    for index, item in enumerate(rows):
        if index % test_every == 0:
            test.append(item)
        else:
            train.append(item)
    train_keys = {normalize_text(row['input']) for row in train}
    test_keys = {normalize_text(row['input']) for row in test}
    if train_keys & test_keys: # 같은 키가 있다면
        raise ValueError('Train/Test에 같은 입력이 들어 있음')
    return train, test

# 단순 키워드 규칙만으로 위험도를 예측하는 기준선 함수
# text: 평가할 보안 이벤트 설명
# 반환값: 높음, 보통, 낮음 중 하나
def baseline_predict(text):
    high = ('랜섬웨어', '침해', '유출', '해외 접속')
    medium = ('악성', '로그인 실패', '첨부파일', '비정상')
    if any(term in text for term in high):
        return '높음'
    if any(term in text for term in medium):
        return '보통'
    return '낮음'

# 평가지의 정답과 기준선의 예측값으로 정확도를 계산하는 함수
# test: 지시학습 데이터 딕셔너리 리스트
# 반환값: (정확도 float, 오분류 딕셔너리 리스트), 정확도: 맞힌 건수 / 테스트 전체 건수
def evaluate(test):
    wrong, correct = [], 0
    for item in test:
        predicted = baseline_predict(item['input'])
        if predicted == item['output']: # 예측이 맞으면
            correct += 1
        else:
            wrong.append({
                'input': item['input'],
                'expected': item['output'],
                'predicted': predicted
            })
    accuracy = correct / len(test) if test else 0.0
    return accuracy, wrong

# JSONL 파일에 학습 데이터를 한 건씩 저장하는 함수
def save_jsonl(path, records):
    with path.open('w', encoding='utf-8') as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')

def main():

    data_dir, report_dir = ROOT / 'data', ROOT / 'report'
    data_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    rows, rejected = prepare_samples(EVENTS)

    train, test = split_records(rows)

    accuracy, wrong = evaluate(test)

    save_jsonl(data_dir / 'challenge_train.jsonl', train)
    save_jsonl(data_dir / 'challenge_test.jsonl', test)

    report = {
        'original': len(EVENTS),
        'accepted': len(rows),
        'rejected': rejected,
        'train': len(train),
        'test': len(test),
        'test_accuracy': round(accuracy, 4),
        'train_label_counts': dict(Counter(row['output'] for row in train)),
        'test_label_counts': dict(Counter(row['output'] for row in test)),
        'misclassified': wrong
    }

    (report_dir / 'challenge_security_report.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n',encoding= 'utf-8'
    )

    pp('정상: ', len(rows), ', 제외: ', len(rejected))
    pp('Train: ', len(train), ', Test: ', len(test))
    pp('기준선 정확도: ', f'{accuracy:.1%}')
    pp('오분류 사례: ', wrong)

if __name__ == '__main__':
    main()

up(5)
























