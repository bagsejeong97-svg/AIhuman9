# day36_basic.py
# 주제: 도서관 안내 멘트 제작 및 MP3 저장, 메타데이터 CSV 정리

import asyncio  # 비동기 IO
import csv
import time
from pathlib import Path
import edge_tts  # 온라인 TTS 모델
import pandas as pd
from mutagen import File as AudioFile  # 파일의 메타데이터
from util.print_util import pp, up

MESSAGES = [
    "도서관은 오전 아홉 시부터 오후 여섯 시까지 운영합니다.",
    "열람실에서는 휴대전화를 진동으로 설정해 주세요.",
    "대출 도서는 반납함을 이용해 돌려주실 수 있습니다.",
]

OUT = Path(__file__).resolve().parent / 'basic_output'
VOICE = 'ko-KR-SunHiNeural'


async def generate_tts(text, filename, rate='+0%', pitch='+0Hz', voice=VOICE):
    # 1. 출력 디렉토리 생성

    target = OUT / filename

    # 2. TTS 음성 합성 및 저장
    tts = edge_tts.Communicate(text, voice=voice, rate=rate, pitch=pitch)
    await tts.save(str(target))  # 합성 결과를 MP3 저장

    # 3. 오디오 메타데이터 분석 (길이, 용량)
    audio = AudioFile(str(target))
    if audio is None or not hasattr(audio, 'info'):
        raise ValueError(f'오디오 메타데이터 분석 실패: {target}')

    seconds = round(audio.info.length, 3)  # 음성 재생 길이 (초)
    size_bytes = target.stat().st_size  # 파일의 바이트 수

    return [filename,seconds,size_bytes]



async def main():
    OUT.mkdir(parents=True, exist_ok=True)


    results = [

    ]
    for i,text in enumerate(MESSAGES, start=1):
        filename = f'LIBRARY_0{i}.mp3'
        info = await generate_tts(text, filename)
        results.append(info)

    with (OUT / 'library.csv').open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['filename', 'duration_sec', 'size_bytes'])
        writer.writerows(results)





if __name__ == '__main__':
    asyncio.run(main())
    pp('저장완료')