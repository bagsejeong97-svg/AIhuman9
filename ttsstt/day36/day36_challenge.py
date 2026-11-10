
# day36_challenge.py

import asyncio
import csv
from pathlib import Path
import edge_tts
import pandas as pd
from mutagen import File as AudioFile
from util.print_util import pp, up

OUT = Path(__file__).resolve().parent / 'museum_output'

TEXTS = {
    "ko": (
        "우리 박물관의 역사 전시관에 오신 것을 환영합니다.",
        ["ko-KR-SunHiNeural", "ko-KR-InJoonNeural"]
    ),
    "en": (
        "Welcome to the history gallery of our museum.",
        ["en-US-AriaNeural", "en-US-GuyNeural"]
    )
}

PITCHES = ['+0Hz', '+20Hz']

async def main():

    OUT.mkdir(parents=True, exist_ok=True)

    manifest = []

    for lang, (text, voices) in TEXTS.items():

        for voice_num, voice in enumerate(voices, start=1):

            for pitch_num, pitch in enumerate(PITCHES, start=1):

                name = f'museum_{lang}_{voice_num}_{pitch_num}.mp3'
                path = OUT / name

                tts = edge_tts.Communicate(text, voice, pitch=pitch)

                try:

                    await tts.save(str(path))

                    seconds = AudioFile(str(path)).info.length

                    manifest.append({
                        'clip_id': name,
                        'language': lang,
                        'voice': voice,
                        'pitch': pitch,
                        'seconds': round(seconds, 2)
                    })

                    pp(f'완료: {name}')

                except Exception as e:
                    pp(f'실패: {name}: {e}')

    pd.DataFrame(manifest).to_csv(
        OUT / 'museum_manifest.csv',
        index=False,
        encoding='utf-8-sig'
    )

    scores = OUT / 'museum_scores.csv'

    if not scores.exists():
        with scores.open('w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['clip_id', 'evaluator', 'clarity', 'naturalness'])
            for row in manifest:
                writer.writerow([row['clip_id'], '', '', ''])

    data = pd.read_csv(scores)

    for col in ['clarity', 'naturalness']:
        data[col] = pd.to_numeric(data[col], errors='coerce')

    valid = data.dropna(subset=['evaluator', 'clarity', 'naturalness'])
    valid = valid[
        valid['clarity'].between(1, 5)
        & valid['naturalness'].between(1, 5)
    ]

    if valid.empty:
        pp('음성 파일을 듣고 점수를 채운 뒤 재실행해 평균을 계산하세요.')
        return

    result = valid.groupby('clip_id', as_index=False).agg(
        responses = ('evaluator', 'count'),
        clarity = ('clarity', 'mean'),
        naturalness = ('naturalness', 'mean')
    )

    result.to_csv(OUT / 'museum_summary.csv', index=False, encoding='utf-8-sig')

    pp(result.round(2).to_string(index=False))

if __name__ == '__main__':
    asyncio.run(main())

up(5)
































































































