# tensorflow
# 텐서플로우

# pip install tensorflow



import numpy as np
import tensorflow as tf
from util.print_util import pp,pt,up

# 텐서플로우 버전 확인
pp(f'텐서플로우 버전:{tf.__version__}')

## 텐서플로우 텐서 생성

# 정수형 상수 텐서
tensor_int = tf.constant(5, dtype=tf.int32) # 4바이트 정수 5
pp(tensor_int) #tf.Tensor(5, shape=(), dtype=int32)

# shape = (2,) : 1차원, 값 2개
tensor1 = tf.constant([5,3]) # tf.Tensor([5 3], shape=(2,), dtype=int32)
pp(tensor1)


tensor2 = tf.constant([50,20])
pp(tensor2) #tf.Tensor([50 20], shape=(2,), dtype=int32)

# 변수 텐서 생성
tensor3 = tf.Variable(5)
pp(tensor3) #<tf.Variable 'Variable:0' shape=() dtype=int32, numpy=5>

# 변수 텐서 값 변경
tensor3.assign(10)
pp(tensor3)

# 넘파이 배열을 텐서로 변환
numpy_arr = np.array([1,2,3,4])
#[1 2 3 4] int64 <class 'numpy.ndarray'>
pp(numpy_arr,numpy_arr.dtype,type(numpy_arr))

tensor = tf.convert_to_tensor(numpy_arr)
#tf.Tensor([1 2 3 4], shape=(4,), dtype=int64) <dtype: 'int64'> <class 'tensorflow.python.framework.ops.EagerTensor'>
pp(tensor,tensor.dtype,type(tensor))

# 리스트를 텐서로 변환
# 파이썬의 리스트는 모든 데이터타입을 요소로 허용, 텐서는 실수나 정수 만 가능

li = [1,3,3.14,7,10]
pp(li,type(li))

tensor2 = tf.convert_to_tensor(li)
#tf.Tensor([ 1.    3.    3.14  7.   10.  ], shape=(5,), dtype=float32) <dtype: 'float32'> <class 'tensorflow.python.framework.ops.EagerTensor'>

pp(tensor2,tensor2.dtype,type(tensor2))

# 텐서를 넘파이 배열로 변환
numpy_arr = tensor.numpy()
pp(numpy_arr,numpy_arr.dtype,type(numpy_arr))

numpy_arr2 = tensor2.numpy()
pp(numpy_arr2,numpy_arr2.dtype,type(numpy_arr2))

## 텐서플로우 함수

# 두정수형 상수 텐서 생성
tensor1 = tf.constant(5,dtype=tf.int32)
tensor2 = tf.constant(7,dtype=tf.int32)

result = tf.add(tensor1,tensor2)
pp(result)

# 텐서 행렬 곱셈
matrix1 = tf.constant([[1,2],[3,4]])
matrix2 = tf.constant([[5,6],[7,8]])

result1 = tf.matmul(matrix1,matrix2)
pp(result1,type(result1))
# tf.Tensor(
# [[19 22]
#  [43 50]], shape=(2, 2), dtype=int32) <class 'tensorflow.python.framework.ops.EagerTensor'>

# 텐서 슬라이싱
tensor3 = tf.constant([[1,2,3],[4,5,6],[7,8,9]]) # 2차원 텐서
pp(tensor3.shape)

slice_tensor = tensor3[0:2,1:3] # 0~1 행, 1~2 열
pp(slice_tensor.numpy())

# 실수 텐서 생성 후 ReLU 활성화 함수 적용
tensor4 = tf.constant([-5.14,2.51,-4.14,0.05])
relu = tf.nn.relu(tensor4)
pp(relu.numpy())

# 텐서 크기 변경
tensor5 = tf.constant([1,2,3,4,5,6]) # (6,)
pp(tensor5.shape) # 1차원
tensor_re = tf.reshape(tensor5,(2,3))
pp(tensor_re.shape) # 2차원

# 모든 요소를 채우는 텐서 생성
zeros_tf = tf.zeros((5,2)) # 0.으로 채움
pp(zeros_tf.numpy())

ones_tf = tf.ones((5,2)) # 1. 으로 채움
pp(ones_tf.numpy())

fill_tf = tf.fill((5,2),5) # 5로 채움
pp(fill_tf.numpy())

# tf.random.normal : 정규분포에서 난수 생성하는 함수
tensor = tf.random.normal(
    (3,4), # 생성할  텐서 모양
    mean=0.0, # 정규 분포의 평균, 기본값 0.0
    stddev=1.0, # 정규분포의 표준편차 기본값 1.0
    dtype=tf.float32, # 텐서의 데이터 타입, 기본값 float 32
    seed=42, # 난수생성 시드값
    name ='ts' #연산 이름을 설정하는 매개변수
)
pp(tensor)



