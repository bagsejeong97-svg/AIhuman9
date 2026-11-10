# day50_ex1.py
# 주제:
#  Fine-turning 데이터 준비와 LoRaA의 학습 규모 및 출력 보정

import json
from pathlib import Path
import numpy as np

from util.print_util import pp

ROOT = Path(__file__).resolve().parent

DATA_DIR = ROOT / 'data' # 학습 데이터 저장 폴더

REPORT_DIR = ROOT / 'reports' # 품질 검사 보고서 저장 폴더

# 지시(instruction), 입력(input), 정답(output)으로 구성된 학습 예제
# 중복 레코드 1건과 정답이 비어 있는 레코드 1건을 의도적으로 포함
SAMPLES = [
    {"instruction": "고객 문의를 분류하세요", "input": "배송이 이틀 늦었어요",
     "output": "배송"},
    {"instruction": "고객 문의를 분류하세요", "input": "환불받고 싶어요",
     "output": "환불"},
    {"instruction": "고객 문의를 분류하세요", "input": "다른 색상이 왔어요",
     "output": "교환"},
    {"instruction": "고객 문의를 분류하세요", "input": "택배 조회가 안 됩니다",
     "output": "배송"},
    {"instruction": "고객 문의를 분류하세요", "input": "결제 취소해주세요",
     "output": "환불"},
    {"instruction": "고객 문의를 분류하세요", "input": "상품 크기가 달라요",
     "output": "교환"},
    {"instruction": "고객 문의를 분류하세요", "input": "택배를 못 받았어요",
     "output": "배송"},
    {"instruction": "고객 문의를 분류하세요", "input": "반품 처리해 주세요",
     "output": "환불"},
    {"instruction": "고객 문의를 분류하세요", "input": "배송이 이틀 늦었어요",
     "output": "배송"},  # 첫 번째 데이터와 중복
    {"instruction": "고객 문의를 분류하세요", "input": "상담원 연결",
     "output": "   "},  # 공백만 포함한 잘못된 정답
]

# 한건의 지시학습 데이터에서 필수 필드와 값의 형식을 검사하는 함수
def validate_sample(item):
    if not isinstance(item, dict):
        return False, '딕셔너리 형식이 아님' # 검증 성공 여부, 검증 메시지
    for field in ('instruction', 'input', 'output'):
        # 필드명(키)이 딕셔너리에 없거나 필드값(값)이 문자열이 아니면
        if field not in item or not isinstance(item[field], str):
            return False, f'{field} 누락 또는 문자열 형식 요류'
    if not item['instruction'].strip():
        return False, '지시가 비어있음'
    if not item['output'].strip():
        return False, '정답이 비어 있음'
    return True, '정상'

# 레코드 목록에서 잘못된 데이터와 완전히 중복된 데이터를 제거하는 함수
# samples : instruction/input/output 딕셔너리들의 리스트
# 변환값 : (accepted, rejected) 튜플
# accepted : 앞뒤 공백을 정리한 정상 데이터의 리스트
# rejected : 원본 행 번호와 제외 사유를 담은 리스트
def clean_samples(samples):
    accepted, rejected, seen = [], [], set()
    for row_number, item in enumerate(samples,start=1):
        valid,reason = validate_sample(item)
        if not valid:
            rejected.append({'row': row_number, 'reason': reason})
            continue
        cleaned = {field: item[field].strip() for field in ('instruction', 'input', 'output')}
        key = tuple(cleaned[field] for field in ('instruction', 'input', 'output'))
        if key in seen: # 이미 처리했다면
            rejected.append({'row': row_number, 'reason': '중복 데이터'})
            continue
        seen.add(key)
        accepted.append(cleaned)
    return accepted, rejected

# 정상 데이터 목록을 한 줄에 JSON객체 하나씩 저장하는 함수
# path : 저장할 파일 경로
# rows : 저장할 딕셔너리들의 리스트
def save_jsonl(path,rows):
    with path.open('w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')

# 전체 가중치와 LoRA의 파라미터 개수를 비교하는 함수
# input_dim : 기본 가중치 행렬의 입력 특징 수(n)
# output_dim : 기본 가중치 행렬의 입력 특징 수(m)
# ranks : 비교할 LoRA RANK 값들의  정수 리스트
def compare_parameters(input_dim, output_dim, ranks):
    full = input_dim * output_dim # 기본 행렬 W의 전체 요소수
    results = [] # 결과 저장 리스트
    for rank in ranks:
        # rank가 정수인지 , rank의 범위가 올바른지 확인
        if not isinstance(rank, int) or not 1<= rank <= min(input_dim, output_dim):
            raise ValueError('Rank는 1이상, 최소 차원 이하의 정수여야 함')
        # LoRA는 A(r*n)과 B(m*r)의 요소만 학습
        lora_count = rank * (input_dim + output_dim)
        percentage = round(lora_count / full * 100, 2) # LoRA비율
        results.append({
            'rank': rank,
            'full': full,
            'lora' : lora_count,
            'percent': percentage,
        })
    return results

# 기본 출력에 보정값을 더하는 LoRa의 직관을 보여주는 함수
# base :  기본 모델의 가상 출력, 1차원 NumPy 배열
# correction: 어댑터의 가상 보정값, base와 동일한 모양의 배열
# 반환값 : 두 배열을 요소별로 더한 NumPy 배열
def add_adapter_correction(base,correction):
    if base.shape != correction.shape:
        raise ValueError('기본 출력과 보정값의 크기가 같아야 함')
    return base + correction


def main():

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    pp('[ 실습 1] 지시학습 데이터 정리')
    accepted, rejected = clean_samples(SAMPLES)
    save_jsonl(DATA_DIR / 'train.jsonl', accepted)
    pp('원본: ',len(SAMPLES), '정상: ', len(accepted))

    pp('[실습 2] 데이터 품질 검사 및 제외 사유')
    for issue in rejected:
        pp('제외 행 : ', issue['row'], '제외 사유: ', issue['reason'])
    pp('[실습 3] LoRA의 작은 학습 규모 확인')
    comparisons = compare_parameters(4096,4096,[4,8,16])
    for info in comparisons:
        pp('Rank: ', info['rank'])
        pp('학습 숫자: ', info['lora'])
        pp('비율(%): ', info['percent'])
    base = np.array([2,3,4]) # 기본 출력의 가상 예씨
    correction = np.array([0,2,0]) # 보정값의 가상 예시
    result = add_adapter_correction(base, correction)
    pp('기본 출력: ',base, '보정 후 출력: ',result)
    report = {
        'original_count': len(SAMPLES),
        # 'accepted': accepted,
        'accepted_count': len(accepted),
        # 'rejected' : rejected,
        'rejected_count': len(rejected),
        'parameter_comparison' : comparisons,
        'base_output' : base.tolist(),
        'accepted_output' : result.tolist(),
        'note' : '파라미터 수 비교와 가상 보정에 대한 시연임, 실제 학습은 아님'
    }
    report_path = REPORT_DIR / 'quality_report.json'
    report_path.write_text(json.dumps(report, ensure_ascii=False,indent=2),encoding='utf-8')

    pp('학습 데이터: ',DATA_DIR / 'train.jsonl')
    pp('품질 보고서 : ',report_path)

if __name__ == '__main__':
    main()






































































