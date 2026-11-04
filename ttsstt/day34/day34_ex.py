# day34_ex.py
# 실제 매장 현장음, 인터뷰 WAV를 표준화하고 품질 점검표 작성

# 처리 순서 : 원본 확인 > 모노 변환 > 16kHz 샘플링레이트 변환
#            > 양끝 무음 정리 > WAV / 파형이미지 / CSV 저장
# 입력 : store_audio/*.wav, interview_audio/*.wav
# 출력 : output_audio/, reports/

import csv
from csv import DictWriter
from pathlib import Path
import numpy as np
import librosa
import soundfile as sf
import matplotlib.pyplot as plt
from util.print_util import pp, up

# 현재 파일을 포함하는 디렉토리 경로
ROOT = Path(__file__).resolve().parent

# 실제 녹음 파일이 들어 있는 하위 폴더와 파일명
SOURCES = {
    'store_audio': ('store_A.wav', 'store_B.wav', 'store_C.wav'),
    'interview_audio': ('interview_10s.wav', 'interview_12s.wav', 'interview_15s.wav', 'interview_30s.wav')
}

OUTPUT = ROOT / 'output_audio' # 처리된 WAV 저장 폴더
REPORT = ROOT / 'reports' # 검수 CSV와 파형 PNG 저장 폴더

TARGET_SR = 16000 # 출력 샘플링레이트

# WAV 파일 존재 여부 확인 함수
def find_recordings():

    missing = [] # 준비되지 않은 파일의 상대 경로 저장 리스트
    found = [] # 존재하는 WAV의 (그룹명, 전체 경로) 튜플 저장 리스트

    for folder, names in SOURCES.items():
        for name in names:
            path = ROOT / folder / name
            if path.is_file():
                found.append((folder, path))
            else:
                missing.append(f'{folder}/{name}')

    if missing:
        pp('실제 녹음 파일이 준비되지 않았습니다.')
        for name in missing:
            pp('누락된 파일: ', name)
        return []

    return found

# 원본 음성의 재생 시간, 채널 개수, 최대 절대 진폭을 계산하는 함수
def inspect(y, sr):

    # 전체 샘플 원소수가 0이거나 샘플링레이트가 0이거나 무한한지 확인
    if y.size == 0 or sr <= 0 or not np.isfinite(y).all():
        raise ValueError('비어 있거나 유효하지 않은 음성 데이터입니다.')

    return {
        'duration': round(y.shape[-1] / sr, 3), # 재생 시간 (초)
        'channels': 1 if y.ndim == 1 else y.shape[0], # 채널 수
        'peak': round(float(np.max(np.abs(y))), 5) # 최대 절대 진폭
    }

# 음성 파일을 모노, 16kHz로 표준화하고 양끝 무음 구간을 정리하는 함수
def prepare(y, sr):

    # 채널별 파형을 결합해서 단일 채널로 변환
    mono = librosa.to_mono(y) if y.ndim == 2 else y

    # 리샘플링 : 샘플링레이트 변환
    resampled = librosa.resample(
        mono, # 채널
        orig_sr=sr, # 원본 샘플링레이트
        target_sr=TARGET_SR # 변환 샘플링레이트
    )

    # 리샘플링한 결과 크기가 0이거나 최대 절대 진폭값이 1/1000000보다 작다면
    if resampled.size == 0 or np.max(np.abs(resampled)) < 1e-6:
        raise ValueError('무음 파일: 직접 청취 후 재녹음 여부 검토 필요')

    # 앞뒤 무음공간 제거
    # trimmed : 무음공간 제거된 샘플배열
    # interval : 유지한 구간의 샘플 인덱스
    trimmed, interval = librosa.effects.trim(
        resampled, # 리샘플링된 샘플배열
        top_db=25 # 기준 에너지보다 약 25dB 이상 작은 프레임을 구분
    )

    if not trimmed.size:
        raise ValueError('처리 가능한 음성 구간을 찾지 못함')

    return trimmed, interval

# 원본과 전처리본 파형을 비교하는 PNG 이미지를 저장하는 함수
# src:원본 샘플, sr:원본 샘플링레이트, dst:표준화한 샘플,
# group:데이터폴더명, stem:확장자제외파일명
def draw_comparison(src, sr, dst, group, stem):

    # 비교 그래프에서 원본 채널을 하나로 합침
    if src.ndim == 2:
        src = librosa.to_mono(src)

    # 2행 1열, 가로 10인치, 세로 5인치
    fig, axes = plt.subplots(2, 1, figsize=(10, 6))

    for ax, y, rate, title in (
        (axes[0], src, sr, 'Original recoding'),
        (axes[1], dst, TARGET_SR, 'Prepared WAV')
    ):
        x = np.arange(len(y)) / rate # 시간 (초)

        ax.plot(x, y, linewidth=0.6)
        ax.set_title(title)
        ax.set_xlabel('Time (Seconds)')
        ax.set_ylabel('Amplitude')
        ax.set_ylim(-1.05, 1.05) # 진폭의 범위

    fig.tight_layout()
    dest = REPORT / group # 그룹별 그래프 폴더
    dest.mkdir(exist_ok=True)
    fig.savefig(dest / f'{stem}_comparison.png', dpi=120)
    plt.close(fig)

# WAV 1개를 처리하고 CSV 보고서에 들어갈 딕셔너리를 반환하는 함수
def process_file(group, path):

    # CSV 저장할 행 딕셔너리
    row = {
        'group': group,
        'filename': path.name,
        'status': 'review',
        'note': ''
    }

    try:

        # WAV 파일을 (샘플배열, 샘플링레이트)로 읽음
        # sr=None: 원본 샘플링레이트를 유지
        # mono=False: 스테레오를 모노로 변환하지 않고 유지
        y, sr = librosa.load(path, sr=None, mono=False)

        # 원본 길이, 채널 수, 피크
        info = inspect(y, sr)

        row.update({
            'source_sec': info['duration'],
            'source_sr': sr,
            'channels': info['channels'],
            'source_peak': info['peak']
        })

        # 모노, 리샘플링, 무음 제거
        prepared, interval = prepare(y, sr)

        # 모노, 리샘플링, 무음 제거
        prepared, interval = prepare(y, sr)

        # store_audio 파일에만 진폭 4배 적용
        if group == 'store_audio':
            prepared = prepared * 4.0
            # 진폭이 -1.0 ~ 1.0 범위를 벗어나지 않도록 제한
            prepared = np.clip(prepared, -1.0, 1.0)

        # 전처리 후 최대 절대 진폭
        peak = float(np.max(np.abs(prepared)))
        # 전처리 후 최대 절대 진폭
        peak = float(np.max(np.abs(prepared)))

        row['prepared_sec'] = round(len(prepared) / TARGET_SR, 3)
        row['target_sr'] = TARGET_SR
        row['prepared_peak'] = round(peak, 5)
        row['status'] = 'review' if peak < 0.02 else 'ok'
        row['note'] = (
            '음량 낮음: 직접 청취 권장' if peak < 0.02
            else '자동 검사 통과 (청취 검수는 별도로 필요함)'
        )

        # 전처리한 WAV 저장 폴더
        dest = OUTPUT / group
        dest.mkdir(exist_ok=True)

        # 전처리한 WAV 파일 저장
        # PCM_16 : 일반적인 16비트 비압축 PCM WAV 인코딩
        sf.write(dest / path.name, prepared, TARGET_SR, subtype='PCM_16')

        # 비교그래프
        draw_comparison(y, sr, prepared, group, path.stem)

    except Exception as e:
        row['status'] = 'error'
        row['note'] = str(e)

    return row

def main():

    # 실제 녹음 파일 존재 검사
    recordings = find_recordings()
    if not recordings:
        return

    OUTPUT.mkdir(exist_ok=True)
    REPORT.mkdir(exist_ok=True)

    # 각 파일 처리 결과를 CSV 행 목록으로 수집
    rows = [process_file(group, path) for group, path in recordings]

    # CSV 출력용 컬럼명들
    fields = [
        'group', 'filename', 'status', 'source_sec', 'prepared_sec',
        'source_sr', 'target_sr', 'channels', 'source_peak', 'prepared_peak', 'note'
    ]

    # CSV 레포트 파일 경로
    report = REPORT / 'audio_quality_report.csv'

    # CSV 파일 저장
    with report.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    pp('실제 녹음 파일 전처리 및 검수 결과')
    for row in rows:
        pp(row['group'], row['filename'], row['status'], row['note'])

    pp(f'CSV 보고서: {report}')

if __name__ == '__main__':
    main()

up(5)














































































