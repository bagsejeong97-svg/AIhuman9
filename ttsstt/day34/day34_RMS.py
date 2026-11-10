# day34_RMS.py
# RMS(Root Mean Square)

'''
1. RMS
- Root Mean Square(제곱 평균 제곱근)의 약어
- 오디오 신호의 진폭을 이용해 전체 신호가 평균적으로 얼마나 큰 진폭을 갖는지를 나타내는 수치
- 녹음 파일의 평균적인 신호 레벨은 파악할때 유용
- 비교)
    진폭(Amplitude) : 특정 순간의 파형의 크기
    피크(Peak) : 파형내의 진폭 중 최대값, 가장 큰 진폭
    데시벨(dB) : 기준값과 비교한 신호 레벨(강도)을 로그로 표현한 값

2. Peak와 RMS의 차이
- Peak는 높지만 RMS가 낮음 : 순간적으로는 큰소리가 발생하지만 평균적인 소리 크기는 크지 않음
- Peak,RMS 둘다 높은 : 평균 소리 크기가 큼

3. RMS 계산 공식
- 각 진폭의 제곱을 모두 더해서 샘플의 수로 나누고 전체를 제곱근
- RMS = sqrt((x1^2  + x2^2 + x3^2...) / N)
- 예) 신호 : [0.5, -0.5, 0.5, -0.5]
-       제곱 : [0.25,0.25,0.25,0.25]
        평균 : 0.25
        제곱근 : sqrt(0.25) = 0.5
        그러므로, RMS = 0.5

- 진폭은 음수일 수 있지만 RMS는 양수
'''


# Numpy로 RMS 계산
import numpy as np
from util.print_util import pp

# 분석할 신호의 샘플값
y = np.array([0.2, -0.4, 0.6, -0.8])

# Peak
peak = np.max(np.abs(y))

# RMS
rms = np.sqrt(np.mean(y**2))

# 최대 기준 진폭을 1.0으로 가정한 디지털 신호 레벨
# -np.inf : 음의 무한대
rms_dbfs = 20 * np.log10(rms) if rms > 0 else -np.inf

pp(f'Peak: {peak:.4f},\nRMS: {rms:.4f},\nRMS Level: {rms_dbfs:.2f} dBFS')

# 실제 WAV 파일의 RMS 계산

import soundfile as sf

y,sr = sf.read('store_audio/store_A.wav')

if y.ndim == 2: # 스테레오 (2채널)
    y = np.mean(y, axis=1) # 모노로 변환

peak = np.max(np.abs(y))
rms = np.sqrt(np.mean(y**2))
rms_dbfs = 20 * np.log10(rms) if rms > 0 else -np.inf

pp(f'Peak: {peak:.4f},\nRMS: {rms:.4f},\nRMS Level: {rms_dbfs:.2f} dBFS,\nSampling Rate: {sr} Hz')
pp(f'Sample count: {len(y):,}')


















































