# day9_application.py
# 주제:
import numpy as np

stores = np.array([
    [120,135,128,142,150],
    [98,105,110,115,120],
    [160,155,172,168,180],
    [130,125,140,138,145]
])
# 4행5열
reshape = stores.reshape(4,5)
print('4행5열 \n', reshape)
print('shape :',stores.shape)  #shape
print('원소개수 :',stores.size) #원소개수

print('매장별 평균 매출',stores.mean(axis=1)) # 매장별 평균 매출
print('요일별 매출 합계',stores.sum(axis=0))  # 요일별 매출 합계

# 평균 매출이 가장 높은 매장
stores_avg = stores.mean(axis=1)
store_name = np.argmax(stores_avg)
if store_name == 0:
    print('매장 A')
elif store_name == 1:
    print('매장 B')
elif store_name == 2:
    print('매장 C')
elif store_name == 3:
    print('매장 D')

# 전체 매출 평균
total_mean = stores.mean()
print('전체 매출 평균',total_mean)

# 전체 평균의 110%
a1 = total_mean * 1.1
print(round((a1),2) )   #round(s,n)  n번째 자리에서 반올림

# 전체 평균 110% 이상인 매출값
a2 = stores[stores >= a1]
print('110% 이상 매출값',a2)


# a2는 이미 구해서 1차원으로 출력했기 때문에 stores >= a1을 사용
raw,colum = np.where(stores >= a1)

print(raw)
print(colum)






















