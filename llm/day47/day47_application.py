# day47_application.py
# 전자기기 리뷰의 규칙 기반 키워드 분포 계산

import csv
from pathlib import Path
import numpy as np
from util.print_util import pp, up

ROOT = Path(__file__).resolve().parent

REVIEWS = [
    '배터리 배터리 화면',
    '배송이 빠르고 화면이 선명해요',
    '화면 크기가 좋지만 배터리는 아쉬워요',
    '배송 배송이 너무 느립니다',
    '제품의 외관은 깔끔합니다'
]

KEYWORDS = ['배터리', '화면', '배송']

# 1차원 점수를 0~1 확률로 변환하는 함수
def softmax(vector):
    shifted = vector - np.max(vector)
    exps = np.exp(shifted)
    return exps / exps.sum()

# 등장 회수에 문장 첫 등장 위치 보너스를 부여한 규칙 점수 반환 함수
def score_review(review):
    scores = [] # score 저장 리스트
    for word in KEYWORDS: # 키워드 수만큼 반복
        count = review.count(word) # 리뷰내의 키워드 수
        index = review.find(word) # 리뷰에서 키워드 인덱스
        bonus = 1 / (1 + index) if index>=0 else 0 # 보너스 점수 계산
        scores.append(count + bonus) # 점수는 키워드 수 + 보너스 점수
    return np.array(scores, dtype=float) # 실수 배열로 변환 = Embedding

def main():

    path = ROOT / 'review_weights.csv'

    with path.open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['review'] + KEYWORDS + ['sum'])
        for review in REVIEWS:
            # 각 리뷰의 점수를 softmax로 가중치 연산
            weights = softmax(score_review(review))
            assert np.isclose(weights.sum(), 1.0) # 가중치 합이 1.0이어야 검사 통과
            writer.writerow(
                [review]
                + weights.round(5).tolist()
                + [round(float(weights.sum()), 5)]
            )
            pp(review, dict(zip(KEYWORDS, weights.round(3))))

        pp('저장: ', path)

if __name__ == '__main__':
    main()

up(5)











