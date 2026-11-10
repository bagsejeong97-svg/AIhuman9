# day34_application.py

import csv
from pathlib import Path
import numpy as np
import librosa
import soundfile as sf
from util.print_util import pp, up

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "interview_audio"
OUTPUT = ROOT / 'interview_ready'
FILES = ('interview_10s.wav', 'interview_12s.wav', 'interview_15s.wav', 'interview_30s.wav')
REPORT = ROOT / "interview_manifest.csv"

TARGET_SR = 16000
TARGET_SEC = 12

# 채널 평균 > 리샘플링 > 고정 길이 맞춤 함수
def standardize(audio, original_sr):

    mono = audio.mean(axis=1) # 여러 채널을 평균하여 모노로 변환

    # 샘플링레이트 변환
    converted = librosa.resample(mono, orig_sr=original_sr, target_sr=TARGET_SR)

    target_count = TARGET_SR * TARGET_SEC

    if len(converted) < target_count:
        converted = np.pad(converted, (0, target_count - len(converted)))
        action = 'pad' # 덧붙임
    elif len(converted) > target_count:
        converted = converted[:target_count] # 앞에서 12초 발췌
        action = 'crop' # 잘라냄
    else:
        action = 'keep' # 유지

    return converted, action

def main():

    missing = [name for name in FILES if not (INPUT / name).is_file()]

    if missing:
        pp('실제 녹음 파일이 없습니다')
        pp('누락: ', ', '.join(missing))
        return

    OUTPUT.mkdir(exist_ok=True)

    rows = []

    for name in FILES:
        path = INPUT / name
        try:

            audio, sr = sf.read(path, dtype=np.float32, always_2d=True)
            if audio.size == 0 or not np.isfinite(audio).all():
                raise ValueError('빈 파일 또는 잘못된 샘플')

            seconds = len(audio) / sr

            converted, action = standardize(audio, sr)

            dest = OUTPUT / name

            sf.write(dest, converted, TARGET_SR, subtype='PCM_16')

            rows.append({
                'filename': name,
                'original_sec': round(seconds, 2),
                'original_sr': sr,
                'channels': audio.shape[1],
                'final_sec': round(len(converted) / TARGET_SR, 2),
                'final_sr': TARGET_SR,
                'action': action,
                'status': 'ok'
            })

        except (OSError, RuntimeError, ValueError) as e:
            rows.append({
                'filename': name,
                'original_sec': '',
                'original_sr': '',
                'channels': '',
                'final_sec': '',
                'final_sr': '',
                'action': '',
                'status': f'error: {e}'
            })

    fields = ['filename', 'original_sec', 'original_sr', 'channels', \
              'final_sec', 'final_sr', 'action', 'status']

    with REPORT.open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    pp('실제 인터뷰 녹음 표준화 결과')
    for row in rows:
        pp(row)

    pp(f'manifest 저장: {REPORT}')

if __name__ == '__main__':
    main()

up(5)

























