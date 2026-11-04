#day28_model
# MNIST 손글씨 숫자 인식 CNN 모델 생성 및 저장

# day28_ex2.py를 Streamlit에서 실해기 전에
# day28_model.py를 먼저 실행해서 mnist_cnn.keras 모델 파일을 생성

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from util.print_util import pp

MODEL_PATH = 'mnist_cnn.keras'  # 모델 저장 파일명

# MNIST 데이터 로드 후 train / test 분리
(x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()

# 픽셀값을 0~255에서 0~1 범위로 변환
x_train = x_train.astype('float32') / 255.0
x_test = x_test.astype('float32') / 255.0

# CNN 입력 형태에 맞게 흑백 채널 차원을 추가
# (60000,28,28) -> (60000,28,28,1)
x_train = x_train[...,tf.newaxis]
# (10000,28,28) -> (10000,28,28,1)
x_test = x_test[...,tf.newaxis]

pp('학습 데이터 shape:', x_train.shape)
pp('테스트 데이터 shape:', x_test.shape)

# CNN 모델 생성
model = keras.Sequential([
    #MNIST 사진 한장은 28 x28 크기의 흑백이미지
    keras.Input(shape=(28, 28,1)),
    layers.Conv2D(16, kernel_size=(3, 3),activation='relu'),
    layers.MaxPooling2D(pool_size=2),
    layers.Flatten(),
    layers.Dense(64, activation='relu'),
    layers.Dense(10,activation='softmax') # 10개 숫자 분류, 다중 분류는 softmax
])

# 모델 컴파일
model.compile(optimizer='adam',loss='sparse_categorical_crossentropy',metrics=['accuracy'])

# 모델 학습
history = model.fit(x_train, y_train, epochs=5, batch_size=32, validation_split=0.1)

# 모델 평가
test_loss,test_accuracy = model.evaluate(x_test, y_test,verbose=0)

pp('테스트 손실:',round(test_loss,4))
pp('테스트 정확도:',round(test_accuracy,4))

# 모델을 keras 파일로 저장
model.save(MODEL_PATH)

pp('모델저장완료: ',MODEL_PATH)












































































