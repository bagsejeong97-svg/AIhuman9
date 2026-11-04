# day35_challenge.py
# 주제:
import csv
import re
import time
import unicodedata
import wave
from pathlib import Path
import pandas as pd
from jiwer import wer, cer, process_words
from faster_whisper import WhisperModel
import numpy as np
from util.print_util import pp

BASE = Path(__file__).resolve().parent
OUTPUT = BASE / "results" / 'day35_challenge_result.csv'

KEYWORDS = ("승강장", "출발", "변경")

SAMPLES = [
    ("열차 출발 시간은 오전 열 시입니다",
     "열차 출발 시간은 오전 열 시입니다", 2.1, 6.0),
    ("다음 열차는 삼 번 승강장에 도착합니다",
     "다음 열차는 삼 번에 도착합니다", 2.4, 7.0),
    ("열차 출발 장소가 변경되었습니다",
     "열차 장소가 되었습니다", 2.9, 6.0),
    ("안전선 안쪽에서 기다려 주세요",
     "안전선 안쪽에서 기다려 주세요", 1.5, 5.0)]

result=[]


for i,(ref,hyp,hyp_s,ref_s) in enumerate(SAMPLES,start=1):
    wer_score = round(wer(ref,hyp),3)
    cer_score = round(cer(ref,hyp),3)
    rtf = round(hyp_s/ref_s,2)

    status = '정상'
    ref_n = ref.split()
    hyp_n = hyp.split()

    for k in KEYWORDS:
        if k in ref_n:
            if k not in hyp_n:
                pp(f'누락 된 키워드 : {k}\n정답 문장 : {ref}\n예측 문장 : {hyp}')
                pp('위험 키워드 누락 건에 대해 자동 배포 금지(검토 필요) 판정을 내리세요.')

                status = f"자동 배포 금지 (키워드 '{k}' 누락)"
                break

    result.append([i,ref, hyp,wer_score,cer_score,rtf,status])

df = pd.DataFrame(result,columns=['번호','reference', 'hypothesis','wer_score','cer_score','rtf','status'])

pp(df)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT,index=False,encoding='utf-8-sig')
pp('파일 저장 ',OUTPUT.resolve())



'''
# day35_challenge.py
# 철도역 안내 자막 품질 게이트

import re
import unicodedata
from pathlib import Path
import pandas as pd
from jiwer import wer, cer, process_words
from util.print_util import pp, up

KEYWORDS = ("승강장", "출발", "변경")

SAMPLES = [
    ("열차 출발 시간은 오전 열 시입니다",
     "열차 출발 시간은 오전 열 시입니다", 2.1, 6.0),
    ("다음 열차는 삼 번 승강장에 도착합니다",
     "다음 열차는 삼 번에 도착합니다", 2.4, 7.0),
    ("열차 출발 장소가 변경되었습니다",
     "열차 장소가 되었습니다", 2.9, 6.0),
    ("안전선 안쪽에서 기다려 주세요",
     "안전선 안쪽에서 기다려 주세요", 1.5, 5.0)
]

# 정규화 함수
def norm(value):
    value = unicodedata.normalize('NFC', value).lower()
    value = re.sub(r'[^가-힣a-z0-9\s]', r' ', value)
    return re.sub(r'\s+', ' ', value).strip()

def main():

    records = []

    for i, (reference, hypothesis, latency, duration) in enumerate(SAMPLES, 1):

        ref_n, hyp_n = norm(reference), norm(hypothesis)

        word_rate, char_rate = wer(ref_n, hyp_n), cer(ref_n, hyp_n)

        rtf = latency / duration

        # 정답에는 있지만 인식에는 없는 키워드 리스트
        missing = [k for k in KEYWORDS if k in ref_n and k not in hyp_n]

        review = bool(missing) or word_rate > 0.2 or rtf > 1.0

        records.append({
            '번호': i,
            '정답': reference,
            '전사': hypothesis,
            'WER': word_rate,
            'CER': char_rate,
            'RTF': rtf,
            '누락키워드': ','.join(missing),
            '판정': '검토 필요' if review else '자동 통과'
        })

    df = pd.DataFrame(records)

    summary = pd.DataFrame([{
        '전체': len(df),
        '검토필요': (df['판정'] == '검토 필요').sum(),
        '평균WER': df['WER'].mean(),
        '평균CER': df['CER'].mean(),
        '평균RTF': df['RTF'].mean()
    }])

    base = Path(__file__).resolve().parent

    df.to_csv(base / 'railway_report.csv', index=False, encoding='utf-8-sig')

    summary.to_csv(base / 'railway_summary.csv', index=False, encoding='utf-8-sig')

    pp(df.to_string(index=False))
    pp(summary.to_string(index=False))
    pp('위험한 자동 안내의 실제 게시에는 반드시 인적 검수가 필요합니다.')

if __name__ == '__main__':
    main()

up(5)



























'''





























































