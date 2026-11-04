# day36_ex1.py
# 한국어 TTS 합성 및 청취 품질 평가

# Alt + F12 > pip install edge-tts, mutagen

import asyncio # 비동기 IO
import csv
import time
from pathlib import Path
import edge_tts # 온라인 TTS 모델
import pandas as pd
from mutagen import File as AudioFile # 파일의 메타데이터
from util.print_util import pp, up

# 출력 파일 경로
OUT = Path(__file__).resolve().parent / 'outputs'

# edge-tts에서 제공하는 voice id
VOICE = 'ko-KR-SunHiNeural'
ALT_VOICE = 'ko-KR-InJoonNeural'

# TTS에 사용할 문장들
SAMPLES = [
    ' 나는 신의진이라 합니다. 서울에서 주먹으로 이름좀 날리다가 과거 청산하고 제대로 살아볼려고 합니다 건들지 마이소',
    '나란남자 신의진 전국을 돌다보니 적수를 만나지못했다 그렇다면 감빵에가면 내 적수가 있을까 감빵들어갈줄 아는 사람들은 신속하게 공유해주길 바란다!',
    '오늘 밤 11시 나 신의진 시내에 나타난다 전국에 진돗개 선포해라 다 디졌다.',
    '다음날이 됬다 나 신의진 처음으로 두들겨 맞았다 아프다 울면서 집가는데 서러웠다 엄마가 된장찌개를 끓여줬다 기분이 나빠서 엎어버렸다.'
]

# 문장을 지정한 음색 / 속도 / 피치로 MP3에 저장하는 함수
async def synthesize(text, filename, voice=VOICE, rate='+0%', pitch='+0%'):

    target = OUT / filename

    # 음성 합성 객체
    tts = edge_tts.Communicate(text, voice=voice, rate=rate, pitch=pitch)

    start = time.perf_counter() # 시작 시간
    await tts.save(str(target)) # 합성 결과를 MP3 저장
    end = time.perf_counter()  # 종료 시간
    elapsed = end - start # 소요 시간

    audio = AudioFile(str(target)) # MP3를 읽어서 메타데이터 조회

    # audio가 없거나 info라는 속성이 없다면
    if audio is None or not hasattr(audio, 'info'):
        raise ValueError(f'오디오 메타데이터 분석 실패: {target}')

    seconds = round(audio.info.length, 3) # 음성 재생 길이 (초)

    return {
        'file': filename, # 파일명
        'text': text, # 변환할 텍스트
        'voice': voice, # voice id
        'rate': rate, # 속도
        'pitch': pitch, # 높낮이
        'duration_sec': seconds, # 재생 시간
        'size_bytes': target.stat().st_size, # 파일의 바이트 수
        'elapsed_sec': round(elapsed, 3), # 처리 소요시간
        'rtf': round(elapsed / seconds, 3) if seconds else None # RTF
    }

async def main():

    OUT.mkdir(parents=True, exist_ok=True)

    cases = [
        (f'tts_{i:02}.mp3', text, VOICE, '+0%', '+0Hz')
        for i, text in enumerate(SAMPLES, start=1)
    ]

    base = '마 몰 째리보노 마내 신!의!진 이다이 드가라.'

    cases += [
        ('cmp_base.mp3', base, VOICE, '+0%', '+0Hz'), # 기본
        ('cmp_punct.mp3', '분석 결과를 확인하세요!', VOICE, '+0%', '+0Hz'), # text 교체
        ('cmp_slow.mp3', base, VOICE, '-20%', '+0Hz'), # 속도 -20% 감소
        ('cmp_fast.mp3', base, VOICE, '+20%', '+0Hz'), # 속도 +20% 증가
        ('cmp_pitch.mp3', base, VOICE, '+0%', '+20Hz'), # 피치 +20Hz 증가
        ('cmp_voice.mp3', base, ALT_VOICE, '+0%', '+0Hz') # voice id 교체
    ]

    rows = []

    for filename, text, voice, rate, pitch in cases:
        try:
            row = await synthesize(text, filename, voice, rate, pitch)
            rows.append(row)
            pp(f'완료: {filename} / {row['duration_sec']}초')
        except Exception as e:
            pp(f'실패: {filename}: {type(e).__name__}: {e}')

    # 빈 설문 CSV : 평가자가 실제 음성을 듣고 점수를 기입함
    with (OUT / 'listening_scores.csv') \
        .open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['clip_id', 'evaluator', 'clarity', 'naturalness', 'comment'])
        for row in rows:
            writer.writerow([row['file'], '', '', '', ''])

    pp('생성 완료: tts_metadata.csv, listening_scores.csv')
    pp('평가표를 작성한 뒤 day36_ex2.py를 실행하세요.')

if __name__ == '__main__':
    asyncio.run(main())
up(5)



























