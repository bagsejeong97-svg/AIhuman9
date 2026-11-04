# day34_challenge.py
# 주제:
# day34_application.py
# 주제:Application: 실제 인터뷰 녹음 표준화와 처리 이력 작성
# 업무 상황
# 실제 인터뷰 음원 3개를 음성 인식(STT) 실험용 12초 길이로 맞추고,
# 처리 과정을 이력 CSV로 기록합니다.

import csv
from pathlib import Path
import numpy as np
import librosa
import soundfile as sf
import matplotlib.pyplot as plt
from util.print_util import pp

# 실제 데이터
# interview_audio/interview_10s.wav: 실제 인터뷰 발췌 10초
# interview_audio/interview_12s.wav: 실제 인터뷰 발췌 12초
# interview_audio/interview_15s.wav: 실제 인터뷰 발췌 15초

ROOT = Path(__file__).resolve().parent

SOURCES = {
    'interview_audio' : ('interview_10s.wav','interview_12s.wav','interview_15s.wav')
}

LOAD = ROOT.parent # 가져올 파일이 있는 상위 폴더
SAVE = ROOT / 'interview_ready' # 저장할 폴더 위치

TARGET_SR = 16_000
TARGET_SEC = 12


# 파일 확인
def find_recordings():
    missing = [] # 없는 파일 이름
    found = [] # 찾은 파일 이름

    for folder, names in SOURCES.items():
        for name in names:
            path = LOAD / folder / name # 가져올 폴더 경로

            if path.is_file():
                found.append(path)
            else:
                missing.append(f'{folder}/{name}')

    if missing:
        pp('파일이 없습니다.')

        for name in missing:
            pp('누락된 파일', name)

        return []

    return found


# 1. 위 세 WAV의 원본 샘플링레이트와 채널 수를 확인하세요.
# y, sr 로드
def load_y_sr(path):
    y, sr = librosa.load(path, sr=None, mono=False)
    return y, sr


# 샘플링 레이트 채널수 리턴 함수
def inspect(name, y, sr):

    if y.size == 0 or sr <= 0 or not np.isfinite(y).all():
        raise ValueError('비어있거나 유효하지 않음')

    return {
        'filename': name,
        'source_sec': round(y.shape[-1] / sr, 3),
        'source_sr': sr,
        'source_channels': 1 if y.ndim == 1 else y.shape[0]
    }


# 스테레오 또는 다채널 파일이면 모노로 변환하세요.
def channel_down(y):
    mono = librosa.to_mono(y) if y.ndim == 2 else y
    return mono


# librosa.resample로 16000 Hz로 리샘플링하세요.
def change_hz(y, sr):
    resampled = librosa.resample(
        y,
        orig_sr=sr,
        target_sr=TARGET_SR
    )

    return resampled


# 10초 음원은 뒤에 무음을 덧붙이고(pad),
# 15초 음원은 앞 12초를 추출(crop)하세요.
# 12초 음원은 길이를 그대로 유지(keep)하세요.
def pad_crop_keep(y):
    target_length = TARGET_SEC * TARGET_SR

    if len(y) < target_length:
        pad_length = target_length - len(y)
        y = np.pad(y, (0, pad_length))
        action = 'pad'

    elif len(y) > target_length:
        y = y[:target_length]
        action = 'crop'

    else:
        action = 'keep'

    return y, action


# interview_manifest.csv 저장
def save_check(rows):
    SAVE.mkdir(exist_ok=True)

    fields = [
        'filename',
        'source_sec',
        'source_sr',
        'source_channels',
        'result_sec',
        'result_sr',
        'action',
        'status'
    ]

    report = SAVE / 'interview_manifest.csv'
    SAVE.mkdir(exist_ok=True)
    with report.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    return report


# 원본 WAV는 변경하지 마세요. 파일이 없으면 누락 목록을 알리세요.
#
# 결과물
# interview_ready/interview_10s.wav
# interview_ready/interview_12s.wav
# interview_ready/interview_15s.wav
# interview_manifest.csv
def main():

    recordings = find_recordings()

    if not recordings:
        return

    rows = []

    for path in recordings:

        try:
            # 원본 읽기
            y, sr = load_y_sr(path)
            # 원본 정보 확인
            info = inspect(path.name, y, sr)
            # 모노 변환
            mono = channel_down(y)
            # 16000 Hz 변환
            resampled = change_hz(mono, sr)
            # 12초로 맞추기
            prepared, action = pad_crop_keep(resampled)
            # 처리된 WAV 저장
            sf.write(
                SAVE / path.name,
                prepared,
                TARGET_SR,
                subtype='PCM_16'
            )

            # 처리 결과 기록
            info['result_sec'] = round(len(prepared) / TARGET_SR, 3)
            info['result_sr'] = TARGET_SR
            info['action'] = action
            info['status'] = 'ok'

            rows.append(info)

            pp(
                info['filename'],
                f"원본 길이: {info['source_sec']}초",
                f"원본 SR: {info['source_sr']}Hz",
                f"원본 채널: {info['source_channels']}",
                f"결과 길이: {info['result_sec']}초",
                f"결과 SR: {info['result_sr']}Hz",
                f"작업: {info['action']}",
                f"상태: {info['status']}"
            )

        except Exception as e:
            pp(path.name, '처리 실패:', str(e))

            rows.append({
                'filename': path.name,
                'source_sec': '',
                'source_sr': '',
                'source_channels': '',
                'result_sec': '',
                'result_sr': '',
                'action': '',
                'status': 'error'
            })

    report = save_check(rows)

    pp(f'CSV 저장 위치: {report}')

if __name__ == '__main__':
    main()
