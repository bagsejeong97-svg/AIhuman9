# day35_basic.py
# 주제: 음성 인식(STT) 평가 지표(WER, CER) 계산

import re
from jiwer import wer, cer, process_words
from util.print_util import pp
import unicodedata

PAIRS = [
    ("첫 번째 상자를 오른쪽 선반으로 이동", "첫 번째 상자를 오른쪽 선반으로 이동"),
    ("파란 상자를 창고 입구에 배치", "파란 상자를 창고에 배치"),
    ("재고 수량 다섯 개를 확인", "재고 수량 네 개를 확인"),
    ("출고 목록을 다시 확인", "출고 목록을 반드시 다시 확인"),
    ("작업 구역 조명을 켜 주세요", "작업 구역 조명 켜 주세요")
]


def normalize(text):
    text = unicodedata.normalize('NFC', text).lower()  # 한국어 정규화
    text = re.sub(r'[^가-힣a-z0-9\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def main(pairs):
    results = []

    # 데이터 정규화 및 평가 결과 저장
    for i, (left, right) in enumerate(pairs, 1):
        ref_n = normalize(left)
        hyp_n = normalize(right)

        counts = process_words(ref_n, hyp_n)
        result = {
            'reference': left,
            'hypothesis': right,
            'WER': wer(ref_n, hyp_n),
            'CER': cer(ref_n, hyp_n),
            'S': counts.substitutions,
            'D': counts.deletions,
            'I': counts.insertions,
        }
        results.append(result)

        # 문장별 결과 출력
        pp(f'--- {i}번 문장 ---')
        pp(f'정답: {result["reference"]}')
        pp(f'인식: {result["hypothesis"]}')
        pp(f'WER: {result["WER"]:.2%}')
        pp(f'CER: {result["CER"]:.2%}')
        pp(f'S (Substitutions): {result["S"]}')
        pp(f'D (Deletions): {result["D"]}')
        pp(f'I (Insertions): {result["I"]}')

    # WER 기준 최악의 결과 찾기
    worst_r = max(results, key=lambda x: x['WER'])
    worst_i = results.index(worst_r) + 1

    pp('=' * 30)
    pp(f'[WER 기준 최악의 문장] ({worst_i}번)')
    pp(f"정답: {worst_r['reference']}")
    pp(f"인식: {worst_r['hypothesis']}")
    pp(f"WER: {worst_r['WER']:.2%}")
    pp(f"CER: {worst_r['CER']:.2%}")

    # CER 기준 최악의 결과 찾기
    worst_c = max(results, key=lambda x: x['CER'])
    worst_ci = results.index(worst_c) + 1

    pp('=' * 30)
    pp(f'[CER 기준 최악의 문장] ({worst_ci}번)')
    pp(f"정답: {worst_c['reference']}")
    pp(f"인식: {worst_c['hypothesis']}")
    pp(f"WER: {worst_c['WER']:.2%}")
    pp(f"CER: {worst_c['CER']:.2%}")


if __name__ == "__main__":
    main(PAIRS)