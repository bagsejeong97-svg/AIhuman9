# day34_basic.py

import csv
from pathlib import Path
import numpy as np
import soundfile as sf
from util.print_util import pp, up

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "store_audio"
FILES = ('store_A.wav', 'store_B.wav', 'store_C.wav')
REPORT = ROOT / "store_audio_check.csv"

LOW_PEAK = 0.03 # 실습용 로우 피크

# 녹음 파일을 읽어서 길이, 채널, 피크, RMS를 반환하는 함수
def inspect_audio(path):

    # always_2d=True: 모노도 (샘플 수, 1채널) 형태로 반환
    audio, sr = sf.read(path, dtype='float32', always_2d=True)

    if audio.size == 0 or not np.isfinite(audio).all():
        raise ValueError("빈 파일이거나 유효하지 않은 샘플이 있습니다")

    peak = float(np.max(np.abs(audio))) # 절대 진폭값 중 가장 큰 값

    rms = float(np.sqrt(np.mean(audio ** 2))) # 전체 평균 음량 지표

    status = 'recheck' if peak < LOW_PEAK else "ok"

    return {
        'filename': path.name,
        'duration_sec': round(len(audio)/sr, 2),
        'sample_rate': sr,
        'channels': audio.shape[1],
        'peak': round(peak, 5),
        'rms': round(rms, 5),
        'status': status
    }

def main():

    missing = [name for name in FILES if not (INPUT / name).is_file()]

    if missing:
        pp('실제 녹음 파일이 없습니다')
        pp('누락: ', ', '.join(missing))
        return

    rows = []

    for name in FILES:
        path = INPUT / name
        try:
            rows.append(inspect_audio(path))
        except (OSError, RuntimeError, ValueError) as e:
            rows.append({
                'filename': name,
                'duration_sec': '',
                'sample_rate': '',
                'channels': '',
                'peak': '',
                'rms': '',
                'status': f'error: {e}'
            })

    fields = ['filename', 'duration_sec', 'sample_rate', 'channels', 'peak', 'rms', 'status']

    with REPORT.open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    pp('실제 현장 녹음 품질 점검')
    for row in rows:
        pp(row)

    pp(f'보고서 저장: {REPORT}')

if __name__ == '__main__':
    main()

up(5)











































