# day35_application.py
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
OUTPUT = BASE / "results" / 'day35_application_result.csv'


SAMPLES = [
    ("진료 예약은 일 층 접수처에서 확인하세요",
     "진료 예약은 일 층 접수처에서 확인하세요",
     "진료 예약은 접수처에서 확인하세요", 7.0, 2.0, 3.0),
    ("응급실 방문자는 안내 직원에게 문의하세요",
     "응급실 방문자는 안내 직원에게 문의하세요",
     "응급실 방문자는 안내 직원에게 문의", 6.0, 1.8, 2.8),
    ("검사 결과는 담당 의료진에게 확인하세요",
     "검사 결과는 담당 의료진에게 확인하세요",
     "검사 결과는 의료진에게 확인하세요", 6.5, 1.7, 2.7)]
# rtf = 추론길이/녹음길이
results = []

for ref,hyp_a,hyp_b,s1,s2,s3 in SAMPLES:
    # 모델 a
    wer_a = wer(ref, hyp_a)
    cer_a = cer(ref, hyp_a)
    # 모델 b
    wer_b = wer(ref, hyp_b)
    cer_b = cer(ref, hyp_b)
    # rtf a
    rtf_a = s2/s1
    # rtf b
    rtf_b = s3/s1

    results.append([
        wer_a,wer_b,cer_a,cer_b,rtf_a,rtf_b

    ])

feature = [
    'wer_a','wer_b','cer_a','cer_b','rtf_a','rtf_b'
           ]

# 모델별 평균 표
df = pd.DataFrame(results, columns = feature)
pp(df)

df = df.mean(axis=0).to_frame().T
pp(df)


OUTPUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT, index=False)
pp('파일 저장 ',OUTPUT.resolve())




'''
# day35_application.py
# 병원 안내 자동 자막 모델 비교

import re
import unicodedata
from pathlib import Path
import pandas as pd
from jiwer import wer, cer, process_words
from util.print_util import pp, up

SAMPLES = [
    ("진료 예약은 일 층 접수처에서 확인하세요",
     "진료 예약은 일 층 접수처에서 확인하세요",
     "진료 예약은 접수처에서 확인하세요", 7.0, 2.0, 3.0),
    ("응급실 방문자는 안내 직원에게 문의하세요",
     "응급실 방문자는 안내 직원에게 문의하세요",
     "응급실 방문자는 안내 직원에게 문의", 6.0, 1.8, 2.8),
    ("검사 결과는 담당 의료진에게 확인하세요",
     "검사 결과는 담당 의료진에게 확인하세요",
     "검사 결과는 의료진에게 확인하세요", 6.5, 1.7, 2.7)
]

# 정규화 함수
def norm(value):
    value = unicodedata.normalize('NFC', value).lower()
    value = re.sub(r'[^가-힣a-z0-9\s]', r' ', value)
    return re.sub(r'\s+', ' ', value).strip()

def main():

    rows = []

    for i, (ref, a, b, duration, time_a, time_b) \
            in enumerate(SAMPLES, 1):

        for model, hyp, latency in [('A', a, time_a), ('B', b, time_b)]:

            ref_n, hyp_n = norm(ref), norm(hyp)

            rows.append({
                '문장': i,
                '모델': model,
                'WER': wer(ref_n, hyp_n),
                'CER': cer(ref_n, hyp_n),
                'RTF': latency / duration
            })

    df = pd.DataFrame(rows)

    summary = df.groupby('모델', as_index=False)[['WER', 'CER', 'RTF']].mean()

    target = Path(__file__).resolve().parent / 'hospital_stt_summary.csv'

    summary.to_csv(target, index=False, encoding='utf-8-sig')

    pp(df.to_string(index=False))
    pp(summary.to_string(index=False))
    pp('의료 상황에서는 낮은 오류율만으로 안전성을 보장할 수 없습니다.')
    pp('개선: 핵심 용어 인적 검수, 불확실한 전사 표시 후 재확인')
    pp(f'저장: {target}')

if __name__ == '__main__':
    main()

up(5)























'''
































