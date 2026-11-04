# day36_ex2.py
# 실제 청취자가 기록한 5점 평가 결과 집계

from pathlib import Path
import pandas as pd

from util.print_util import pp

# 청취자가 기록한 점수가 있는 CSV 경로
PATH = Path(__file__).parent / 'outputs' / 'listening_scores.csv'

def main():

    if not PATH.exists():
        pp('먼저 day36_ex1.py를 실행해서 평가표를 생성하세요.')
        return

    # 파일 저장 형식(utf-8-sig)에 맞춰 인코딩 수정
    try:
        df = pd.read_csv(PATH, encoding='utf-8-sig')
    except UnicodeDecodeError:
        df = pd.read_csv(PATH, encoding='cp949')

    if df.empty:
        pp('평가 자료가 없습니다.')
        return

    # 점수 컬럼들 타입 숫자 변환
    for col in ['clarity','naturalness']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    valid = df.dropna(subset=['evaluator','clarity','naturalness']) # 결측치 제거
    valid = valid[
        valid['clarity'].between(1,5) # 명료도 값이 1~5 범위
        & valid['naturalness'].between(1,5) # 자연스러움 값이 1~5 범위
    ]

    if valid.empty:
        pp('유효한 평가가 없습니다. 평가자와 명료도, 자연스러움 점수를 1~5범위 입력하세요.')
        return

    summary = valid.groupby('clip_id',as_index=False).agg(
        n=('evaluator','count'), # 평가자 수
        clarity_mean=('clarity','mean'), # 명료도 평균
        naturalness_mean=('naturalness','mean'), # 자연스러움 평균
    )

    summary.to_csv(PATH.parent/ 'score_summary.csv', index=False, encoding='utf-8-sig')

    pp(summary.round(2).to_string(index=False))

if __name__ == '__main__':
    main()