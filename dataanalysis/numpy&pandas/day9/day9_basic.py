# day9_basic.py
# 주제:

import numpy as np

late_time = np.array([12,8,15,6,20,9,11,7])
print(late_time)   # 1차원 배열 생성

# 배열 속성 각각 출력
print('shape :',late_time.shape)  #형태
print('ndim :',late_time.ndim)   # 차원 의 수
print('size :',late_time.size)   # 요소의 수
print('dtype :',late_time.dtype)   # 데이터 타입

# -2분씩
print('2분 감소',late_time -2)

avg = late_time.mean()

result = late_time > avg
print(late_time[result])

# 요구 값 출력
print('합계: ',late_time.sum())  #np.sum(late_time)
print('평균: ',avg)
print('최소값: ',late_time.min())
print('최대값: ',late_time.max())

up_late_time = late_time -2
print('개선후 평균 대기시간 :',up_late_time.mean())

