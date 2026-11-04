# day9_ex.py
# 주제: NumPy 배열 , 수치연산

import numpy as np

# 1. python 리스트와 numpy&pandas 배열

# 파이썬 리스트 연산
python_scores = [70,85,90,95]
python_result = []   #결과를 저장할 리스트
for score in python_scores:
    python_result.append(score + 5)
print('python 리스트 계산:', python_result)

# numpy&pandas 배열 벡터 연산
numpy_scores = np.array([70,85,90,95]) #ndarray 생성
print('numpy&pandas 벡터 연산:', numpy_scores + 5)
print('배열 객체 타입: ', type(numpy_scores)) #<class 'numpy&pandas.ndarray'>

# 2. 여러방식으로 배열 생성

# 1차원 배열 생성
arr1 = np.array([10,20,30,40,50])
print(arr1)

# 0부터 10 미만까지 2씩 증가하는 배열 생성
arr2 = np.arange(0,10,2)
print(arr2)

# 0부터 1까지를 5개의 동일한 간격으로 분할한 배열 생성
arr3 = np.linspace(0,1,5)
print(arr3)

# 2행 3열을 모두 0.으로 채운 배열 생성
zeros = np.zeros((2,3))
print(zeros)

# 2행 3열을 모두 1으로 채운 배열 생성
ones = np.ones((2,3))
print(ones)

# 2행 3열을 모두 지정한 수로으로 채운 배열 생성
full = np.full((2,3),7)
print(full)

# 3. shape, ndim, size, dtype 확인
students_scores = np.array([
    [80,90,85],
    [70,75,95]
])
print('shape:', students_scores.shape)   # (2,3) 모양
print('ndim:', students_scores.ndim)     # 2, 차원수
print('size:', students_scores.size)     # 6, 전체 요소 수
print('dtype:', students_scores.dtype)  # int64, 요소데이터 타입

# 4. dtype 지정, 자료형 변환
flast_scores = np.array([70,85,90], dtype = np.float64)
print(flast_scores)   # [70. 85. 90.]   .이 붙으면 실수
print(flast_scores.dtype)  #float64

int_scores = flast_scores.astype(np.int32)  # 4바이트 정수로 변환
print(int_scores)       #[70 85 90]
print(int_scores.dtype)  # int32

# 5. numpy&pandas 주요 상수
print('np.pi:', np.pi)
print('np.e:', np.e)
print('np.inf:', np.inf)
print('np.nan:', np.nan)

#nan 비교 np.innan() 함수 사용
print(np.nan == np.nan)   # false
print(np.isnan(np.nan)) # True

# 6. 1차원 배열 인덱싱과 슬라이싱
values = np.array([10,20,30,40,50,60])
print('첫번째 요소: ',values[0])
print('마지막 요소: ',values[-1])
print('values[1:4]: ',values[1:4])
print('values[:3]: ',values[0:3])
print('values[::2]: ',values[::2])

# 7. 2차원 배열 인덱싱과 슬라이싱
matrix = np.array([
    [11,12,13,14],
    [21,22,23,24],
    [31,32,33,34],
])
print('matrix[1,2]: ',matrix[1,2]) # 23
print('두번째 행: ',matrix[1])  #[21 22 23 24]
print('세번째 열: ',matrix[:,2]) #
print('[matrix[0:2,1:3] ',matrix[0:2,1:3]) #


# 8. 조건 인덱싱
exam_scores = np.array([55,70,82,91,68,88,76,95])
condition = exam_scores >= 80
print(condition)
print('80 이상 : ',exam_scores[condition])

# 70이상 90 미만 조건 인덱싱
mid_scores =exam_scores[(exam_scores >= 70) & (exam_scores <= 90)]
print(mid_scores)

# 90이상인 요소의 인덱스
high_indices = np.where(exam_scores >= 90)[0]
print(high_indices)

# 9. 벡터 연산(Vectorized Operation)
base = np.array([10,20,30,40])
print('+5',base+5)
print('-3',base-3)
print('*2',base*2)
print('/10',base/10)
print('**2',base**2)

a = np.array([1,2,3])
b = np.array([10,20,30])
c = np.array([2,3])
print('a+b',a+b)
print('a*b',a*b)
print('a-b',a-b)

# print('a+c',a+c)   #ValueError , 요소 수가 다르면 연산 불가

# 10. 집계 함수와 axis
# 집계 함수 (aggregation  function): 여러 데이터로 하나의 결과를 내는 함수
scores = np.array([
    [78,85,92],
    [88,90,76],
    [95,82,89],
    [67,74,80],
])
print('전체 합계:',scores.sum())
print('전체 평균:',scores.mean())
print('전체 최대값:',scores.max())
print('전체 최소값:',scores.min())
print('과목별 평균:',scores.mean(axis=0))

students_avg = scores.mean(axis=1)
print('학생별 평균:',students_avg)


# 평균이 85 이상인 학생의 인덱스
excellent_students = np.where(students_avg >= 85)[0]
print(excellent_students)

#11. reshape(), faltten()

sequence = np.arange(1, 13) # [1 2 3 ... 12]
print(sequence)

reshape = sequence.reshape(3,4) # 3행 4열로 모양 변경
print(reshape)

auto_reshape = sequence.reshape(2,-1) # 열의 개수를 자동 계산
print(auto_reshape) #
flatten = sequence.flatten()  # 평탄화 2차원 배열을 1차원배열로 변경
print(flatten)

#전치 : 행과 열을 뒤바꿈
print('전치 결과:',reshape.T)

# 12. 브로드캐스팅 (broadcasting)
# 배열간 연산에서 모양이 다른 경우 연산을 위해서 내부적으로 모양을 변경하여
# 연산을 수행

# 아래 점수 보정 연산에서 2차원 배열에 1차원 배열 연산을 하기 위해서
# 내부적으로 1차원 배열을 2차원 배열로 맞춘 후 연산

# 2차원 배열 , 원래 점수
raw_scores = np.array([
    [70,80,90],
    [75,85,95]
])

# 1차원 배열 , 보정점수
bonus = np.array([2,3,1])

# 보정후 점수
adjusted_scores = raw_scores + bonus # 2차원 배열 + 1차원 배열


print('원래 점수: ', raw_scores)
print('보정 점수: ', bonus)
print('보정 후 점수: ', adjusted_scores)








arr = np.array([[1, 2, 3], [4, 5, 6]])
print(arr.shape)




















