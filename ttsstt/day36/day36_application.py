# day36_application.py
# 주제:
import asyncio  # 비동기 IO
import csv
import time
from pathlib import Path
import edge_tts  # 온라인 TTS 모델
import pandas as pd
from mutagen import File as AudioFile  # 파일의 메타데이터
from util.print_util import pp, up

MESSAGES = [
    "이번 역은 시청역입니다. 이호선으로 갈아타실 수 있습니다. ",
    "열차에서 내리실 때 발 빠짐에 주의해 주세요.",
]

OUT = Path(__file__).resolve().parent / 'appl_output'
VOICE = 'ko-KR-SunHiNeural'


async def generate_tts(text, filename, rate='+0%', pitch='+0Hz', voice=VOICE):
    # 1. 출력 디렉토리 생성

    target = OUT / filename

    # 2. TTS 음성 합성 및 저장
    tts = edge_tts.Communicate(text, voice=voice, rate=rate, pitch=pitch)
    start = time.perf_counter()
    await tts.save(str(target))  # 합성 결과를 MP3 저장
    end = time.perf_counter()  # 종료 시간
    elapsed = end - start #처리시간

    audio = AudioFile(str(target))
    if audio is None or not hasattr(audio, 'info'):
        raise ValueError(f'오디오 메타데이터 분석 실패: {target}')

    seconds = round(audio.info.length, 3) # 길이

    rtf = elapsed / seconds

    return [filename,seconds,elapsed,rtf]

async def main():
    OUT.mkdir(parents=True, exist_ok=True)

    cases = []

    for i, text in enumerate(MESSAGES, start=1):
        cases.append((f'app_slow_{i:02}.mp3', text, VOICE, '-15%', '+0Hz'))
        cases.append((f'app_base_{i:02}.mp3', text, VOICE, '+0%', '+0Hz'))
        cases.append((f'app_fast_{i:02}.mp3', text, VOICE, '+20%', '+0Hz'))

    results = []

    # 2. cases를 순회하며 synthesize(generate_tts) 실행 및 결과 수집
    for filename, text, voice, rate, pitch in cases:
        # generate_tts 호출 후 리턴값(info) 받기
        info = await generate_tts(text, filename, rate=rate, pitch=pitch, voice=voice)
        results.append(info)

    # 3. 수집된 결과들을 CSV 파일로 저장
    csv_path = OUT / 'subway_audio_metrics.csv'
    with csv_path.open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)

        # 컬럼 헤더 작성
        writer.writerow(['filename', 'duration_sec', 'elapsed_sec', 'rtf'])

        # 데이터 행들 작성
        writer.writerows(results)

    pp(f'모든 작업 완료! CSV 저장 위치: {csv_path}')
if __name__ == '__main__':
    asyncio.run(main())
    pp('저장완료')












































































