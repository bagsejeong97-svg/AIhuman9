# day47_challenge.py
# 주제:
# day47_challenge.py
# 가상 재난 메시지 키워드 분석

import csv
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from util.print_util import pp, up
from include.graph_config import set_graph

set_graph(10, 8, 13)

ROOT = Path(__file__).resolve().parent

MESSAGES = [
    '건물 화재와 연기 발생',
    '엘리베이터에 사람 구조 요청',
    '주차장 연기 확인',
    '거리 가로등 고장 안내',
    '산불 화재 의심 신고',
    '구조 장비 지원 요청'
]

WORDS = ['화재', '연기', '구조']

# 사전 정의된 교육용 수치: 실제 위험도 지표가 아님
QUERY = np.array([1., 0.5])
KEYS = np.array([[1., 0.], [0.7, 0.3], [0., 1.]])
VALUES = np.array([3., 2., 2.5])

# 등장한 키워드만 정규화하는 함수
# scores: 점수, present:  등장 여부
# 반환값: 등장 키워드가 없으면 전부 0인 가중치 배열
def masked_softmax(scores, present):
    if not present.any(): # 등장한 적이 없다면
        return np.zeros_like(scores) # 0인 배열 리턴
    selected = scores[present] # 불리언 인덱싱으로 등장한 키워드의 점수만 추출
    # 가장 큰 점수를 빼서 지수 계산의 수치적 안정성 확보
    # 모든 값에서 같은 상수를 빼더라도 softmax 결과는 동일
    exp_scores = np.exp(selected - selected.max())
    # 기존 scores와 같은 크기의 0 배열 생성
    weights = np.zeros_like(scores)
    # 등장한 키워드 위치에만 정규화한 가중치 저장
    weights[present] = exp_scores / exp_scores.sum()
    return weights # 키워드별 최종 가중치 반환

# 임의의 Q/K 내적 점수를 키워드 등장 조건으로 정규화하는 함수
# message: 가상 접수 문자열
# 반환값: (가중치, 가상 점수)
def analyze(message):
    # 각 키워드가 메시지에 포함되었는지 검사
    present = np.array([word in message for word in WORDS])
    # K Q 내적을 Q의 차원에 루트로 나눔
    scores = KEYS @ QUERY / np.sqrt(QUERY.size)
    # 등장한 키워드의 점수만 softmax로 정규화해서 가중치 획득
    weights = masked_softmax(scores, present)
    # 가중치와 가중치 V 내적값 리턴
    return weights, float(weights @ VALUES)

def main():

    rows = [(message, *analyze(message)) for message in MESSAGES]

    path = ROOT / 'dispatch_priority.csv'

    with path.open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['message'] + WORDS + ['toy_score'])
        for message, weights, score in rows:
            writer.writerow([message] + weights.round(4).tolist() +
                            [round(score, 4)])
            pp(message, '가상 점수:', round(score, 3))

    fig, ax = plt.subplots()
    ax.bar(range(len(rows)), [item[2] for item in rows])
    ax.set_xticks(range(len(rows)), [f'M{i}' for i in range(1, 7)])
    ax.set_ylabel('Toy weighted score (not operational)')
    ax.set_title('Educational keyword analysis')
    fig.tight_layout()
    fig.savefig(ROOT / 'dispatch_priority.png', dpi=150)
    plt.close(fig)
    pp('저장:', path)

if __name__ == '__main__':
    main()

up(5)






















