# day33_basic.py
# 주제: 쇼핑몰 고객 리뷰 토큰 빈도 분석

import re
from collections import Counter
from pathlib import Path
from util.print_util import pp
from include.graph_config import set_graph

set_graph(10, 8, 13)

BASE_DIR = Path(__file__).resolve().parent

DOCS = [
    " 배송이 정말 빨라요!!! ",
    "포장이 깔끔하고 배송도 좋네요.",
    "배송 늦음... 포장 불량",
    "상품 품질이 좋아요, 재구매!"
]


def normalize(text):
    # 1) 특수문자를 공백으로 바꾸고 중복 공백 줄이기
    text = re.sub(r'[^가-힣\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def inspect_documents(documents):
    # 데이터 원본을 수정하지 않고 별도의 정제 리스트 생성
    cleaned = [normalize(text) for text in documents]

    # 2) 리뷰별 토큰 리스트 출력
    token_lists = [text.split() for text in cleaned]
    for index, token in enumerate(token_lists,1):
        pp("리뷰별 토큰 리스트", index, token)

    # 3) 전체 단어 빈도 TOP 5 출력
    all_tokens = ' '.join(cleaned).split()
    counts = Counter(all_tokens)
    most_5 = counts.most_common(5)
    pp('전체 단어 빈도 TOP 5', most_5)

    # 4) 전체 리뷰 수와 고유 단어 수 표시
    total_reviews = len(documents)
    unique_words_count = len(set(all_tokens))
    pp('전체 리뷰 수', total_reviews)
    pp('고유 단어 수', unique_words_count)

    return cleaned


if __name__ == '__main__':
    inspect_documents(DOCS)


























