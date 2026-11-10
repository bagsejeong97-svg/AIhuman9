# day9_challenge.py
# 주제:
import numpy as np

e_product = np.array([
    [3,5,4,6,2,4],
    [6,7,5,8,6,7],
    [2,3,1,4,3,2],
    [4,5,6,5,7,4]
])

e_product = e_product.reshape(4,6)
print('4,6배열 생성\n',e_product)

time_e_p = np.round(e_product.mean(axis=1),2)
print('각 라인의 평균 불량 수',time_e_p)

avg_e_p = e_product.sum(axis=0)
print('각 시간 총 불량 수',avg_e_p)


target = np.array([4,5,3,4])  # 4목표값
target = target[:, np.newaxis] # 5
print('목표값\n',target.shape)   # 튜플로 행열출력

# 6실제 불량 개수 - 라인별 목표값 차이
e_product2 = e_product - target
print('불량 개수 - 라인별 목표값 \n',e_product2)


over_e_product = e_product > target # 7.
print('bool\n',over_e_product)

over_target_count = over_e_product.sum(axis=1)  # 8.  목표 초과 횠수
print('목표 초과 횟수',over_target_count)

max_o_t_c= np.argmax(over_target_count) # 9
print('목표 초과횟수가 가장 많은 라인',max_o_t_c)

# 각 라인 안에서 불량 개수를 0~1 범위로 Min-Max 정규화하세요.
#  공식: (값 - 라인별 최솟값) / (라인별 최댓값 - 라인별 최솟값)

# 정규화 : 어떤 범위의 값들을 지정한 다른 범위의 값들로 치환하는 과정

# Min - Max 정규화
# 원래값에서 최소값을 뺀 값을 최대값에서 최소값 뺀 값으로 나눠서
#모든 값을 0~1의 범위 안에 있도록 재구성
# 원래값 - 최소값 / 최대값 - 최소값

# [:,np.newaxis] 행을 열로 축을 봐꿈 reshape와 같은 원리
e_p_min = e_product.min(axis=1)[:,np.newaxis]  #라인별 최소값
print('라인별 최소값 \n',e_p_min)
e_p_max = e_product.max(axis=1)[:,np.newaxis]  #라인별 최대값
print('라인별 최대값 \n',e_p_max)
# 정규화
a = (e_product - e_p_min) / (e_p_max - e_p_min)
print(np.round(a,2))























