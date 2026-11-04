# day25_ex.py
# CNN, RNN, LSTM

import numpy as np
from tensorflow import keras

from util.print_util import pp

RANDOM_SEED = 42
keras.utils.set_random_seed(RANDOM_SEED)

# Numpy로 합성곱 연산 직접 계산
region = np.array([  # 이미지의 부분 영역
    [0, 0, 0],
    [1, 1, 1],
    [0, 0, 0],
], dtype=np.float32)

kernel = np.array([  # 커널
    [-1, -1, -1],
    [2, 2, 2],
    [-1, -1, -1]
], dtype=np.float32)

score = np.sum(region * kernel)  # 행렬 곱의 합
pp('Convolution:', score)  # 6.0


# CNN 실습용 16X16 흑백 이미지 240장 생성
def make_image_data(n_samples=240, size=16, random_state=42):
    rng = np.random.default_rng(random_state)  # 랜덤수 생성기
    X = np.zeros((n_samples, size, size), dtype=np.float32)
    y = np.zeros(n_samples, dtype=np.float32)

    for i in range(n_samples):
        if i % 2 == 0:  # 짝수: 가로선 패턴
            row = rng.integers(3, size - 3)
            X[i, row - 1: row + 2, :] = 1.0
            y[i] = 0
        else:  # 홀수: 세로선 패턴
            col = rng.integers(3, size - 3)
            X[i, :, col - 1: col + 2] = 1.0
            y[i] = 1
        X[i] += rng.normal(0, 0.08, (size, size))  # 노이즈 추가

    X = X[..., np.newaxis]  # 채널축 추가 -> (samples, height, width, 1)

    return X, y


X_cnn, y_cnn = make_image_data()

pp(X_cnn)
pp(y_cnn)
pp('X_cnn.shape', X_cnn.shape)
pp('y_cnn.shape', y_cnn.shape)

# Conv2D : 2차원 지역 패턴을 필터로 추출하는 합성곱 층
cnn = keras.Sequential([
    keras.Input(shape=(16, 16, 1)),
    keras.layers.Conv2D(
        filters=16,  # 생성할 Feature Map 개수
        kernel_size=3,  # 3X3 필터
        strides=1,  # 필터를 한번에 1픽셀씩 이동
        padding='same',  # stride=1 일때 높이와 너비 유지
        activation='relu'
    ),
    # 2X2 영역마다 최댓값을 선택해 공간 크기를 절반 수준으로 축소 (8x8)
    keras.layers.MaxPooling2D(pool_size=2),

    keras.layers.Conv2D(
        filters=32,
        kernel_size=3,  # 수정: 32 -> 3
        padding='same',
        activation='relu'
    ),
    # 공간 크기를 절반 수준으로 축소 (4x4)
    keras.layers.MaxPooling2D(pool_size=2),

    keras.layers.Flatten(),
    keras.layers.Dense(32, activation='relu'),
    keras.layers.Dense(1, activation='sigmoid'),
])

# 모델 요약 정보 출력
cnn.summary(print_fn=lambda line: pp(line))

# padding = 'valid', padding = 'same' 출력 비교
valid_layer = keras.layers.Conv2D(4, 3, padding='valid')
same_layer = keras.layers.Conv2D(4, 3, padding='same')
sample_images = X_cnn[:2]
pp('valid shape:', valid_layer(sample_images).shape)
pp('same shape:', same_layer(sample_images).shape)

# 모델 설정
cnn.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# 모델 학습
cnn_history = cnn.fit(
    X_cnn,
    y_cnn,
    epochs=3,
    batch_size=32,
    validation_split=0.2,
    verbose=0
)

# 검증 정확도, 예측 출력
pp('CNN val_accuracy:', cnn_history.history['val_accuracy'][-1])
pp('CNN predict: ', cnn.predict(X_cnn[:3], verbose=0))


# 순차 데이터 생성
def make_sequence_data(n_samples=500, timesteps=20, features=1, random_state=42):
    rng = np.random.default_rng(random_state)

    X = rng.normal(0, 1, (n_samples, timesteps, features)).astype(np.float32)
    left = X[:, : timesteps // 2, :].mean(axis=(1, 2))  # 앞 절반 평균
    right = X[:, timesteps // 2:, :].mean(axis=(1, 2))  # 수정: 뒤 절반 평균 (timesteps//2 :)
    y = (right > left).astype(np.int32)

    return X, y


X_seq, y_seq = make_sequence_data()
pp(X_seq)
pp(y_seq)
pp('X_seq.shape', X_seq.shape)
pp('y_seq.shape', y_seq.shape)

# reshape() : 2차원 시계열을 (samples, timesteps, features) 3차원으로 변환
flat_seq = X_seq[:, :, 0]
restored_seq = flat_seq.reshape(flat_seq.shape[0], flat_seq.shape[1], 1)
pp('reshape result: ', restored_seq.shape)

# SimpleRNN
rnn_last = keras.layers.SimpleRNN(
    units=8, # hidden state 차원
    activation='tanh', # 활성화 함수
    dropout=0.5, #입력 연결의 일부를 학습 중 비활성화
    return_sequences=False,# 마지막 시점 출력만 반환, False 는 기본값
    return_state=False # 별도 state를 반환하지 않음
)
rnn_all = keras.layers.SimpleRNN(
    units=8,
    return_sequences=True # 모든 시점의 출력을 반환
)

pp('RNN last output shape : ', rnn_last(X_seq[:4]).shape) # (4,8)
pp('RNN all output shape : ', rnn_all(X_seq[:4]).shape) # (4,20,8)

# return-state = True : 출력과 마지막 hidden state를 함께 반환
rnn_state_layer = keras.layers.SimpleRNN(8,return_state=True)
rnn_output,rnn_state = rnn_state_layer(X_seq[:4])
pp('RNN output shape :', rnn_output.shape) # (4,8)
pp('RNN state shape :', rnn_state.shape)# (4,8)

# SimpleRNN 기본 이진 분류 모델
rnn = keras.Sequential([
    keras.Input(shape=(20,1)),
    keras.layers.SimpleRNN(16),
    keras.layers.Dense(1,activation='sigmoid')
])

rnn.summary(print_fn=lambda line: pp(line))

rnn.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy']
)

rnn.history = rnn.fit(
    X_seq,
    y_seq,
    epochs=3,
    batch_size=32,
    validation_split=0.2,
    verbose=0
)

pp('RNN val_accuracy:', rnn.history.history['val_accuracy'][-1])

# LSTM : Gate와 Cell State를 사용해 장기 의존성 학습을 강화한 순환층
lstm_layer = keras.layers.LSTM(
    units=8, # 출려과 hidden state 차원
    activation='tanh', # Cell 출력 활성화 함수
    recurrent_activation='sigmoid',  # Gate 계산 활성화 함수
    dropout=0.2, # 입력 연결 Dropout
    recurrent_dropout= 0.0, # 순환 연결 Dropout
    return_sequences=False,
    return_state=True
)

lstm_output,hidden_state,cell_state = lstm_layer(X_seq[:4])
pp('LSTN output shape: ', lstm_output.shape) #(4, 8)
pp('LSTN hidden state shape: ', hidden_state.shape) # (4, 8)
pp('LSTN cell state shape: ', cell_state.shape) #(4, 8)

# LSTM 기본 이진 분류 모델
lstm = keras.Sequential([
    keras.Input(shape=(20,1)),
    keras.layers.LSTM(16),
    keras.layers.Dense(16,activation='relu'),
    keras.layers.Dense(1,activation='sigmoid')
])

lstm.summary(print_fn=lambda line: pp(line))

lstm.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy']
)

lstm_history = lstm.fit(
    X_seq,
    y_seq,
    epochs=3,
    batch_size=32,
    validation_split=0.2,
    verbose=0
)


pp('LSTM val_accuracy: ', lstm_history.history['val_accuracy'][-1])
pp('RNN predict: ', rnn.predict(X_seq[:3], verbose=0))
pp('LSTM predict: ', lstm.predict(X_seq[:3], verbose=0))










































