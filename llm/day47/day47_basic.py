# day47_basic.py
# 주제: 도서관 도서 제목 자동 분류 및 토큰화 비교 분석

import csv
from pathlib import Path
from collections import Counter
import re
from util.print_util import pp, up


TITLES = [
    '파이썬 데이터 분석 실습', '파이썬 알고리즘 안내',
    '데이터 시각화 설계', '머신러닝 프로젝트 가이드',
    '프로젝트 분석 방법', '데이터 분석과 통계',
    '실전 파이썬 프로젝트', '머신러닝 데이터 입문'
]

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'basic'
OUT.mkdir(parents=True, exist_ok=True)

rows = []

for text in TITLES:
    # 1. 공백 기준 토큰화
    space_tokens = text.split()

    # 2. 정규식 기반 토큰화
    regex_tokens = re.findall(r'\w+', text)

    # 통계 계산
    word_count_space = len(space_tokens)
    unique_count_space = len(set(space_tokens))

    # 최빈 단어 계산 (가장 빈도가 높은 단어)
    counter = Counter(space_tokens)
    most_common_word = counter.most_common(1)[0][0]

    row = {
        'title': text,
        'space_tokens': ' / '.join(space_tokens),
        'space_word_count': word_count_space,
        'space_unique_count': unique_count_space,
        'regex_tokens': ' / '.join(regex_tokens),
        'most_common_word': most_common_word
    }
    rows.append(row)

    pp('원문: ', text)
    pp('공백 토큰: ', space_tokens)
    pp('정규식 토큰: ', regex_tokens)


# CSV 파일 저장
csv_path = OUT / 'book_titles.csv'
with csv_path.open('w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

pp('결과 CSV 저장 완료: ', csv_path.resolve())

up(5)